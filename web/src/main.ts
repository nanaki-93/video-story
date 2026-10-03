import "./style.css";
import { element } from "./dom";
import { layouts, wireframe } from "./wireframes";
import type { PageId } from "./wireframes";
import { playbackSpike } from "./playback";
import { connect, sessionPanel } from "./session";
import { projectsPage, setupPage, restoreRecents } from "./workspace";
import { assetsPage, inspectorPage } from "./assets";
import { editorPage } from "./editor";
import { previewPage } from "./preview";
import { audioPage } from "./audio";

const app = document.querySelector<HTMLDivElement>("#app")!;
const shell = element("div", { className: "shell" });
const sidebar = element("aside", { className: "sidebar" });
sidebar.append(
  element("div", { className: "wordmark", text: "tabi / story studio" }),
  element("p", { className: "eyebrow", text: "LOCAL WORKSPACE" }),
);
const navigation = element("nav");
navigation.setAttribute("aria-label", "Workspace design pages");
const links = new Map<PageId, HTMLAnchorElement>();
for (const [id, layout] of Object.entries(layouts)) {
  const link = element("a", { text: layout.title });
  link.href = `#${id}`;
  navigation.append(link);
  links.set(id as PageId, link);
}
sidebar.append(
  navigation,
  element("p", {
    className: "sidebar-note",
    text: "Local files stay on this Mac.",
  }),
);
const main = element("main", { id: "workspace" });
main.tabIndex = -1;
shell.append(sidebar, main);
app.append(shell);
document
  .querySelector<HTMLAnchorElement>(".skip")
  ?.addEventListener("click", (event) => {
    event.preventDefault();
    main.focus();
  });
let cleanup: (() => void) | undefined;
let mode: "spike" | "connected" | undefined;
function navigate() {
  if (!mode) return;
  cleanup?.();
  const requested = location.hash.slice(1);
  const page: PageId = Object.hasOwn(layouts, requested)
    ? (requested as PageId)
    : mode === "spike"
      ? "preview"
      : "projects";
  for (const [id, link] of links) {
    if (id === page) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  const layout = layouts[page];
  const header = element("header", { className: "page-header" });
  const text = element("div");
  text.append(
    element("p", {
      className: "eyebrow",
      text: "TABI STORY STUDIO / LOCAL WORKSPACE",
    }),
    element("h1", { text: layout.title }),
    element("p", { className: "muted", text: layout.subtitle }),
  );
  header.append(
    text,
    element("span", {
      className: "badge",
      text:
        mode === "connected" &&
        [
          "settings",
          "projects",
          "assets",
          "inspector",
          "setup",
          "story",
          "timeline",
          "notebook",
          "preview",
          "audio",
        ].includes(page)
          ? "Connected worker"
          : page === "preview" && mode === "spike"
            ? "Working playback spike"
            : "Wireframe",
    }),
  );
  main.replaceChildren(header);
  const pages = {
    audio: audioPage,
    preview: previewPage,
    projects: projectsPage,
    setup: setupPage,
    assets: assetsPage,
    inspector: inspectorPage,
    story: () => editorPage("story"),
    timeline: () => editorPage("timeline"),
    notebook: () => editorPage("notebook"),
  };
  if (mode === "connected" && Object.hasOwn(pages, page)) {
    const panel = pages[page as keyof typeof pages]();
    cleanup = panel.dispose;
    main.append(panel.root);
  } else if (mode === "connected" && page === "settings") {
    const panel = sessionPanel();
    cleanup = panel.dispose;
    main.append(panel.root);
  } else if (page === "preview" && mode === "spike") {
    const preview = playbackSpike();
    cleanup = preview.dispose;
    main.append(preview.root);
  } else {
    cleanup = undefined;
    main.append(wireframe(page));
  }
  document.title = `${layout.title} · Tabi Story Studio`;
}
let connectionAttempt = 0;
function connectWorkspace() {
  const attempt = ++connectionAttempt;
  cleanup?.();
  mode = undefined;
  main.replaceChildren(
    element("p", {
      text: "Connecting to the local worker…",
      className: "notice",
    }),
  );
  void connect()
    .then(async (value) => {
      if (attempt !== connectionAttempt) return;
      if (value === "connected") await restoreRecents();
      if (attempt !== connectionAttempt) return;
      mode = value;
      navigate();
    })
    .catch((error: unknown) => {
      if (attempt !== connectionAttempt) return;
      main.replaceChildren(
        element("h1", { text: "Workspace unavailable" }),
        element("p", { text: String(error), className: "notice" }),
      );
    });
}
window.addEventListener("hashchange", () => {
  if (location.hash.startsWith("#bootstrap=")) connectWorkspace();
  else navigate();
});
connectWorkspace();
