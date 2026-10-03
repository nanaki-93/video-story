import { api } from "./session";
import { document as checked } from "./contracts";
import type { Documents } from "./contracts";
import { button, element, field, section } from "./dom";
import {
  actionForm,
  choice,
  episodeId,
  input,
  jsonEditor,
  number,
  prefix,
  projectPage,
} from "./workspace";
import { EditHistory } from "./edit-history";

export function audioPage() {
  let cleanup = () => {};
  const panel = projectPage(async (root, project, catalog, active) => {
    if (!catalog.episodes.length)
      throw new Error(
        "Create an episode first; WAV import is available in Assets.",
      );
    const base = prefix(project),
      path = `${base}/episodes/${episodeId()}`;
    let data = await api(`${path}/audio`, "web_audio");
    if (!active()) return;
    let tracks = structuredClone(data.episode.tracks || []),
      dirty = false;
    let planned: Documents["audio_edit_plan"] | undefined;
    let generation = 0;
    const history = new EditHistory(data.episode, async (revision, command) => {
      const operation = command as {
        kind: string;
        episode?: Documents["episode"];
        tracks?: Documents["track_placement"][];
      };
      if (operation.kind === "replace")
        return api(`${path}/edit`, "episode", {
          expected_revision: revision,
          command: operation,
        });
      return api(`${path}/audio`, "episode", {
        expected_revision: revision,
        tracks: operation.tracks,
        resequence_music: false,
      });
    });
    const state = element("p", {
      className: "notice",
      text: `Saved revision ${history.current.revision}`,
    });
    state.setAttribute("role", "status");
    const report = element("div"),
      rows = element("div"),
      proposal = element("pre", { className: "state" });
    const auditionStatus = element("p", {
      className: "notice",
      text: "No edited mix audition yet.",
    });
    const player = element("audio");
    player.controls = true;
    player.preload = "metadata";
    player.setAttribute("aria-label", "Edited soundtrack audition");
    player.addEventListener("error", () => {
      if (player.getAttribute("src"))
        auditionStatus.textContent =
          "Audio unavailable; check the worker session or render the audition again.";
    });
    const contiguous = input("", "checkbox");
    const save = button("Apply reviewed audio edit", () => {
      void commit();
    });
    save.disabled = true;
    const undo = button("Undo audio edit", () => {
        void restore(false);
      }),
      redo = button("Redo audio edit", () => {
        void restore(true);
      });
    const beforeUnload = (event: BeforeUnloadEvent) => {
      if (dirty || history.pending) event.preventDefault();
    };
    window.addEventListener("beforeunload", beforeUnload);
    function changed() {
      ++generation;
      dirty = true;
      planned = undefined;
      save.disabled = true;
      state.textContent =
        "Unsaved audio changes. Review their timing before applying.";
      proposal.textContent = "";
      if (player.getAttribute("src"))
        auditionStatus.textContent =
          "STALE audition — audio edits are pending. Apply them, then render again.";
    }
    contiguous.addEventListener("change", changed);
    function issues() {
      report.replaceChildren(
        element("p", {
          text: `Saved episode: ${data.timeline.duration_samples} samples at 48,000 Hz. Sources are unchanged.`,
        }),
      );
      for (const issue of data.timeline.issues)
        report.append(
          element("p", {
            className: "notice",
            text: `${issue.severity}: ${issue.message} ${issue.suggested_fix}`,
          }),
        );
      undo.disabled = !history.past.length;
      redo.disabled = !history.future.length;
    }
    async function refresh() {
      data = await api(`${path}/audio`, "web_audio");
      if (!active()) return;
      tracks = structuredClone(history.current.tracks || []);
      dirty = false;
      planned = undefined;
      save.disabled = true;
      state.textContent = `Saved revision ${history.current.revision}. Regenerate the audition to hear it.`;
      const option = root.querySelector<HTMLOptionElement>(
        "select[data-episode-selector] option:checked",
      );
      if (option)
        option.textContent = `${history.current.title} · revision ${history.current.revision}`;
      if (player.getAttribute("src"))
        auditionStatus.textContent =
          "STALE audition — saved audio has changed.";
      draw();
      issues();
    }
    async function restore(forward: boolean) {
      root.inert = true;
      try {
        if (forward) await history.redo();
        else await history.undo();
        await refresh();
      } catch (error) {
        state.textContent = String(error);
      } finally {
        root.inert = false;
      }
    }
    async function commit() {
      if (!planned?.can_apply) return;
      save.disabled = true;
      root.inert = true;
      try {
        await history.apply({ kind: "audio", tracks: planned.tracks });
        await refresh();
      } catch (error) {
        state.textContent = `${String(error)}. Reload if another tab changed this episode.`;
      } finally {
        root.inert = false;
      }
    }
    async function plan() {
      const requested = generation;
      planned = await api(`${path}/audio/plan`, "audio_edit_plan", {
        expected_revision: history.current.revision,
        tracks,
        resequence_music: contiguous.checked,
      });
      if (!active()) return;
      if (requested !== generation) {
        planned = undefined;
        return "Audio changed during analysis. Review timing again.";
      }
      proposal.textContent = `Proposed audio end: ${planned.effective_end_sample} samples\nStory end: ${planned.episode_duration_samples} samples\n${planned.tracks.map((t) => `${t.id}: starts ${t.start_sample}; source [${t.trim_start_sample}, ${t.trim_end_sample})`).join("\n")}\n${planned.issues.join("\n")}`;
      save.disabled = !planned.can_apply;
      return planned.can_apply
        ? "Timing checked. Visual actions and story beats retain their authored timing."
        : "This edit conflicts with the story or source. Resolve the listed issues before applying.";
    }
    function draw() {
      rows.replaceChildren();
      tracks.forEach((track, index) => {
        const row = section(
          `${index + 1}. ${track.id} · ${track.asset.id}`,
          `${track.role || "music"} · ${track.asset.version}`,
        );
        const numeric: [keyof Documents["track_placement"], string][] = [
          ["start_sample", "Episode start sample"],
          ["trim_start_sample", "Source trim start (48 kHz)"],
          ["trim_end_sample", "Source trim end (exclusive)"],
          ["gain_db", "Gain dB"],
          ["fade_in_samples", "Fade in samples"],
          ["fade_out_samples", "Fade out samples"],
          ["loop_duration_samples", "Ambience loop duration (blank = no loop)"],
          ["loop_crossfade_samples", "Ambience loop crossfade samples"],
        ];
        const controls = element("div", { className: "audio-fields" });
        for (const [key, label] of numeric) {
          const value = track[key];
          const control = input(
            value == null
              ? key === "loop_duration_samples"
                ? ""
                : "0"
              : String(value),
            "number",
          );
          control.step = key === "gain_db" ? "0.1" : "1";
          control.addEventListener("input", () => {
            (track as unknown as Record<string, unknown>)[key] =
              control.value === "" && key === "loop_duration_samples"
                ? null
                : Number(control.value);
            changed();
          });
          controls.append(field(`${track.id} · ${label}`, control));
        }
        const role = choice(
          [
            ["music", "Music"],
            ["ambience", "Ambience"],
          ],
          track.role || "music",
        );
        role.addEventListener("change", () => {
          track.role = role.value as "music" | "ambience";
          changed();
        });
        const release = choice(
          [
            ["", "No release metadata"],
            ...catalog.releases.map(
              (r) => [r.id, r.release_title] as [string, string],
            ),
          ],
          track.release_id || "",
        );
        release.addEventListener("change", () => {
          track.release_id = release.value || null;
          changed();
        });
        const wave = element("div");
        row.append(
          controls,
          field(`${track.id} · Role`, role),
          field(`${track.id} · Music release`, release),
          button("Move track earlier", () => {
            if (index === 0) return;
            [tracks[index - 1], tracks[index]] = [
              tracks[index],
              tracks[index - 1],
            ];
            contiguous.checked = true;
            changed();
            draw();
          }),
          button("Move track later", () => {
            if (index === tracks.length - 1) return;
            [tracks[index], tracks[index + 1]] = [
              tracks[index + 1],
              tracks[index],
            ];
            contiguous.checked = true;
            changed();
            draw();
          }),
          button("Remove placement", () => {
            tracks.splice(index, 1);
            changed();
            draw();
          }),
          actionForm("Show source waveform", [], async () => {
            const result = await api(
              `${base}/assets/${track.asset.id}/${track.asset.version}/waveform`,
              "waveform_report",
            );
            if (!active()) return;
            const canvas = element("canvas");
            canvas.width = 1024;
            canvas.height = 160;
            canvas.style.width = "100%";
            canvas.setAttribute("role", "img");
            canvas.setAttribute(
              "aria-label",
              `${track.asset.id}: ${result.duration_samples} source samples, ${result.sample_rate} Hz, ${result.channels} channels`,
            );
            const ctx = canvas.getContext("2d")!;
            ctx.fillStyle = "#171820";
            ctx.fillRect(0, 0, 1024, 160);
            ctx.strokeStyle = "#B3A1D4";
            result.bins.forEach((bin, i) => {
              const x = (i * 1024) / result.bins.length;
              ctx.beginPath();
              ctx.moveTo(x, 80 - 72 * Math.max(...bin.maximum));
              ctx.lineTo(x, 80 - 72 * Math.min(...bin.minimum));
              ctx.stroke();
            });
            wave.replaceChildren(
              canvas,
              element("p", {
                text: `${result.synthetic ? "Synthetic · " : ""}Whole source waveform at ${result.sample_rate} Hz; trims use the prepared 48 kHz stream. Leading silence: ${result.leading_silence_samples}; trailing: ${result.trailing_silence_samples} samples.`,
              }),
            );
            return "Waveform derived from the hashed master.";
          }),
          wave,
        );
        rows.append(row);
      });
    }
    const assets = choice(
      data.sources.map((s) => [
        `${s.asset.id}@${s.asset.version}`,
        `${s.asset.id} · ${s.asset.version} · ${s.prepared_samples} prepared samples`,
      ]),
    );
    const id = input(`track-${tracks.length + 1}`),
      role = choice([
        ["music", "Music"],
        ["ambience", "Ambience"],
      ]);
    const add = actionForm(
      "Add audio placement",
      [
        field("Prepared master", assets),
        field("Placement ID", id),
        field("New placement role", role),
      ],
      async () => {
        const source = data.sources.find(
          (s) => `${s.asset.id}@${s.asset.version}` === assets.value,
        );
        if (!source) throw new Error("Import a WAV master in Assets first.");
        tracks.push({
          id: id.value,
          asset: { id: source.asset.id, version: source.asset.version },
          start_sample: 0,
          trim_start_sample: 0,
          trim_end_sample: source.prepared_samples,
          role: role.value as "music" | "ambience",
        });
        changed();
        draw();
        return "Placement added to the unsaved draft. Review its timing below.";
      },
    );
    const listen = section(
      "Edited soundtrack audition",
      "Renders the saved sample timeline through the same Python mixer used by final video. Maximum range: 120 seconds. A new WAV is created; distribution masters are untouched.",
    );
    const first = input("0", "number"),
      end = input(
        String(Math.min(data.timeline.duration_samples, 120 * 48000)),
        "number",
      );
    const analysis = element("pre");
    listen.append(
      actionForm(
        "Render audio audition",
        [
          field("First audition sample", first),
          field("End audition sample (exclusive)", end),
        ],
        async () => {
          if (dirty)
            throw new Error(
              "Apply or reload the pending audio edits before auditioning.",
            );
          const auditionRevision = history.current.revision;
          const result = await api(`${path}/audio/audition`, "web_audio_mix", {
            expected_revision: auditionRevision,
            first_sample: number(first),
            end_sample: number(end),
          });
          if (!active()) return;
          player.src = `/api/v1${base}/audio/auditions/${result.id}/media`;
          auditionStatus.textContent = `${dirty || history.current.revision !== auditionRevision ? "STALE audition · " : ""}Saved revision ${auditionRevision} · snapshot ${result.report.snapshot_sha256}`;
          const r = result.report;
          analysis.textContent = `Verified samples: ${r.sample_count}\nPeak: ${r.sample_peak_dbfs ?? "silence"} dBFS\nTrue peak: ${r.true_peak_dbtp ?? "unmeasured"} dBTP\nIntegrated loudness: ${r.integrated_lufs ?? "unmeasured"} LUFS\nSamples over full scale: ${r.over_full_scale_samples}\nSuggested gain adjustment: ${r.suggested_gain_db ?? "none"} dB (not applied)\n${r.warnings.join("\n")}`;
          return "Audition ready. Press Play to listen; measurements do not replace your review.";
        },
      ),
      auditionStatus,
      player,
      analysis,
    );
    root.append(
      state,
      button("Import WAV masters in Assets", () => {
        location.hash = "assets";
      }),
      report,
      undo,
      redo,
      rows,
      add,
      actionForm(
        "Review timing changes",
        [
          field(
            "Lay music consecutively in this list order (ambience keeps explicit positions)",
            contiguous,
          ),
        ],
        plan,
      ),
      proposal,
      save,
      listen,
    );
    draw();
    issues();
    const metadata = section(
      "Music release metadata",
      "Enter factual titles, credits and known IDs. Blank ISRC/UPC stay unknown. Saving a draft does not grant creative or publishing approval.",
    );
    const releaseId = input("music-release"),
      artist = input(""),
      title = input(""),
      upc = input("");
    const source = choice(
      data.sources.map((s) => [`${s.asset.id}@${s.asset.version}`, s.asset.id]),
    );
    const trackTitle = input(""),
      isrc = input(""),
      credits = jsonEditor([]),
      explicit = choice([
        ["", "Unknown"],
        ["no", "No"],
        ["yes", "Yes"],
      ]);
    const rowsJson = jsonEditor([]);
    metadata.append(
      actionForm(
        "Add master to metadata draft",
        [
          field("Metadata master", source),
          field("Track title", trackTitle),
          field("Credits JSON", credits),
          field("Explicit content", explicit),
          field("Known ISRC", isrc),
        ],
        async () => {
          const found = data.sources.find(
            (s) => `${s.asset.id}@${s.asset.version}` === source.value,
          )?.asset;
          if (!found) throw new Error("Choose an imported master.");
          const list = JSON.parse(rowsJson.value);
          if (!Array.isArray(list))
            throw new Error("Track metadata must be a list.");
          list.push({
            asset: { id: found.id, version: found.version },
            title: trackTitle.value,
            master: found.files[0].location,
            sha256: found.files[0].sha256,
            sample_rate: found.probe.sample_rate,
            channels: found.probe.channels,
            duration_samples: found.probe.duration_samples,
            credits: JSON.parse(credits.value),
            explicit_content:
              explicit.value === "" ? null : explicit.value === "yes",
            isrc: isrc.value || null,
            commercial_use_status:
              found.provenance?.commercial_use || "pending",
            ai_use_notes: found.provenance?.generation?.notes || null,
          });
          rowsJson.value = JSON.stringify(list, null, 2);
          return "Added to metadata draft. Review and save below.";
        },
      ),
    );
    let editing: Documents["release_record"] | undefined;
    metadata.append(
      actionForm(
        "Save music metadata draft",
        [
          field("Release ID", releaseId),
          field("Artist", artist),
          field("Release title", title),
          field("Known UPC", upc),
          field("Ordered track metadata JSON", rowsJson),
        ],
        async () => {
          const record = checked("release_record", {
            ...editing,
            schema_version: "1.0",
            document_type: "release_record",
            id: releaseId.value,
            revision: editing?.revision || 0,
            artist: artist.value,
            release_title: title.value,
            upc: upc.value || null,
            tracks: JSON.parse(rowsJson.value),
            status: "draft",
            rights_status: editing?.rights_status || "pending",
          });
          editing = await api(`${base}/music-metadata`, "release_record", {
            record,
            expected_revision: editing?.revision ?? null,
          });
          releaseId.disabled = true;
          return `Metadata saved at revision ${editing.revision}. Rights/creative review remains separate.`;
        },
      ),
    );
    for (const record of catalog.releases)
      metadata.append(
        button(`Edit metadata: ${record.release_title}`, () => {
          if (record.status !== "draft") {
            state.textContent =
              "Reviewed records are preserved. Create a new draft ID for changed metadata.";
            return;
          }
          editing = record;
          releaseId.value = record.id;
          releaseId.disabled = true;
          artist.value = record.artist;
          title.value = record.release_title;
          upc.value = record.upc || "";
          rowsJson.value = JSON.stringify(record.tracks, null, 2);
        }),
      );
    root.append(metadata);
    cleanup = () => {
      player.pause();
      player.removeAttribute("src");
      player.load();
      window.removeEventListener("beforeunload", beforeUnload);
    };
  });
  return {
    root: panel.root,
    dispose: () => {
      panel.dispose();
      cleanup();
    },
  };
}
