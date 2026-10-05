// Navigation metadata. Every listed page is backed by the local worker.
export const layouts = {
  flow: {
    title: "Create video",
    subtitle: "A saved workflow from TABI reference to finished video.",
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
    subtitle: "Existing compiled episode playback.",
  },
  audio: {
    title: "Audio",
    subtitle: "Local soundtrack tools for existing episodes.",
  },
  renders: { title: "Renders", subtitle: "Existing layered render jobs." },
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
