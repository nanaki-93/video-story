import { api } from "./session";
import type { Documents } from "./contracts";
import { button, element, field, section } from "./dom";
import { EditHistory } from "./edit-history";
import {
  actionForm,
  choice,
  episodeId,
  input,
  jsonEditor,
  number,
  prefix,
  projectPage,
  selectFrame,
  selectedFrame,
} from "./workspace";

type Episode = Documents["episode"];
const editors = new Map<string, EditHistory<Episode>>();
const unsaved = new Set<HTMLInputElement>();
window.addEventListener("beforeunload", (event) => {
  if (
    unsaved.size ||
    [...editors.values()].some((editor) => editor.pending > 0)
  ) {
    event.preventDefault();
    event.returnValue = "";
  }
});
let zoom = 1;

export function editorPage(mode: "story" | "timeline" | "notebook") {
  let removeKeys = () => {};
  let flushPending = () => {};
  const page = projectPage(async (root, project, catalog, active) => {
    if (!episodeId()) {
      root.append(
        section("No episode", "Use New episode to create a draft first."),
      );
      return;
    }
    const base = `${prefix(project)}/episodes/${episodeId()}`,
      key = `${project.project.id}/${episodeId()}`;
    await editors.get(key)?.tail;
    let view = await api(`${base}/editor`, "web_editor");
    if (!active()) return;
    let history = editors.get(key);
    if (!history || history.current.revision !== view.episode.revision) {
      history = new EditHistory(view.episode, (expected_revision, command) =>
        api(`${base}/edit`, "episode", { expected_revision, command }),
      );
      editors.set(key, history);
    }
    const editor = history;
    const ownedControls = new Set<HTMLInputElement>();
    const status = element("p", {
      className: "notice",
      text: `Saved revision ${editor.current.revision || 0}. Changes are written atomically when applied.`,
    });
    status.setAttribute("role", "status");
    const content = element("div", { className: "workspace-content" });
    async function accepted(result: Promise<Episode>, redraw = true) {
      status.textContent = "Saving and checking timeline…";
      try {
        await result;
        view = await api(`${base}/editor`, "web_editor");
        if (!active()) return;
        status.textContent = `Saved revision ${editor.current.revision}. Last-known-good backups are on disk.`;
        const picker = root.querySelector<HTMLSelectElement>(
          "select[data-episode-selector]",
        );
        const option = Array.from(picker?.options || []).find(
          (item) => item.value === editor.current.id,
        );
        if (option)
          option.textContent = `${editor.current.title} · revision ${editor.current.revision}`;
        undo.disabled = !editor.past.length;
        redo.disabled = !editor.future.length;
        if (redraw) draw();
      } catch (error) {
        if (active())
          status.textContent = `${String(error)}. Your last saved document was preserved. Reload after a revision conflict.`;
        throw error;
      }
    }
    const run = (command: unknown, redraw = true) =>
      accepted(editor.apply(command), redraw);
    const flushers = new Set<() => void>();
    flushPending = () => {
      for (const flush of flushers) flush();
    };
    function autosave(control: HTMLInputElement, command: () => unknown) {
      ownedControls.add(control);
      let timer: ReturnType<typeof setTimeout> | undefined;
      let generation = 0;
      const flush = () => {
        if (!timer) return;
        clearTimeout(timer);
        timer = undefined;
        const attempt = generation;
        void run(command(), false)
          .then(() => {
            if (attempt === generation) unsaved.delete(control);
          })
          .catch(() => {});
      };
      flushers.add(flush);
      control.addEventListener("input", () => {
        generation++;
        unsaved.add(control);
        status.textContent = "Unsaved change — autosave pending…";
        clearTimeout(timer);
        timer = setTimeout(flush, 450);
      });
      control.addEventListener("change", flush);
      control.addEventListener("blur", flush);
    }
    const toolbar = element("div", { className: "toolbar" });
    const undo = button("Undo", () => {
      void accepted(editor.undo()).catch(() => {});
    });
    const redo = button("Redo", () => {
      void accepted(editor.redo()).catch(() => {});
    });
    undo.disabled = !editor.past.length;
    redo.disabled = !editor.future.length;
    toolbar.append(
      undo,
      redo,
      button("Reload saved document", () => {
        for (const control of ownedControls) unsaved.delete(control);
        editors.delete(key);
        window.dispatchEvent(new Event("hashchange"));
      }),
      button("Preview episode", () => {
        location.hash = "preview";
      }),
    );
    root.append(toolbar, status, content);
    const keydown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement;
      if (
        target.closest("input, textarea, select, [contenteditable=true]") ||
        !(event.metaKey || event.ctrlKey) ||
        event.key.toLowerCase() !== "z"
      )
        return;
      event.preventDefault();
      void accepted(event.shiftKey ? editor.redo() : editor.undo()).catch(
        () => {},
      );
    };
    window.addEventListener("keydown", keydown);
    removeKeys = () => window.removeEventListener("keydown", keydown);
    function draw() {
      const episode = editor.current;
      content.replaceChildren();
      if (!view.validation.valid || view.validation.issues.length) {
        const issues = section("Timeline checks");
        for (const issue of view.validation.issues)
          issues.append(
            element("p", {
              className: "state",
              text: `${issue.severity}: ${issue.message} ${issue.suggested_fix || ""}`,
            }),
          );
        content.append(issues);
      }
      const title = input(episode.title);
      autosave(title, () => ({ kind: "title", title: title.value }));
      content.append(field("Episode title — autosaves on change", title));
      if (mode !== "notebook") {
        const timeline = section(
          "Timeline",
          "Frame positions come from Python. Audio labels retain their exact sample intervals. Drag an action to a frame or use its numeric inspector; source duration is preserved.",
        );
        const cursor = input(
          String(Math.min(selectedFrame, episode.duration_frames - 1)),
          "range",
        );
        cursor.min = "0";
        cursor.max = String(episode.duration_frames - 1);
        cursor.step = "1";
        // Native ranges clamp values to 100 until their maximum is assigned.
        cursor.value = String(
          Math.min(selectedFrame, episode.duration_frames - 1),
        );
        const cursorText = element("p", {
          text: `Selected frame ${cursor.value}`,
          className: "mono",
        });
        cursor.addEventListener("input", () => {
          selectFrame(number(cursor));
          cursorText.textContent = `Selected frame ${cursor.value}`;
        });
        const zoomer = choice(
          [
            ["1", "Fit"],
            ["2", "2×"],
            ["4", "4×"],
            ["8", "8×"],
          ],
          String(zoom),
        );
        const scroll = element("div", { className: "timeline-scroll" });
        const lanes = element("div", { className: "timeline-lanes" });
        const applyZoom = () => {
          zoom = Number(zoomer.value);
          lanes.style.width = `${zoom * 100}%`;
        };
        zoomer.addEventListener("change", applyZoom);
        applyZoom();
        for (const lane of view.lanes) {
          const label = element("p", { text: lane.title, className: "muted" });
          const row = element("div", { className: "timeline-lane" });
          row.setAttribute("aria-label", lane.title);
          row.addEventListener("dragover", (e) => {
            e.preventDefault();
          });
          row.addEventListener("drop", (event) => {
            event.preventDefault();
            const id = event.dataTransfer?.getData("text/tabi-action");
            if (!id) return;
            const rect = row.getBoundingClientRect();
            const frame = Math.max(
              0,
              Math.min(
                episode.duration_frames - 1,
                Math.round(
                  ((event.clientX - rect.left) / rect.width) *
                    episode.duration_frames,
                ),
              ),
            );
            void run({ kind: "move_action", id, start_frame: frame }).catch(
              () => {},
            );
          });
          for (const item of lane.items) {
            const block = button(item.label, () => {
              selectFrame(
                Math.min(item.start_frame, episode.duration_frames - 1),
              );
              cursor.value = String(selectedFrame);
              cursorText.textContent = `Selected frame ${selectedFrame}`;
            });
            block.className = "timeline-block";
            block.title = `${item.label} · frames ${item.start_frame}–${item.end_frame}`;
            block.style.left = `${(100 * item.start_frame) / episode.duration_frames}%`;
            block.style.width = `${Math.max(0.6, (100 * (item.end_frame - item.start_frame)) / episode.duration_frames)}%`;
            if (item.action_id) {
              block.draggable = true;
              block.addEventListener("dragstart", (event) => {
                event.dataTransfer?.setData(
                  "text/tabi-action",
                  item.action_id!,
                );
              });
            }
            row.append(block);
          }
          lanes.append(label, row);
        }
        scroll.append(lanes);
        timeline.append(
          field("Timeline zoom", zoomer),
          field("Selected global frame", cursor),
          cursorText,
          scroll,
        );
        content.append(timeline);
        const cards = section(
          "Scene cards",
          "Durations, entry state and transitions use the same core contracts as exports. Music and actions are never silently shifted by a scene edit.",
        );
        for (const scene of episode.scenes) {
          const card = section(
            scene.id,
            `Frames ${scene.start_frame}–${scene.end_frame} · ${scene.template.id} ${scene.template.version}`,
          );
          const purpose = input(scene.purpose || "");
          autosave(purpose, () => {
            const current = editor.current.scenes.find(
              (s) => s.id === scene.id,
            )!;
            return {
              kind: "scene",
              scene: { ...current, purpose: purpose.value || null },
            };
          });
          card.append(field("Scene purpose — autosaves on change", purpose));
          const details = element("details");
          details.append(
            element("summary", {
              text: "Frame boundaries, transition and state inspector",
            }),
          );
          const data = jsonEditor(scene);
          details.append(
            actionForm(
              "Apply scene changes",
              [field("Scene JSON", data)],
              async () => {
                await run({ kind: "scene", scene: JSON.parse(data.value) });
              },
            ),
          );
          if (scene.start_frame) {
            const cut = input(String(scene.start_frame), "number");
            details.append(
              actionForm(
                "Move cut boundary",
                [field("New cut frame (actions stay in place)", cut)],
                async () => {
                  await run({
                    kind: "move_cut",
                    scene_id: scene.id,
                    frame: number(cut),
                  });
                },
              ),
            );
          }
          card.append(details);
          cards.append(card);
        }
        const append = element("details");
        append.append(element("summary", { text: "Append a scene" }));
        const id = input(`scene-${episode.scenes.length + 1}`),
          duration = input("300", "number"),
          purpose = input("");
        const template = choice(
          catalog.templates.map((t) => [
            `${t.id}@${t.version}`,
            `${t.id} ${t.version}`,
          ]),
        );
        const actions = catalog.packs.flatMap((p) =>
          p.actions
            .filter((a) => a.channel === "body")
            .map((a) => ({ pack: p, action: a })),
        );
        const action = choice([
          ["", "No character action (environment-only scene)"],
          ...actions.map((v): [string, string] => [
            `${v.pack.id}@${v.pack.version}/${v.action.id}`,
            `${v.pack.id} / ${v.action.id}`,
          ]),
        ]);
        append.append(
          actionForm(
            "Append scene and save",
            [
              field("Scene ID", id),
              field("Template", template),
              field("Added frames", duration),
              field("Purpose", purpose),
              field("Body action", action),
            ],
            async () => {
              const [tid, version] = template.value.split("@");
              const selected = actions.find(
                (v) =>
                  `${v.pack.id}@${v.pack.version}/${v.action.id}` ===
                  action.value,
              );
              await run({
                kind: "append_scene",
                id: id.value,
                template: { id: tid, version },
                duration_frames: number(duration),
                purpose: purpose.value,
                pack: selected
                  ? { id: selected.pack.id, version: selected.pack.version }
                  : null,
                action_id: selected?.action.id ?? null,
              });
            },
          ),
        );
        cards.append(append);
        content.append(cards);
        const actionBox = section(
          "Actions",
          "Only registered action packs are selectable. Python checks poses, channels, frame rate, transitions, props and whole loops.",
        );
        for (const action of episode.actions || []) {
          const start = input(String(action.start_frame), "number");
          actionBox.append(
            actionForm(
              `Move ${action.id}`,
              [
                field(
                  `${action.action_id} — start frame (${action.end_frame - action.start_frame} source-window frames)`,
                  start,
                ),
              ],
              async () => {
                await run({
                  kind: "move_action",
                  id: action.id,
                  start_frame: number(start),
                });
              },
            ),
          );
        }
        if (catalog.packs.length) {
          const prepared = catalog.packs.flatMap((p) =>
            p.actions.map((a) => ({ pack: p, action: a })),
          );
          const source = choice(
            prepared.map((v, i) => [
              String(i),
              `${v.pack.id} / ${v.action.id} · ${v.action.channel} · ${v.action.kind}`,
            ]),
          );
          const scene = choice(episode.scenes.map((s) => [s.id, s.id]));
          const id = input(`action-${Date.now()}`),
            start = input(String(selectedFrame), "number"),
            end = input(String(episode.duration_frames), "number");
          const repeat = choice([
            ["once", "Once"],
            ["loop_to_fill", "Whole loops to fill"],
          ]);
          actionBox.append(
            actionForm(
              "Add or replace action",
              [
                field("Request ID", id),
                field("Prepared action", source),
                field("Scene", scene),
                field("Start frame", start),
                field("End frame", end),
                field("Repeat", repeat),
              ],
              async () => {
                const { pack, action } = prepared[Number(source.value)];
                await run({
                  kind: "put_action",
                  action: {
                    id: id.value,
                    scene_id: scene.value,
                    pack: { id: pack.id, version: pack.version },
                    action_id: action.id,
                    version: action.version,
                    channel: action.channel,
                    repeat: repeat.value,
                    start_frame: number(start),
                    end_frame: number(end),
                  },
                });
              },
            ),
          );
        } else
          actionBox.append(
            element("p", {
              text: "Import an authored action pack on Assets to add character actions.",
            }),
          );
        content.append(actionBox);
        const curves = section(
          "Keyframe inspector",
          "Only parameters declared by the scene template are offered. Values and interpolation are validated in Python.",
        );
        for (const scene of episode.scenes) {
          const template = catalog.templates.find(
            (t) =>
              t.id === scene.template.id &&
              t.version === scene.template.version,
          );
          for (const [target, limits] of Object.entries(
            template?.parameter_limits || {},
          )) {
            const existing = [
              ...(episode.curves || []),
              ...(scene.curves || []),
            ].find((c) => c.scope === scene.id && c.target === target);
            const keys = jsonEditor(
              existing?.keys || [
                { frame: scene.start_frame, value: limits.minimum },
                { frame: scene.end_frame, value: limits.minimum },
              ],
            );
            const interpolation = choice(
              [
                ["linear", "Linear"],
                ["constant", "Constant"],
              ],
              existing?.interpolation || "linear",
            );
            const unit = choice(
              [
                ["fraction", "Fraction (0–1)"],
                ["design_px_per_second", "Design pixels / second"],
                ["design_px", "Design pixels"],
                ["degrees", "Degrees"],
                ["db", "dB"],
              ],
              existing?.unit ||
                (target === "travel_speed"
                  ? "design_px_per_second"
                  : "fraction"),
            );
            curves.append(
              actionForm(
                `Save ${scene.id}/${target}`,
                [
                  field("Keyframes JSON (integer global frames)", keys),
                  field("Interpolation", interpolation),
                  field("Unit", unit),
                ],
                async () => {
                  await run({
                    kind: "put_curve",
                    curve: {
                      scope: scene.id,
                      target,
                      unit: unit.value,
                      interpolation: interpolation.value,
                      outside: "clamp",
                      limits,
                      keys: JSON.parse(keys.value),
                    },
                  });
                },
              ),
            );
          }
        }
        if (curves.children.length === 2)
          curves.append(
            element("p", { text: "This template has no animated parameters." }),
          );
        content.append(curves);
        const beats = section(
          "Story beats",
          "Map authored intent to scene intervals and existing music placement IDs.",
        );
        const values = jsonEditor(episode.beats || []);
        beats.append(
          actionForm(
            "Save story beats",
            [field("Beat list JSON", values)],
            async () => {
              await run({ kind: "beats", beats: JSON.parse(values.value) });
            },
          ),
        );
        content.append(beats);
      }
      const notebook = section(
        "Continuity notebook",
        "Record carried objects, their intended locations, links to previous episodes, and deliberate discontinuities.",
      );
      const summary = input(episode.continuity?.summary || ""),
        previous = input(episode.continuity?.previous_episode_id || ""),
        objects = input((episode.continuity?.objects || []).join(", "));
      const notes = jsonEditor(episode.continuity?.notes || []),
        objectNotes = jsonEditor(episode.continuity?.object_notes || {});
      notebook.append(
        actionForm(
          "Save continuity notes",
          [
            field("Episode summary", summary),
            field("Previous episode ID", previous),
            field("Object IDs (comma separated)", objects),
            field("Notes JSON", notes),
            field("Object notes JSON", objectNotes),
          ],
          async () => {
            await run({
              kind: "continuity",
              continuity: {
                summary: summary.value || null,
                previous_episode_id: previous.value || null,
                objects: objects.value
                  .split(",")
                  .map((v) => v.trim())
                  .filter(Boolean),
                notes: JSON.parse(notes.value),
                object_notes: JSON.parse(objectNotes.value),
              },
            });
          },
        ),
      );
      content.append(notebook);
      const advanced = element("details");
      advanced.append(
        element("summary", {
          text: "Apply an atomic edit across several scenes or lanes",
        }),
      );
      const data = jsonEditor(episode);
      advanced.append(
        actionForm(
          "Validate and save episode",
          [field("Complete episode JSON", data)],
          async () => {
            await run({ kind: "replace", episode: JSON.parse(data.value) });
          },
        ),
      );
      content.append(advanced);
    }
    draw();
  });
  return {
    ...page,
    dispose: () => {
      flushPending();
      removeKeys();
      page.dispose();
    },
  };
}
