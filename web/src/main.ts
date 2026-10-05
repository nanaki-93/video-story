import "./style.css";
import { element } from "./dom";
import { layouts } from "./wireframes";
import type { PageId } from "./wireframes";
import { api, connect } from "./session";
import { projectsPage, setupPage, restoreRecents } from "./workspace";
import { assetsPage, inspectorPage } from "./assets";
import { editorPage } from "./editor";
import { previewPage } from "./preview";
import { audioPage } from "./audio";
import { rendersPage, settingsPage } from "./production";
import { releasePage } from "./release";
import { flowPage } from "./flow";

const app = document.querySelector<HTMLDivElement>("#app")!;
const shell = element("div", { className: "shell" });
const sidebar = element("aside", { className: "sidebar" });
sidebar.append(
  element("div", { className: "wordmark", text: "tabi / story studio" }),
);
const navigation = element("nav");
navigation.setAttribute("aria-label", "Workspace");
const advanced = element("details", { className: "advanced-nav" });
advanced.append(element("summary", { text: "Advanced" }));
const links = new Map<PageId, HTMLAnchorElement>();
for (const [id, layout] of Object.entries(layouts)) {
  const link = element("a", { text: layout.title });
  link.href = `#${id}`;
  links.set(id as PageId, link);
  if (["flow", "projects"].includes(id)) navigation.append(link);
  else advanced.append(link);
}
navigation.append(advanced);
sidebar.append(
  navigation,
  element("p", {
    className: "sidebar-note",
    text: "Files and music stay on this Mac.\nGeneration happens in Google Flow.",
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
const pages = {
  flow: flowPage,
  projects: projectsPage,
  setup: setupPage,
  assets: assetsPage,
  inspector: inspectorPage,
  story: () => editorPage("story"),
  timeline: () => editorPage("timeline"),
  notebook: () => editorPage("notebook"),
  preview: previewPage,
  audio: audioPage,
  renders: rendersPage,
  release: releasePage,
  settings: settingsPage,
};
let cleanup: (() => void) | undefined;
let connected = false;
function navigate() {
  if (!connected) return;
  cleanup?.();
  const requested = location.hash.slice(1);
  const page: PageId = Object.hasOwn(layouts, requested)
    ? (requested as PageId)
    : "flow";
  for (const [id, link] of links) {
    if (id === page) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  if (!["flow", "projects"].includes(page)) advanced.open = true;
  const layout = layouts[page];
  const header = element("header", { className: "page-header" });
  const text = element("div");
  text.append(
    element("p", { className: "eyebrow", text: "TABI STORY STUDIO" }),
    element("h1", { text: layout.title }),
    element("p", { className: "muted", text: layout.subtitle }),
  );
  header.append(text);
  const panel = pages[page]();
  cleanup = panel.dispose;
  main.replaceChildren(header, panel.root);
  document.title = `${layout.title} · Tabi Story Studio`;
}
let attempt = 0;
function connectWorkspace() {
  const current = ++attempt;
  cleanup?.();
  connected = false;
  main.replaceChildren(
    element("p", {
      text: "Opening your local workspace…",
      className: "notice",
    }),
  );
  void connect()
    .then(async () => {
      if (current !== attempt) return;
      await restoreRecents();
      const settings = await api("/settings", "web_settings");
      document.documentElement.dataset.theme = settings.preferences.theme;
      if (current !== attempt) return;
      connected = true;
      navigate();
    })
    .catch((error) => {
      if (current !== attempt) return;
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
