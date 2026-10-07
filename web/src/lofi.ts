import { api } from "./session";
import { button, element, field, section } from "./dom";
import { SceneDraft } from "./lofi-state";
import {
  actionForm,
  choice,
  input,
  number,
  prefix,
  projectPage,
  selectEpisode,
} from "./workspace";
import type { Documents } from "./contracts";
import type {
  AssetRef,
  OverlayLayer,
  SceneryLayer,
} from "./generated/lofi_scene";

type Scene = Documents["lofi_scene"];
const key = (ref?: AssetRef | null) => (ref ? `${ref.id}@${ref.version}` : "");
function reference(value: string): AssetRef {
  const [id, version] = value.split("@");
  if (!id || !version) throw new Error("Choose an imported asset first.");
  return { id, version };
}
function decimal(control: HTMLInputElement) {
  const value = Number(control.value);
  if (!control.value || !Number.isFinite(value))
    throw new Error("Enter a number.");
  return value;
}
function numeric(value: number, minimum = 0, step = "any") {
  const control = input(String(value), "number");
  control.min = String(minimum);
  control.step = step;
  control.required = true;
  return control;
}

export function lofiPage() {
  const draft = new SceneDraft();
  const mayLeave = () =>
    !draft.dirty || window.confirm("Discard unsaved scene changes?");
  const beforeUnload = (event: BeforeUnloadEvent) => {
    if (draft.dirty) {
      event.preventDefault();
      event.returnValue = "";
    }
  };
  window.addEventListener("beforeunload", beforeUnload);
  const page = projectPage(
    async (root, project, catalog, active) => {
      const base = `${prefix(project)}/lofi`;
      const data = await api(base, "web_lofi");
      if (!active()) return;
      const savedKey = `tabi-scene-${project.project.id}`;
      let saved: Scene | undefined;
      let saving = false;
      const assets = catalog.assets;
      const byRef = (value: string) =>
        assets.find((asset) => key(asset) === value);
      const options = (kind: string, empty: string): [string, string][] => [
        ["", empty],
        ...assets
          .filter((asset) => asset.kind === kind)
          .map((asset): [string, string] => [
            key(asset),
            `${asset.id} · ${asset.version}${asset.provenance?.origin === "synthetic" ? " · SYNTHETIC" : ""}`,
          ]),
      ];
      const top = section(
        "1. Choose a reusable scene",
        "Prepare the artwork and small loops once. Reuse the saved scene for each music video.",
      );
      const selector = choice([]);
      const summary = element("p", { className: "state" });
      summary.setAttribute("role", "status");
      const preview = element("img", { className: "lofi-master" });
      preview.alt =
        "Fixed master illustration; moving layers appear in the rendered preview";
      preview.hidden = true;
      const editor = element("details", { className: "lofi-editor" });
      editor.append(
        element("summary", { text: "Scene settings and prepared assets" }),
      );
      const formHost = element("div");
      editor.append(formHost);
      const intro = element("p", {
        className: "muted",
        text: "The master holds the character and room still. A window mask reveals scrolling scenery; transparent PNG sequences supply small movements.",
      });
      top.append(field("Saved scene", selector), intro);
      const newButton = button("New scene", () => {
        if (!saving && mayLeave()) load();
      });
      const versionButton = button("Make a new scene version", () => {
        if (!saved || saving || !mayLeave()) return;
        const copy = structuredClone(saved);
        const [major, minor] = (copy.version || "1.0").split(".").map(Number);
        copy.version = `${major}.${minor + 1}`;
        copy.revision = 0;
        copy.approval = { status: "draft" };
        load(copy, true);
        draft.change();
        updateStatus();
      });
      const imports = button("Import artwork or music", () => {
        location.hash = "assets";
      });
      const tools = element("div", { className: "toolbar" });
      tools.append(newButton, versionButton, imports);
      top.append(tools, summary, preview, editor);
      if (data.archived_flow_present)
        root.append(
          element("p", {
            className: "notice",
            text: "Earlier Flow inputs and exports are preserved in this project. This workspace now creates videos from reusable artwork and loops.",
          }),
        );
      root.append(top);

      const soundtrack = section(
        "2. Make a video",
        "Choose the music and duration. The saved scene controls the motion for the whole video.",
      );
      const title = input("Tokyo lo-fi session");
      title.required = true;
      const durationMode = choice([
        ["fixed", "Set duration"],
        ["music", "Fit selected music"],
      ]);
      const duration = numeric(90, 1, "1");
      duration.max = "21600";
      const durationField = field(
        "Duration in seconds (up to 6 hours)",
        duration,
      );
      durationMode.addEventListener("change", () => {
        durationField.hidden = durationMode.value === "music";
        duration.disabled = durationMode.value === "music";
      });
      const track = choice(options("audio", "Choose a music master"));
      const ordered: string[] = [];
      const tracks = element("ol", { className: "lofi-tracks" });
      const musicTools = element("div", { className: "toolbar" });
      function showTracks() {
        tracks.replaceChildren();
        ordered.forEach((value, index) => {
          const row = element("li");
          row.append(
            element("span", { text: value }),
            button(`Remove track ${index + 1}`, () => {
              ordered.splice(index, 1);
              showTracks();
            }),
          );
          tracks.append(row);
        });
      }
      musicTools.append(
        button("Add track to the end", () => {
          if (track.value) {
            ordered.push(track.value);
            showTracks();
          }
        }),
      );
      const create = actionForm(
        "Create video and open preview",
        [
          field("Video title", title),
          field("Music master", track),
          musicTools,
          tracks,
          element("p", {
            className: "muted",
            text: "Tracks play completely in this order. Fit selected music uses their combined length. A longer fixed duration has silence after the music; no tracks makes a silent draft.",
          }),
          field("Video length", durationMode),
          durationField,
        ],
        async () => {
          if (!saved || draft.dirty || saving)
            throw new Error("Save the scene changes first.");
          const episode = await api(`${base}/videos`, "episode", {
            id: `video.${crypto.randomUUID()}`,
            title: title.value,
            scene: { id: saved.id, version: saved.version || "1.0" },
            expected_scene_revision: saved.revision || 0,
            duration_seconds:
              durationMode.value === "music" ? null : number(duration),
            music: ordered.map(reference),
          });
          if (!active()) return;
          selectEpisode(episode.id);
          location.hash = "preview";
        },
      );
      const createButton = create.querySelector<HTMLButtonElement>(
        'button[type="submit"]',
      )!;
      createButton.classList.add("primary");
      soundtrack.append(create);
      root.append(soundtrack);
      function updateStatus() {
        versionButton.disabled = !saved || saving;
        selector.disabled = saving;
        newButton.disabled = saving;
        createButton.disabled = !saved || draft.dirty || saving;
        summary.textContent = saving
          ? "Saving scene…"
          : draft.dirty
            ? "Unsaved changes. Save the scene before making a video."
            : saved
              ? `${saved.title} · version ${saved.version} is ready to reuse. Source approvals are checked separately for production export.`
              : "Choose a master illustration and save your first scene below.";
      }
      function refreshOptions() {
        const select = choice([
          ["", "New scene"],
          ...data.scenes.map((scene): [string, string] => [
            key({ id: scene.id, version: scene.version || "1.0" }),
            `${scene.title} · ${scene.version}`,
          ]),
        ]);
        selector.replaceChildren(...select.children);
        selector.value = saved
          ? key({ id: saved.id, version: saved.version || "1.0" })
          : "";
      }
      selector.addEventListener("change", () => {
        const wanted = selector.value;
        if (!mayLeave()) {
          refreshOptions();
          return;
        }
        load(
          data.scenes.find(
            (scene) =>
              key({ id: scene.id, version: scene.version || "1.0" }) === wanted,
          ),
        );
      });
      function load(scene?: Scene, asNew = false) {
        saved = asNew ? undefined : scene;
        draft.reset();
        refreshOptions();
        editor.open = !saved;
        if (saved)
          sessionStorage.setItem(
            savedKey,
            key({ id: saved.id, version: saved.version || "1.0" }),
          );
        const identity = input(scene?.id || `scene.${Date.now()}`);
        const version = input(scene?.version || "1.0");
        identity.disabled = version.disabled = !!saved;
        identity.required = version.required = true;
        const name = input(scene?.title || "Tokyo window scene");
        name.required = true;
        const master = choice(
          options("still", "Choose the fixed illustration"),
          key(scene?.master),
        );
        master.required = true;
        const currentFps = scene?.fps || { num: 30, den: 1 };
        const fpsValue = `${currentFps.num}/${currentFps.den}`;
        const rates: [string, string][] = [
          ["24/1", "24 fps"],
          ["30/1", "30 fps"],
          ["30000/1001", "29.97 fps"],
          ["60/1", "60 fps"],
        ];
        if (!rates.some(([value]) => value === fpsValue))
          rates.push([fpsValue, `${fpsValue} fps`]);
        const fps = choice(rates, fpsValue);
        const windowMask = choice(
          options("mask", "No moving window view"),
          key(scene?.window_mask),
        );
        const speed = numeric(scene?.speed ?? 24);
        speed.max = "1000";
        const panorama = section(
          "Window scenery",
          "Optional. White in the mask reveals the exterior; black preserves the illustration and overlapping character or props. Scenery strips need matching height and repeated padding for a continuous wrap.",
        );
        const sceneryRows = element("div");
        const scenery: { root: HTMLElement; read: () => SceneryLayer }[] = [];
        const addScenery = button("Add scenery layer", () => {
          sceneryRow();
          changed();
        });
        function sceneryRow(layer?: SceneryLayer) {
          const row = section(`Scenery layer ${scenery.length + 1}`);
          const asset = choice(
            options("still", "Choose a prepared scrolling strip"),
            key(layer?.asset),
          );
          asset.required = true;
          const width = numeric(layer?.repeat_width || 1920, 1, "1");
          const depth = numeric(layer?.depth ?? 1);
          depth.max = "4";
          const entry = {
            root: row,
            read: (): SceneryLayer => ({
              id: layer?.id || `scenery.${crypto.randomUUID()}`,
              asset: reference(asset.value),
              repeat_width: number(width),
              depth: decimal(depth),
            }),
          };
          scenery.push(entry);
          row.append(
            field("Scenery strip", asset),
            field("Repeat width in pixels (excluding padding)", width),
            field("Relative speed (distant layers move slower)", depth),
            button("Remove scenery layer", () => {
              scenery.splice(scenery.indexOf(entry), 1);
              row.remove();
              addScenery.disabled = false;
              changed();
            }),
          );
          sceneryRows.append(row);
          addScenery.disabled = scenery.length >= 3;
        }
        for (const layer of scene?.scenery || []) sceneryRow(layer);
        panorama.append(
          field("Window mask", windowMask),
          field("Travel speed in pixels per second", speed),
          sceneryRows,
          addScenery,
        );
        const loops = section(
          "Small animation loops",
          "Optional aligned transparent PNG sequences: a blink, rain or a reflection. Use the same canvas and frame rate as the master scene. Each animation repeats on its own clock; the master shows during gaps.",
        );
        const overlayRows = element("div");
        const overlays: {
          root: HTMLElement;
          read: () => {
            layer: OverlayLayer;
            seconds: { repeat_seconds: number; delay_seconds: number };
          };
        }[] = [];
        const addOverlay = button("Add animation loop", () => {
          overlayRow();
          changed();
        });
        function overlayRow(layer?: OverlayLayer) {
          const row = section(`Animation loop ${overlays.length + 1}`);
          const asset = choice(
            options("sequence", "Choose a transparent PNG sequence"),
            key(layer?.asset),
          );
          asset.required = true;
          const repeat = numeric(
            layer
              ? (layer.timing.repeat_frames * currentFps.den) / currentFps.num
              : 4,
            0.001,
          );
          const delay = numeric(
            layer
              ? ((layer.timing.first_frame || 0) * currentFps.den) /
                  currentFps.num
              : 0,
          );
          const start = numeric(layer?.timing.source.start_frame || 0, 0, "1");
          const end = numeric(layer?.timing.source.end_frame || 1, 1, "1");
          asset.addEventListener("change", () => {
            start.value = "0";
            end.value = String(byRef(asset.value)?.probe.frame_count || 1);
          });
          const mask = choice(
            options("mask", "Use the sequence transparency"),
            key(layer?.mask),
          );
          const opacity = numeric(layer?.opacity ?? 1);
          opacity.max = "1";
          const advanced = element("details");
          advanced.append(
            element("summary", { text: "Source frames, mask and opacity" }),
            field("First source frame", start),
            field("End source frame (exclusive)", end),
            field("Overlay mask", mask),
            field("Opacity", opacity),
          );
          const entry = {
            root: row,
            read: () => {
              const id = layer?.id || `overlay.${crypto.randomUUID()}`;
              return {
                layer: {
                  id,
                  asset: reference(asset.value),
                  mask: mask.value ? reference(mask.value) : null,
                  opacity: decimal(opacity),
                  timing: {
                    source: {
                      start_frame: number(start),
                      end_frame: number(end),
                    },
                    repeat_frames: number(end) - number(start),
                    first_frame: 0,
                  },
                },
                seconds: {
                  repeat_seconds: decimal(repeat),
                  delay_seconds: decimal(delay),
                },
              };
            },
          };
          overlays.push(entry);
          row.append(
            field("Animation sequence", asset),
            field("Repeat every (seconds)", repeat),
            field("First play after (seconds)", delay),
            advanced,
            button("Remove animation loop", () => {
              overlays.splice(overlays.indexOf(entry), 1);
              row.remove();
              addOverlay.disabled = false;
              changed();
            }),
          );
          overlayRows.append(row);
          addOverlay.disabled = overlays.length >= 8;
        }
        for (const layer of scene?.overlays || []) overlayRow(layer);
        loops.append(overlayRows, addOverlay);
        const metadata = element("details");
        metadata.append(
          element("summary", { text: "Scene identity" }),
          field("Scene ID", identity),
          field("Scene version", version),
        );
        const form = actionForm(
          "Save reusable scene",
          [
            field("Scene name", name),
            field("Fixed master illustration", master),
            field("Scene frame rate", fps),
            panorama,
            loops,
            metadata,
          ],
          async () => {
            const [num, den] = fps.value.split("/").map(Number);
            const prepared = overlays.map((row) => row.read());
            const ticket = draft.ticket();
            const body = {
              scene: {
                schema_version: "1.0",
                document_type: "lofi_scene",
                id: identity.value,
                version: version.value,
                title: name.value,
                master: reference(master.value),
                fps: { num, den },
                window_mask: windowMask.value
                  ? reference(windowMask.value)
                  : null,
                speed: decimal(speed),
                scenery: scenery.map((row) => row.read()),
                overlays: prepared.map((entry) => entry.layer),
                notes: scene?.notes || "",
                revision: saved?.revision || 0,
                approval: saved?.approval || { status: "draft" },
              },
              expected_revision: saved?.revision ?? null,
              timing_seconds: Object.fromEntries(
                prepared.map((entry) => [entry.layer.id, entry.seconds]),
              ),
            };
            saving = true;
            updateStatus();
            const controls = Array.from(
              form.querySelectorAll<
                HTMLInputElement | HTMLButtonElement | HTMLSelectElement
              >("input,button,select"),
            );
            const disabled = controls.map((control) => control.disabled);
            for (const control of controls) control.disabled = true;
            try {
              const result = await api(`${base}/scenes`, "lofi_scene", body);
              if (!active()) return;
              data.scenes = [
                ...data.scenes.filter(
                  (item) =>
                    item.id !== result.id || item.version !== result.version,
                ),
                result,
              ];
              saved = result;
              refreshOptions();
              sessionStorage.setItem(
                savedKey,
                key({ id: result.id, version: result.version || "1.0" }),
              );
              identity.disabled = version.disabled = true;
              if (draft.accept(ticket)) {
                editor.open = false;
                return "Scene saved. Choose your music and video length below.";
              }
              return "Saved the submitted scene. Your newer changes still need saving.";
            } finally {
              controls.forEach((control, index) => {
                control.disabled = disabled[index];
              });
              identity.disabled = version.disabled = !!saved;
              saving = false;
              updateStatus();
            }
          },
        );
        function changed() {
          draft.change();
          updateStatus();
        }
        form.addEventListener("input", changed);
        form.addEventListener("change", changed);
        function showMaster() {
          const asset = byRef(master.value);
          preview.hidden = !asset;
          if (asset)
            preview.src = `/api/v1${prefix(project)}/assets/${asset.id}/${asset.version}/media`;
          else preview.removeAttribute("src");
        }
        master.addEventListener("change", showMaster);
        showMaster();
        if (saved?.approval?.status && saved.approval.status !== "draft") {
          for (const control of form.querySelectorAll<
            HTMLInputElement | HTMLButtonElement | HTMLSelectElement
          >("input,button,select"))
            control.disabled = true;
          form.prepend(
            element("p", {
              className: "notice",
              text: "This version is under review or approved. Make a new scene version to edit it.",
            }),
          );
        }
        formHost.replaceChildren(form);
        updateStatus();
      }
      const remembered = sessionStorage.getItem(savedKey);
      load(
        data.scenes.find(
          (scene) =>
            key({ id: scene.id, version: scene.version || "1.0" }) ===
            remembered,
        ) || data.scenes[0],
      );
    },
    { episodeSelector: false },
  );
  return {
    ...page,
    canLeave: mayLeave,
    dispose: () => {
      window.removeEventListener("beforeunload", beforeUnload);
      page.dispose();
    },
  };
}
