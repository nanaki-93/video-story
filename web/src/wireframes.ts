// Navigation metadata. Every listed page is backed by the local worker.
export const layouts = {
  lofi: {
    title: "Create video",
    subtitle: "Reusable artwork. Gentle loops. Your music.",
  },
  projects: {
    title: "Projects",
    subtitle: "Your local videos and working folders.",
  },
  setup: {
    title: "Scene setup",
    subtitle: "Advanced tools for existing layered projects.",
  },
  assets: {
    title: "Asset library",
    subtitle: "Local sources and immutable versions.",
  },
  inspector: {
    title: "Asset details",
    subtitle: "Media, provenance and approvals.",
  },
  story: { title: "Story", subtitle: "Existing layered episode structure." },
  timeline: {
    title: "Timeline",
    subtitle: "Existing authored frame schedule.",
  },
  notebook: { title: "Notebook", subtitle: "Existing episode notes." },
  preview: {
    title: "Preview",
    subtitle:
      "Render a short preview to check motion, loop boundaries and sound.",
  },
  audio: {
    title: "Music",
    subtitle: "Arrange tracks, fades and loudness for the current video.",
  },
  renders: {
    title: "Export",
    subtitle: "Render and download a saved video locally.",
  },
  release: {
    title: "YouTube delivery",
    subtitle: "Review a verified export before manual upload.",
  },
  settings: {
    title: "Settings",
    subtitle: "Local worker, storage and preferences.",
  },
} as const;
export type PageId = keyof typeof layouts;
