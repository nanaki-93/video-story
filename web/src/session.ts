import { document as checked } from "./contracts";
import type { Documents } from "./generated/documents";
import { element, section } from "./dom";

let current: Documents["web_session"] | undefined;

export async function connect() {
  const fragment = location.hash;
  let response: Response;
  if (fragment.startsWith("#bootstrap=")) {
    const secret = fragment.slice("#bootstrap=".length);
    // Remove the one-time ticket before any network request or UI rendering.
    history.replaceState(null, "", `${location.pathname}#lofi`);
    response = await fetch("/api/v1/bootstrap", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ protocol: "1", secret }),
    });
  } else
    response = await fetch("/api/v1/session", {
      credentials: "same-origin",
      cache: "no-store",
    });
  if (!response.ok)
    throw new Error(
      "Session unavailable or expired. Enter ‘open’ in the local launcher to reopen this workspace.",
    );
  const payload: unknown = await response.json();
  if (
    typeof payload === "object" &&
    payload !== null &&
    "protocol" in payload &&
    payload.protocol !== "1"
  )
    throw new Error(
      "Worker protocol is incompatible. Restart with the matching installed app.",
    );
  current = checked("web_session", payload);
  return "connected" as const;
}

export async function api<K extends keyof Documents>(
  path: string,
  kind: K,
  body?: unknown,
  method = body === undefined ? "GET" : "POST",
  signal?: AbortSignal,
): Promise<Documents[K]> {
  return checked(kind, await request(path, body, method, signal));
}

export async function request(
  path: string,
  body?: unknown,
  method = body === undefined ? "GET" : "POST",
  signal?: AbortSignal,
): Promise<unknown> {
  if (!current) throw new Error("No authenticated local session");
  const response = await fetch(`/api/v1${path}`, {
    method,
    credentials: "same-origin",
    cache: "no-store",
    headers:
      body === undefined
        ? {}
        : {
            "Content-Type":
              body instanceof Blob
                ? "application/octet-stream"
                : "application/json",
            "X-Tabi-CSRF": current.csrf,
          },
    body:
      body === undefined
        ? undefined
        : body instanceof Blob
          ? body
          : JSON.stringify(body),
    signal,
  });
  if (response.status === 401)
    throw new Error(
      "Session expired. Reopen from the local launcher; saved work and jobs remain on disk.",
    );
  if (!response.ok) {
    const detail = await response
      .json()
      .catch(() => ({ detail: "Local service unavailable" }));
    if (Array.isArray(detail.issues))
      throw new Error(
        detail.issues
          .map(
            (issue: { message: string; suggested_fix?: string }) =>
              `${issue.message} ${issue.suggested_fix || ""}`,
          )
          .join("\n"),
      );
    if (Array.isArray(detail.detail))
      throw new Error(
        detail.detail
          .map(
            (issue: { location: unknown[]; message: string }) =>
              `${issue.location.join(".")}: ${issue.message}`,
          )
          .join("\n"),
      );
    throw new Error(
      typeof detail.detail === "string"
        ? detail.detail
        : JSON.stringify(detail),
    );
  }
  return response.json();
}

export function sessionPanel(
  openProject: (project: Documents["web_project"]) => void,
) {
  const root = section(
    "Local worker",
    "This browser uses the same Python services as the CLI.",
  );
  root.append(
    element("p", {
      className: "notice",
      text: `Connected · protocol ${current?.protocol} · worker ${current?.pid}`,
    }),
  );
  root.append(
    element("p", {
      className: "muted",
      text: "Refreshing or closing a tab leaves render jobs running. Enter ‘open’ in the launcher to reopen; ‘stop’ waits for the current job before exiting.",
    }),
  );
  let disposed = false;
  void Promise.all([
    api("/roots", "web_roots"),
    api("/projects", "web_projects"),
  ])
    .then(async ([roots, projects]) => {
      if (disposed) return;
      root.append(element("h2", { text: "Registered folders" }));
      for (const folder of roots.roots)
        root.append(
          element("p", {
            className: "mono",
            text: `${folder.id} · ${folder.path}`,
          }),
        );
      root.append(element("h2", { text: "Open projects and verified media" }));
      if (!projects.projects.length)
        root.append(
          element("p", { text: "No projects are open in this worker." }),
        );
      for (const project of projects.projects) {
        root.append(element("h3", { text: project.project.title }));
        const list = await api(`/projects/${project.handle}/jobs`, "web_jobs");
        if (disposed) return;
        for (const job of list.jobs) {
          const row = element("p", {
            text: `${job.id} · ${job.state} · ${job.completed_frames}/${job.duration_frames} verified frames `,
          });
          if (job.state === "verified") {
            const link = element("a", { text: "Review verified exports" });
            link.href = "#renders";
            link.addEventListener("click", () => openProject(project));
            row.append(link);
          }
          root.append(row);
        }
      }
    })
    .catch((error: unknown) => {
      if (!disposed)
        root.append(element("p", { className: "notice", text: String(error) }));
    });
  return {
    root,
    dispose: () => {
      disposed = true;
    },
  };
}
