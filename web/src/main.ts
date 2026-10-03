import "./style.css";
import { element } from "./dom";
import { layouts, wireframe } from "./wireframes";
import type { PageId } from "./wireframes";
import { playbackSpike } from "./playback";

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
    text: "Design study · T25\nLocal files stay on this Mac.",
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
function navigate() {
  cleanup?.();
  const requested = location.hash.slice(1);
  const page: PageId = Object.hasOwn(layouts, requested)
    ? (requested as PageId)
    : "preview";
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
      text: "TABI STORY STUDIO / INTERFACE STUDY",
    }),
    element("h1", { text: layout.title }),
    element("p", { className: "muted", text: layout.subtitle }),
  );
  header.append(
    text,
    element("span", {
      className: "badge",
      text: page === "preview" ? "Working playback spike" : "Wireframe",
    }),
  );
  main.replaceChildren(header);
  if (page === "preview") {
    const preview = playbackSpike();
    cleanup = preview.dispose;
    main.append(preview.root);
  } else {
    cleanup = undefined;
    main.append(wireframe(page));
  }
  document.title = `${layout.title} · Tabi Story Studio`;
}
window.addEventListener("hashchange", navigate);
navigate();
