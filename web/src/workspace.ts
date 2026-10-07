import { api } from "./session";
import { button, element, field, section } from "./dom";
import type { Documents } from "./contracts";

export type Panel = {
  root: HTMLElement;
  dispose: () => void;
  canLeave?: () => boolean;
};
type Recent = { root_id: string; path: string; id: string; title: string };
export type Project = Documents["web_project"];
export type Catalog = Documents["web_catalog"];
let selected: Project | undefined;
export async function restoreRecents() {
  selected = undefined;
  const result = await api("/recents", "web_recents");
  // Keep unavailable drives visible for relinking. Opening still checks the project ID.
  const items = result.projects;
  localStorage.setItem("tabi-recents", JSON.stringify(items));
  if (!items.some((r) => r.id === localStorage.getItem("tabi-current"))) {
    if (items.length) localStorage.setItem("tabi-current", items[0].id);
    else localStorage.removeItem("tabi-current");
  }
}
let chosenEpisode = sessionStorage.getItem("tabi-episode") || "";
export let selectedFrame = Number(sessionStorage.getItem("tabi-frame") || 0);
export function selectFrame(frame: number) {
  selectedFrame = frame;
  sessionStorage.setItem("tabi-frame", String(frame));
}
export function episodeId() {
  return chosenEpisode;
}
export function selectEpisode(identity: string) {
  chosenEpisode = identity;
  sessionStorage.setItem("tabi-episode", identity);
}
export function prefix(project: Project) {
  return `/projects/${project.handle}`;
}
export function input(value = "", type = "text") {
  const result = element("input");
  result.type = type;
  result.value = value;
  return result;
}
export function choice(options: [string, string][], selected?: string) {
  const result = element("select");
  for (const [value, text] of options) {
    const option = element("option", { text });
    option.value = value;
    result.append(option);
  }
  if (selected !== undefined) result.value = selected;
  return result;
}
export function number(control: HTMLInputElement) {
  const value = Number(control.value);
  if (!control.value || !Number.isSafeInteger(value))
    throw new Error("Enter a whole number");
  return value;
}
export function jsonEditor(value: unknown) {
  const result = element("textarea");
  result.rows = 8;
  result.value = JSON.stringify(value, null, 2);
  result.spellcheck = false;
  return result;
}
export function actionForm(
  label: string,
  controls: HTMLElement[],
  execute: () => Promise<string | void>,
) {
  const form = element("form");
  const status = element("p", { className: "state" });
  status.setAttribute("role", "status");
  const submit = button(label, () => {});
  submit.type = "submit";
  form.append(...controls, submit, status);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (submit.disabled) return;
    submit.disabled = true;
    status.textContent = "Working…";
    void execute()
      .then((message) => {
        status.textContent = message || "Saved locally.";
      })
      .catch((error: unknown) => {
        status.textContent = String(error);
        status.className = "state error";
      })
      .finally(() => {
        submit.disabled = false;
      });
  });
  return form;
}
function recent(): Recent[] {
  try {
    const value: unknown = JSON.parse(
      localStorage.getItem("tabi-recents") || "[]",
    );
    return Array.isArray(value)
      ? value
          .filter(
            (v): v is Recent =>
              v &&
              [v.root_id, v.path, v.id, v.title].every(
                (s: unknown) => typeof s === "string",
              ),
          )
          .slice(0, 30)
      : [];
  } catch {
    return [];
  }
}
export function remember(project: Project) {
  selected = project;
  const next = {
    root_id: project.root_id,
    path: project.path,
    id: project.project.id,
    title: project.project.title,
  };
  localStorage.setItem(
    "tabi-recents",
    JSON.stringify(
      [next, ...recent().filter((r) => r.id !== next.id)].slice(0, 30),
    ),
  );
  localStorage.setItem("tabi-current", next.id);
}
export async function currentProject(): Promise<Project> {
  const previous = recent().find(
    (r) => r.id === localStorage.getItem("tabi-current"),
  );
  if (!previous)
    throw new Error("Choose or create a project on the Projects page.");
  const project = await api("/projects/open", "web_project", {
    root_id: previous.root_id,
    path: previous.path,
    expected_project_id: previous.id,
  });
  remember(project);
  return project;
}
export function projectPage(
  build: (
    root: HTMLElement,
    project: Project,
    catalog: Catalog,
    active: () => boolean,
  ) => Promise<void> | void,
  options: { episodeSelector?: boolean } = {},
): Panel {
  const root = element("div", { className: "workspace-content" });
  let active = true;
  root.append(element("p", { className: "notice", text: "Loading project…" }));
  void currentProject()
    .then(async (project) => {
      const catalog = await api(`${prefix(project)}/catalog`, "web_catalog");
      if (!active) return;
      root.replaceChildren(
        element("p", {
          className: "muted",
          text: `${project.project.title} · ${project.root_id}/${project.path}`,
        }),
      );
      if (!catalog.episodes.some((e) => e.id === chosenEpisode))
        selectEpisode(catalog.episodes[0]?.id || "");
      if (catalog.episodes.length && options.episodeSelector !== false) {
        const select = choice(
          catalog.episodes.map((e) => [
            e.id,
            `${e.title} · revision ${e.revision}`,
          ]),
          chosenEpisode,
        );
        select.dataset.episodeSelector = "true";
        select.addEventListener("change", () => {
          selectEpisode(select.value);
          refreshPage();
        });
        root.append(field("Current video", select));
      }
      await build(root, project, catalog, () => active);
    })
    .catch((error: unknown) => {
      if (active)
        root.replaceChildren(
          element("p", { className: "notice", text: String(error) }),
          button("Choose or create a project", () => {
            location.hash = "projects";
          }),
        );
    });
  return {
    root,
    dispose: () => {
      active = false;
    },
  };
}
export function refreshPage() {
  window.dispatchEvent(new Event("hashchange"));
}
export async function folderChooser(
  onChoose: (root: string, path: string) => void,
) {
  const box = section(
    "Local folder",
    "Only folders registered by the launcher are available.",
  );
  const roots = await api("/roots", "web_roots");
  const select = choice(roots.roots.map((r) => [r.id, `${r.id} · ${r.path}`]));
  const listing = element("div");
  let path = "",
    offset = 0;
  const location = element("p", { className: "mono" });
  async function browse() {
    location.textContent = `${select.value}/${path}`;
    onChoose(select.value, path);
    listing.replaceChildren(element("p", { text: "Reading folder…" }));
    try {
      const data = await api(
        `/files?${new URLSearchParams({ root_id: select.value, path, offset: String(offset) })}`,
        "web_directory",
      );
      listing.replaceChildren();
      if (path)
        listing.append(
          button("Parent folder", () => {
            path = path.split("/").slice(0, -1).join("/");
            offset = 0;
            void browse();
          }),
        );
      for (const entry of data.entries) {
        if (entry.kind === "directory")
          listing.append(
            button(`Open folder: ${entry.name}`, () => {
              path = entry.path;
              offset = 0;
              void browse();
            }),
          );
      }
      if (!data.entries.length)
        listing.append(element("p", { text: "This folder is empty." }));
      if (data.next_offset !== null)
        listing.append(
          button("More folders", () => {
            offset = data.next_offset!;
            void browse();
          }),
        );
    } catch (error) {
      listing.replaceChildren(
        element("p", { className: "notice", text: String(error) }),
      );
    }
  }
  listing.className = "folder-list";
  select.addEventListener("change", () => {
    path = "";
    offset = 0;
    void browse();
  });
  box.append(field("Registered folder", select), location, listing);
  await browse();
  return box;
}
export function projectsPage(): Panel {
  const root = element("div", { className: "workspace-content" });
  let active = true;
  const list = section(
    "Recent projects",
    "Recent locations are disposable browser preferences; all project content is stored on disk.",
  );
  const status = element("p", { className: "notice" });
  status.setAttribute("role", "status");
  let relink: Recent | undefined;
  for (const item of recent()) {
    const row = element("div", { className: "toolbar" });
    row.append(
      element("span", { text: `${item.title} · ${item.root_id}/${item.path}` }),
      button("Reopen", () => {
        status.textContent = "Opening…";
        void api("/projects/open", "web_project", {
          root_id: item.root_id,
          path: item.path,
          expected_project_id: item.id,
        })
          .then((p) => {
            remember(p);
            if (active) location.hash = "lofi";
          })
          .catch((e: unknown) => {
            status.textContent = `Project unavailable. Reconnect the drive or choose Relink. ${String(e)}`;
          });
      }),
      button("Relink", () => {
        relink = item;
        status.textContent = `Choose the moved folder for ${item.title}, then open it. Its project ID must match.`;
      }),
    );
    list.append(row);
  }
  if (!recent().length)
    list.append(
      element("p", { text: "No recent projects. Create a project below." }),
    );
  if (selected) {
    list.append(
      element("p", { text: `Current: ${selected.project.title}` }),
      button("Create video", () => {
        location.hash = "lofi";
      }),
      button("Advanced scene setup", () => {
        location.hash = "setup";
      }),
    );
    void api(`${prefix(selected)}/catalog`, "web_catalog")
      .then((catalog) => {
        if (!active) return;
        for (const episode of catalog.episodes)
          list.append(
            button(`Preview ${episode.title}`, () => {
              selectEpisode(episode.id);
              location.hash = "preview";
            }),
          );
      })
      .catch((e: unknown) => {
        status.textContent = String(e);
      });
  }
  root.append(list, status);
  let rootId = "",
    path = "";
  void folderChooser((id, relative) => {
    rootId = id;
    path = relative;
  })
    .then((chooser) => {
      if (!active) return;
      const name = input("My lo-fi videos");
      const title = input("My lo-fi videos");
      chooser.append(
        actionForm("Open selected project", [], async () => {
          const project = await api("/projects/open", "web_project", {
            root_id: rootId,
            path,
            expected_project_id: relink?.id ?? null,
          });
          remember(project);
          relink = undefined;
          if (active) location.hash = "lofi";
        }),
        actionForm(
          "Create project in this folder",
          [field("New folder name", name), field("Project title", title)],
          async () => {
            const project = await api("/projects/create", "web_project", {
              root_id: rootId,
              parent: path,
              folder: name.value,
              title: title.value,
            });
            remember(project);
            if (active) location.hash = "lofi";
          },
        ),
      );
      root.append(chooser);
    })
    .catch((e: unknown) => {
      status.textContent = String(e);
    });
  return {
    root,
    dispose: () => {
      active = false;
    },
  };
}

export function setupPage(): Panel {
  return projectPage((root, project, catalog) => {
    if (!catalog.templates.length) {
      root.append(
        section(
          "Add a starting scene",
          "Import a scene template in Assets, or create a still scene from an imported image in its inspector.",
        ),
      );
      return;
    }
    const box = section(
      "Create an episode",
      "Inputs remain draft. The worker checks duration in integer frames and places music in integer samples without trimming it.",
    );
    const id = input(`episode-${Date.now()}`),
      title = input("Untitled story"),
      duration = input("300", "number"),
      seed = input("0", "number");
    const format = choice([
      ["story", "Story"],
      ["session", "Session"],
      ["track", "Track"],
    ]);
    const template = choice(
      catalog.templates.map((t) => [
        `${t.id}@${t.version}`,
        `${t.id} ${t.version} · ${t.approval?.status || "draft"}`,
      ]),
    );
    const fps = choice([
      ["30/1", "30 fps"],
      ["24/1", "24 fps"],
      ["30000/1001", "30000/1001 fps"],
      ["60/1", "60 fps"],
    ]);
    const canvas = choice([
      ["1920x1080", "1920 × 1080"],
      ["3840x2160", "3840 × 2160"],
      ["960x540", "960 × 540 preview"],
    ]);
    const pose = input("idle");
    const music = element("div");
    const ordered: string[] = [];
    const audio = catalog.assets.filter((a) => a.kind === "audio");
    const choose = choice([
      ["", "Choose a music master"],
      ...audio.map((a): [string, string] => [
        `${a.id}@${a.version}`,
        `${a.id} ${a.version} · ${a.provenance?.commercial_use || "pending"}`,
      ]),
    ]);
    const names = element("p");
    music.append(
      field("Music order", choose),
      button("Append track", () => {
        if (choose.value) ordered.push(choose.value);
        names.textContent = ordered.join(" → ");
      }),
      button("Clear music order", () => {
        ordered.length = 0;
        names.textContent = "";
      }),
      names,
    );
    box.append(
      actionForm(
        "Create draft episode",
        [
          field("Episode ID", id),
          field("Title", title),
          field("Format", format),
          field("Scene template", template),
          field("Initial body pose", pose),
          field("Frame rate", fps),
          field("Canvas", canvas),
          field("Duration in frames", duration),
          field("Random seed", seed),
          music,
        ],
        async () => {
          const [num, den] = fps.value.split("/").map(Number),
            [width, height] = canvas.value.split("x").map(Number);
          const ref = (v: string) => {
            const [id, version] = v.split("@");
            return { id, version };
          };
          const episode = await api(`${prefix(project)}/episodes`, "episode", {
            id: id.value,
            title: title.value,
            format: format.value,
            template: ref(template.value),
            fps: { num, den },
            canvas: { width, height },
            duration_frames: number(duration),
            seed: number(seed),
            body_pose: pose.value,
            music: ordered.map(ref),
          });
          selectEpisode(episode.id);
          return `Saved ${episode.title}. Open Story to author its scenes. Approval and rights remain unchanged.`;
        },
      ),
    );
    root.append(box);
  });
}
