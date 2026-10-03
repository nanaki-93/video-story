import { element, section } from "./dom";

export const layouts = {
  projects: {
    title: "Projects",
    subtitle: "Your local stories, sources and working folders.",
    panels: [
      [
        "Open a workspace",
        "Recent projects · Folder chooser · Create project",
        "Project name",
        "Storage location",
        "Last opened / unavailable drive",
      ],
      [
        "Project details",
        "Episode list · Backup · Relink",
        "Draft episode / most recent preview",
        "Local storage and missing files",
        "Recover from backup",
      ],
    ],
    states: [
      "No projects yet. Choose a local folder to begin.",
      "Reading project…",
      "The selected drive is unavailable. Relink when connected.",
    ],
  },
  setup: {
    title: "New episode",
    subtitle: "Choose an authored format and compatible starting scene.",
    panels: [
      [
        "Episode",
        "Title and format",
        "Title",
        "Story / Session / Track",
        "Frame rate and output canvas",
      ],
      [
        "Scene and music",
        "Choose from the local registry",
        "Compatible scene template",
        "Ordered music masters",
        "Duration conflicts and draft input review",
      ],
    ],
    states: [
      "Import a scene template to create an episode.",
      "Checking asset compatibility…",
      "Music exceeds the proposed duration. Adjust the story or placement explicitly.",
    ],
  },
  assets: {
    title: "Assets",
    subtitle: "Versioned media, provenance and approval in one library.",
    panels: [
      [
        "Library",
        "Filter by kind, pack and status",
        "Still / mask / sequence / audio",
        "Pack cards with version and approval badge",
        "Import selected files or a registered folder",
      ],
      [
        "Selected asset",
        "Technical health and provenance",
        "Source and prepared proxy",
        "Missing or changed source",
        "Rights pending / reviewed hash",
      ],
    ],
    states: [
      "No assets imported.",
      "Copying and probing selected media…",
      "One source changed. Import a new version before approving it.",
    ],
  },
  inspector: {
    title: "Asset inspector",
    subtitle: "Inspect a prepared version before using or reviewing it.",
    panels: [
      [
        "Visual inspection",
        "Source / proxy · Checkerboard / light / dark",
        "Preview with alpha and mask overlay",
        "Anchor and pivot coordinates",
        "Action poses and frame range",
      ],
      [
        "Version and provenance",
        "Review applies to this content hash",
        "Camera and template compatibility",
        "Creator, rights evidence and generation notes",
        "Normalize a new version / record explicit review",
      ],
    ],
    states: [
      "Select an asset version.",
      "Normalizing a new version…",
      "This camera is incompatible with the selected template.",
    ],
  },
  story: {
    title: "Story",
    subtitle:
      "Shape the episode through scenes, musical moments and small actions.",
    panels: [
      [
        "Storyboard",
        "Ordered scene cards",
        "Scene purpose · Start / end frame",
        "Transition and continuity state",
        "Add a musical story beat",
      ],
      [
        "Scene inspector",
        "Template and supported effects",
        "Slot assignments and action selection",
        "Speed, light, rain and reflection curves",
        "Objects carried into the next scene",
      ],
    ],
    states: [
      "Choose an episode to begin.",
      "Saving draft…",
      "A pose transition is missing. Choose a compatible action or an explicit reset.",
    ],
  },
  timeline: {
    title: "Timeline",
    subtitle: "Frame-based edits over the same Python episode document.",
    panels: [
      [
        "Lanes",
        "Zoom · Selected frame · Undo / redo",
        "Scenes ━━━━━━━ ━━━━━━━",
        "Music ━━━━━━━━━━━━━━━",
        "Tabi · Weather · Light · Speed",
      ],
      [
        "Selection",
        "Numeric frame inspector",
        "Action start / end and return pose",
        "Curve keys and interpolation",
        "Validation report with suggested correction",
      ],
    ],
    states: [
      "No selection. Choose a scene or action.",
      "Compiling the changed draft…",
      "Moving this action would overlap another body action.",
    ],
  },
  audio: {
    title: "Audio",
    subtitle: "Use finished masters; author placement and ambience separately.",
    panels: [
      [
        "Music and ambience",
        "Import WAV · Order placements",
        "Waveform proxy and exact sample bounds",
        "Trim, gain and fades",
        "Ambience loop and crossfade",
      ],
      [
        "Mix and release facts",
        "Analyze continuous mix",
        "Effective duration, silence, peak and loudness",
        "Artist, title, credits and known IDs",
        "Source master hash and rights status",
      ],
    ],
    states: [
      "Import a finished WAV master.",
      "Analyzing audio…",
      "Mix clipping detected. Lower gain before final AAC encoding.",
    ],
  },
  preview: {
    title: "Preview",
    subtitle: "Watch a rendered proxy and inspect exact frames from Python.",
    panels: [],
    states: [
      "No rendered proxy yet.",
      "Rendering the selected range…",
      "This proxy belongs to an earlier snapshot. It remains playable as stale.",
    ],
  },
  renders: {
    title: "Renders",
    subtitle: "Verified progress survives browser closure and worker restart.",
    panels: [
      [
        "New export",
        "Freeze the reviewed draft",
        "Proxy / 1080p / 4K and explicit encoder",
        "Destination and disk estimate",
        "Snapshot hash and production-input checks",
      ],
      [
        "Queue",
        "Completed frames and measured approximate ETA",
        "Queued → rendering → verified",
        "Pause after chunk · Cancel owned work · Resume",
        "Failure diagnostics and interrupted-job recovery",
      ],
    ],
    states: [
      "The render queue is empty.",
      "Rendering the current chunk…",
      "Worker interrupted. Verified chunks are retained for recovery.",
    ],
  },
  release: {
    title: "Release",
    subtitle: "Prepare a factual bundle for a deliberate manual release.",
    panels: [
      [
        "Public metadata",
        "Title · Description · Chapters",
        "Factual track list and artist credits",
        "Approved thumbnail",
        "Disclosure notes for human review",
      ],
      [
        "Readiness",
        "Export and review hashes",
        "Creative, rights and disclosure checks",
        "Public bundle / private evidence",
        "Actual URLs and manual claim notes",
      ],
    ],
    states: [
      "Select a verified export.",
      "Verifying the selected export and bundle…",
      "Rights are pending. A draft bundle is available; upload readiness is blocked.",
    ],
  },
  settings: {
    title: "Settings",
    subtitle: "Local tools, storage and worker health.",
    panels: [
      [
        "Tools and worker",
        "Health check and exact versions",
        "FFmpeg / ffprobe paths",
        "Session and protocol status",
        "Optional local generation endpoint",
      ],
      [
        "Storage and preferences",
        "Launcher-registered roots",
        "Project and media folders",
        "Cache inspection, budget and explicit pruning",
        "Theme and export defaults",
      ],
    ],
    states: [
      "Run a toolchain check to inspect this installation.",
      "Probing installed tools…",
      "FFmpeg is unavailable. Select a supported local installation.",
    ],
  },
  notebook: {
    title: "Continuity notebook",
    subtitle: "Keep recurring objects and deliberate story changes visible.",
    panels: [
      [
        "Episode notes",
        "Authored summary and previous episode link",
        "Why this episode exists",
        "Musical and visual contribution",
        "Deliberate discontinuities",
      ],
      [
        "Carried objects",
        "Manual object notes",
        "Object identity and current role",
        "Scene links and state changes",
        "Unresolved continuity notes",
      ],
    ],
    states: [
      "No continuity notes yet.",
      "Saving notebook…",
      "An object note refers to an undeclared object. Add it or correct the reference.",
    ],
  },
} as const;

export type PageId = keyof typeof layouts;

export function wireframe(page: PageId) {
  const layout = layouts[page];
  const root = element("div", { className: "wireframe" });
  root.append(
    element("p", {
      className: "notice",
      text: "Wireframe only · Layout and state copy for review. These are not connected production controls.",
    }),
  );
  const grid = element("div", { className: "panel-grid" });
  for (const [title, hint, ...rows] of layout.panels) {
    const panel = section(title, hint);
    for (const row of rows)
      panel.append(element("div", { className: "wire-row", text: row }));
    grid.append(panel);
  }
  root.append(grid);
  const states = section(
    "State review",
    "The finished page will report actual service state.",
  );
  for (const [index, state] of layout.states.entries())
    states.append(
      element("p", { className: `state state-${index}`, text: state }),
    );
  root.append(states);
  return root;
}
