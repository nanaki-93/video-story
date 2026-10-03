import { api, request, sessionPanel } from "./session";
import type { Documents } from "./contracts";
import { button, element, field, section } from "./dom";
import { generationPanel } from "./generation";
import {
  actionForm,
  choice,
  episodeId,
  input,
  jsonEditor,
  number,
  prefix,
  projectPage,
  refreshPage,
  remember,
} from "./workspace";

export function rendersPage() {
  let timer = 0;
  const players: HTMLVideoElement[] = [];
  const page = projectPage(async (root, project, catalog, active) => {
    const base = prefix(project),
      settings = await api("/settings", "web_settings");
    if (!active()) return;
    const episode = catalog.episodes.find((e) => e.id === episodeId());
    const state = element("p", { className: "notice" });
    state.setAttribute("role", "status");
    const list = section(
      "Saved render queue",
      "Closing this tab leaves jobs running. Pausing finishes the current video chunk; cancelling stops only this worker's owned work and retains verified chunks.",
    );
    root.append(state, button("Reload latest drafts", refreshPage));
    if (episode) {
      const setup = section(
        "Freeze and export",
        "Draft previews are labeled. Production needs approved inputs and explicit review of the frozen snapshot. Later edits do not change an existing job.",
      );
      const purpose = choice([
        ["preview", "Draft preview"],
        ["production", "Production with approved inputs"],
      ]);
      let frozen: Documents["compilation_result"] | undefined,
        planned: Record<string, unknown> | undefined;
      let generation = 0;
      const frozenLabel = element("p", { className: "mono" });
      const preset = choice(
        [
          ["proxy", "Proxy · 960 × 540"],
          ["1080p", "1080p · 1920 × 1080"],
          ["4k", "4K · 3840 × 2160"],
        ],
        settings.preferences.export_preset,
      );
      const encoder = choice(
        [
          ["libx264", "Software H.264"],
          ["h264_videotoolbox", "Apple VideoToolbox H.264"],
        ],
        settings.preferences.encoder,
      );
      const destination = input(`exports/${episode.id}-${Date.now()}.mp4`),
        first = input("0", "number"),
        end = input(String(episode.duration_frames), "number"),
        chunks = input("900", "number");
      const estimate = element("pre", { className: "state" });
      const queue = button("Queue frozen export", () => {
        if (!planned) return;
        queue.disabled = true;
        void api(`${base}/renders`, "render_job", planned)
          .then((job) => {
            state.textContent = `Queued ${job.id}. The frozen plan is saved on disk.`;
            planned = undefined;
            void poll();
          })
          .catch((error: unknown) => {
            state.textContent = String(error);
            queue.disabled = !planned;
          });
      });
      queue.disabled = true;
      function changed() {
        ++generation;
        planned = undefined;
        queue.disabled = true;
        estimate.textContent =
          "Export settings changed. Estimate again before queueing.";
      }
      for (const control of [preset, encoder, destination, first, end, chunks])
        control.addEventListener("input", changed);
      purpose.addEventListener("change", () => {
        frozen = undefined;
        frozenLabel.textContent = "Freeze this purpose before continuing.";
        changed();
      });
      setup.append(
        actionForm(
          "Freeze saved episode",
          [field("Render purpose", purpose)],
          async () => {
            const wanted = purpose.value;
            const result = await api(
              `${base}/episodes/${episode.id}/compile`,
              "compilation_result",
              { expected_revision: episode.revision, purpose: wanted },
            );
            if (!active() || purpose.value !== wanted)
              return "Purpose changed. Freeze again.";
            frozen = result;
            changed();
            frozenLabel.textContent = `${result.purpose} snapshot ${result.snapshot_sha256} · ${result.duration_frames} frames`;
            return "Frozen snapshot saved. Inspect the estimate below.";
          },
        ),
        frozenLabel,
      );
      const reviewer = input(""),
        note = input("");
      const review = element("details");
      review.append(
        element("summary", { text: "Review a production snapshot" }),
        actionForm(
          "Record my production snapshot review",
          [field("Reviewer", reviewer), field("Review note", note)],
          async () => {
            if (!frozen || frozen.purpose !== "production")
              throw new Error(
                "Freeze a production snapshot with approved inputs first.",
              );
            frozen = await api(
              `${base}/snapshots/${frozen.snapshot_sha256}/review`,
              "compilation_result",
              {
                expected_hash: frozen.review_content_sha256,
                reviewer: reviewer.value,
                note: note.value,
              },
            );
            changed();
            frozenLabel.textContent = `Reviewed production snapshot ${frozen.snapshot_sha256}`;
            return "Review recorded for this exact content hash.";
          },
        ),
      );
      setup.append(
        review,
        actionForm(
          "Estimate export storage",
          [
            field("Output profile", preset),
            field("Video encoder", encoder),
            field(`New output beneath ${project.path}/exports/`, destination),
            field("First export frame", first),
            field("End export frame (exclusive)", end),
            field("Maximum frames per video chunk", chunks),
          ],
          async () => {
            if (!frozen) throw new Error("Freeze the saved episode first.");
            const requested = generation;
            const body = {
              snapshot_sha256: frozen.snapshot_sha256,
              preset: preset.value,
              encoder: encoder.value,
              destination: destination.value,
              first_frame: number(first),
              end_frame: number(end),
              max_chunk_frames: number(chunks),
            };
            const plan = await api(
              `${base}/renders/plan`,
              "web_render_plan",
              body,
            );
            if (!active() || requested !== generation)
              return "Settings changed during estimation. Estimate again.";
            estimate.textContent = `${plan.job.profile.canvas.width} × ${plan.job.profile.canvas.height} · ${plan.job.profile.fps.num}/${plan.job.profile.fps.den} fps\n${plan.job.chunks.length} chunks · ${plan.job.duration_frames} frames\nAdditional space estimate: ${(plan.storage.required_additional_bytes / 1024 ** 3).toFixed(2)} GiB\nAvailable: ${(plan.storage.available_bytes / 1024 ** 3).toFixed(2)} GiB\n${plan.storage.assumptions.join("\n")}`;
            planned = plan.storage.sufficient ? body : undefined;
            queue.disabled = !planned;
            return plan.storage.sufficient
              ? "Estimate is sufficient; space is checked again when the job starts."
              : "Not enough project space. Free storage or prune managed cache before queueing.";
          },
        ),
        estimate,
        queue,
      );
      root.append(setup);
    }
    root.append(list);
    type Row = {
      root: HTMLElement;
      status: HTMLElement;
      details: HTMLElement;
      pause: HTMLButtonElement;
      cancel: HTMLButtonElement;
      resume: HTMLButtonElement;
      verify: HTMLButtonElement;
      link: HTMLButtonElement;
      revision: number;
    };
    const rows = new Map<string, Row>();
    let polling = false;
    function rowFor(job: Documents["render_job"]): Row {
      const found = rows.get(job.id);
      if (found) return found;
      const card = section(job.id, job.destination || "Saved job"),
        status = element("p", { className: "notice" }),
        details = element("pre");
      const diagnostic = element("details");
      diagnostic.append(
        element("summary", { text: "Job diagnostics and frozen profile" }),
        details,
      );
      const run = (operation: string) => {
        void api(
          `${base}/jobs/${job.id}/${operation}`,
          operation === "verify" ? "export_verification" : "render_job",
          {},
        )
          .then(() => {
            state.textContent = `${job.id}: ${operation} accepted.`;
            void poll();
          })
          .catch((error: unknown) => {
            state.textContent = String(error);
          });
      };
      const pause = button("Pause after current chunk", () => run("pause")),
        cancel = button("Cancel owned job", () => run("cancel")),
        resume = button("Resume verified progress", () => run("resume")),
        verify = button("Verify export again", () => run("verify"));
      const link = button("Open verified export", () => {});
      const source = `/api/v1${base}/jobs/${job.id}/video`;
      link.hidden = true;
      const playback = element("div");
      playback.hidden = true;
      const video = element("video", { className: "preview-media" });
      video.controls = true;
      video.playsInline = true;
      video.preload = "metadata";
      players.push(video);
      const seconds = input("0", "number");
      seconds.min = "0";
      seconds.step = "0.1";
      const clock = element("p", { className: "mono" });
      video.addEventListener("timeupdate", () => {
        clock.textContent = `Playback ${video.currentTime.toFixed(2)} / ${video.duration.toFixed(2)} seconds (approximate)`;
      });
      video.addEventListener("error", () => {
        clock.textContent =
          "Export playback failed. Check the worker connection and verify the saved export.";
      });
      link.addEventListener("click", (event) => {
        event.preventDefault();
        for (const other of players) {
          if (other === video) continue;
          other.pause();
          other.removeAttribute("src");
          other.load();
          if (other.parentElement) other.parentElement.hidden = true;
        }
        if (!video.getAttribute("src")) video.src = source;
        playback.hidden = false;
      });
      playback.append(
        video,
        actionForm(
          "Seek export",
          [field("Playback seconds", seconds)],
          async () => {
            const value = Number(seconds.value);
            if (
              !Number.isFinite(video.duration) ||
              !Number.isFinite(value) ||
              value < 0 ||
              value >= video.duration
            )
              throw new Error(
                "Choose a playback time within the loaded export.",
              );
            video.currentTime = value;
            return "Seek requested. Browser time is approximate; use Preview for exact renderer frames.";
          },
        ),
        clock,
      );
      card.append(
        status,
        pause,
        cancel,
        resume,
        verify,
        link,
        playback,
        diagnostic,
      );
      list.append(card);
      const result = {
        root: card,
        status,
        details,
        pause,
        cancel,
        resume,
        verify,
        link,
        revision: -1,
      };
      rows.set(job.id, result);
      return result;
    }
    async function poll() {
      if (!active() || polling) return;
      polling = true;
      clearTimeout(timer);
      try {
        const jobs = await api(`${base}/jobs`, "web_jobs");
        if (!active()) return;
        if (!jobs.jobs.length && !rows.size)
          state.textContent =
            "No render jobs yet. Freeze an episode and inspect its storage estimate.";
        for (const job of jobs.jobs) {
          const row = rowFor(job);
          let detail = "";
          if (job.state === "running") {
            const measured = await api(
              `${base}/jobs/${job.id}/progress`,
              "job_progress",
            );
            if (!active()) return;
            detail =
              measured.eta_seconds === null
                ? " · Measuring speed / assembling and checking audio-video…"
                : ` · Measured estimate: about ${Math.ceil(measured.eta_seconds)} seconds of video work remaining (${measured.measured_fps?.toFixed(1)} fps); assembly follows`;
          }
          row.status.textContent = `${job.state}${job.pause_requested ? " · pause requested" : ""} · ${job.completed_frames}/${job.duration_frames} verified frames${detail}${job.error ? ` · ${job.error.message}` : ""}`;
          row.pause.disabled =
            !["running", "queued"].includes(job.state) || !!job.pause_requested;
          row.cancel.disabled = ![
            "running",
            "queued",
            "paused",
            "interrupted",
          ].includes(job.state);
          row.resume.disabled = ![
            "paused",
            "interrupted",
            "failed",
            "cancelled",
          ].includes(job.state);
          row.verify.disabled = job.state !== "verified";
          row.link.hidden = job.state !== "verified";
          if (row.revision !== job.revision) {
            row.details.textContent = JSON.stringify(job, null, 2);
            row.revision = job.revision || 0;
          }
        }
      } catch (error) {
        if (active())
          state.textContent = `Worker unavailable: ${String(error)}. Reopen from the launcher to recover saved jobs.`;
      } finally {
        polling = false;
        if (active())
          timer = window.setTimeout(() => {
            void poll();
          }, 1500);
      }
    }
    await poll();
  });
  return {
    root: page.root,
    dispose: () => {
      page.dispose();
      clearTimeout(timer);
      for (const video of players) {
        video.pause();
        video.removeAttribute("src");
        video.load();
      }
    },
  };
}

export function settingsPage() {
  const session = sessionPanel(remember),
    root = element("div");
  root.append(session.root);
  let active = true;
  const status = element("p", { className: "notice" });
  root.append(status);
  void api("/settings", "web_settings")
    .then((data) => {
      if (!active) return;
      const prefs = section(
        "Preferences",
        "Defaults are saved locally. Cache cleanup is explicit and never removes source masters or artwork.",
      );
      const theme = choice(
          [
            ["dusk", "Dusk"],
            ["contrast", "High contrast"],
          ],
          data.preferences.theme,
        ),
        preset = choice(
          [
            ["proxy", "Proxy"],
            ["1080p", "1080p"],
            ["4k", "4K"],
          ],
          data.preferences.export_preset,
        ),
        encoder = choice(
          [
            ["libx264", "Software H.264"],
            ["h264_videotoolbox", "Apple VideoToolbox"],
          ],
          data.preferences.encoder,
        ),
        budget = input(
          String(
            (data.preferences.cache_budget_bytes ?? 20 * 1024 ** 3) / 1024 ** 3,
          ),
          "number",
        );
      budget.step = "0.1";
      const generation = data.preferences.generation;
      const genMode = choice(
        [
          ["false", "Disabled"],
          ["true", "Enabled for allowlisted workflows"],
        ],
        String(generation?.enabled ?? false),
      );
      const genEndpoint = input(
        generation?.endpoint || "http://127.0.0.1:8188",
      );
      const genHashes = jsonEditor(generation?.allowed_workflow_hashes || []);
      const genBudget = input(
        String((generation?.max_output_bytes ?? 64 * 1024 ** 2) / 1024 ** 2),
        "number",
      );
      const genFields = element("details");
      genFields.append(
        element("summary", { text: "Local ComfyUI execution settings" }),
        element("p", {
          text: "Allow only manifests you reviewed, including their workflow, local model files and installed nodes. This app does not install models or change custom nodes.",
        }),
        field("Local generation", genMode),
        field("ComfyUI loopback endpoint", genEndpoint),
        field("Allowed workflow manifest hashes JSON", genHashes),
        field("Generation import limit (MiB)", genBudget),
      );
      prefs.append(
        actionForm(
          "Save local preferences",
          [
            field("Theme", theme),
            field("Default export profile", preset),
            field("Default encoder", encoder),
            field("Managed cache target (GiB)", budget),
            genFields,
          ],
          async () => {
            const result = await api(
              "/settings/preferences",
              "app_preferences",
              {
                preferences: {
                  ...data.preferences,
                  theme: theme.value,
                  export_preset: preset.value,
                  encoder: encoder.value,
                  cache_budget_bytes: Math.round(
                    Number(budget.value) * 1024 ** 3,
                  ),
                  generation: {
                    enabled: genMode.value === "true",
                    endpoint: genEndpoint.value,
                    allowed_workflow_hashes: JSON.parse(genHashes.value),
                    max_output_bytes: Math.round(
                      Number(genBudget.value) * 1024 ** 2,
                    ),
                  },
                },
                expected_revision: data.preferences_saved
                  ? data.preferences.revision
                  : null,
              },
            );
            data = { ...data, preferences: result, preferences_saved: true };
            document.documentElement.dataset.theme = result.theme;
            return "Preferences saved. Reopen Renders to use the new defaults.";
          },
        ),
      );
      const tools = section(
        "Media tools",
        "Tool changes are saved with a backup and take effect after restarting the launcher. Active jobs retain the tools they started with.",
      );
      const ffmpeg = input(data.ffmpeg),
        ffprobe = input(data.ffprobe);
      tools.append(
        element("p", {
          className: "mono",
          text: `Config: ${data.config_file}`,
        }),
        actionForm(
          "Save tool paths for next launch",
          [
            field("FFmpeg executable", ffmpeg),
            field("FFprobe executable", ffprobe),
          ],
          async () => {
            data = await api("/settings/tools", "web_settings", {
              ffmpeg: ffmpeg.value,
              ffprobe: ffprobe.value,
              expected_hash: data.config_sha256,
            });
            return "Tool configuration saved. Restart using the same config file; environment overrides still take precedence.";
          },
        ),
      );
      root.append(
        prefs,
        tools,
        actionForm("Stop worker after current job", [], async () => {
          await request("/shutdown", { mode: "after_job" });
          return "Stopping after the current job. Queued work stays saved.";
        }),
      );
    })
    .catch((e: unknown) => {
      if (active) status.textContent = String(e);
    });
  const project = projectPage((box, item, _catalog, isActive) => {
    const base = prefix(item),
      health = section("Tool and storage health"),
      report = element("pre");
    health.append(
      actionForm("Check media tools", [], async () => {
        const result = await api(`${base}/doctor`, "capability_report");
        if (isActive()) report.textContent = JSON.stringify(result, null, 2);
        return result.ready
          ? "Required tool capabilities are available."
          : "Resolve the capability issues before rendering.";
      }),
      report,
    );
    const cache = section(
      "Managed project cache",
      "Inspect first, then remove only the proposed unprotected entries. Active workers, source references, unknown files and snapshots are protected.",
    );
    let inventory: Documents["web_cache"] | undefined;
    const details = element("pre"),
      prune = button("Apply proposed cache cleanup", () => {
        if (!inventory) return;
        prune.disabled = true;
        void api(`${base}/cache/prune`, "cache_prune_report", {
          expected_inventory: inventory.inventory.inventory_sha256,
          keys: inventory.proposed_keys,
        })
          .then((result) => {
            details.textContent = `Removed ${result.removed.length} disposable entries (${result.removed_entry_bytes} bytes). Retained ${result.remaining_entry_bytes} cache bytes.`;
            inventory = undefined;
          })
          .catch((error: unknown) => {
            details.textContent = String(error);
            inventory = undefined;
          });
      });
    prune.disabled = true;
    cache.append(
      actionForm("Inspect cache and propose cleanup", [], async () => {
        inventory = await api(`${base}/cache`, "web_cache");
        if (!isActive()) return;
        details.textContent = `Managed bytes: ${inventory.inventory.entry_bytes}\nTarget bytes: ${inventory.budget_bytes}\nProposed removals: ${inventory.proposed_keys.length}\nProtected entries: ${inventory.inventory.entries.filter((e) => e.protected).length}\nInvalid entries: ${inventory.inventory.entries.filter((e) => !e.valid).length}\n${(inventory.inventory.warnings ?? []).join("\n")}`;
        prune.disabled = !inventory.proposed_keys.length;
        return "Review this observed inventory before applying cleanup.";
      }),
      details,
      prune,
    );
    box.append(health, cache, generationPanel(base, isActive));
  });
  root.append(project.root);
  return {
    root,
    dispose: () => {
      active = false;
      session.dispose();
      project.dispose();
    },
  };
}
