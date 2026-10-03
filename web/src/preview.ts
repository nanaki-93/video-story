import { api } from "./session";
import { button, element, field, section } from "./dom";
import {
  actionForm,
  episodeId,
  input,
  number,
  prefix,
  projectPage,
  selectedFrame,
  selectFrame,
} from "./workspace";
import type { Documents } from "./contracts";

export function previewPage() {
  let cleanup = () => {};
  const page = projectPage(async (root, project, catalog, active) => {
    if (!catalog.episodes.length) throw new Error("Create an episode first.");
    const base = prefix(project),
      route = `${base}/episodes/${episodeId()}/preview`;
    let view = await api(route, "web_preview"),
      frameAbort: AbortController | undefined;
    if (!active()) return;
    let timer = 0,
      poll = 0,
      generation = 0;
    let audio: AudioContext | undefined,
      analyser: AnalyserNode | undefined,
      meter = 0;
    let showingJob = "";
    const status = element("p", { className: "notice" });
    status.setAttribute("role", "status");
    const issue = element("p", { className: "state error" });
    const details = element("p", { className: "mono" });
    const proxy = section(
      "Rendered proxy",
      "Playback time is approximate. Select an integer frame below for an exact renderer image.",
    );
    const video = element("video", { className: "preview-media" });
    video.controls = true;
    video.playsInline = true;
    video.preload = "metadata";
    video.setAttribute("aria-label", "Renderer proxy video");
    const clock = element("p", { text: "Approximate proxy time: 0.000 s" });
    video.addEventListener("timeupdate", () => {
      clock.textContent = `Approximate proxy time: ${video.currentTime.toFixed(3)} s`;
    });
    video.addEventListener("error", () => {
      if (!video.getAttribute("src")) return;
      issue.textContent =
        "Video unavailable. Checking the saved artifact and session…";
      void api("/session", "web_session")
        .then(async () => {
          const response = await fetch(video.src, {
            method: "HEAD",
            credentials: "same-origin",
          });
          issue.textContent = response.ok
            ? "The browser could not decode this proxy. Regenerate it or inspect render diagnostics."
            : "The saved proxy is missing or changed. Regenerate it; the episode remains saved.";
        })
        .catch((error: unknown) => {
          if (active())
            issue.textContent = `Worker/session unavailable: ${String(error)}`;
        });
    });
    const rms = element("p", {
      className: "muted",
      text: "Audio meter inactive",
    });
    const audioCheck = button("Check audio level", () => {
      audio ??= new AudioContext();
      if (!analyser) {
        analyser = audio.createAnalyser();
        audio
          .createMediaElementSource(video)
          .connect(analyser)
          .connect(audio.destination);
      }
      void audio.resume();
      clearInterval(meter);
      meter = window.setInterval(() => {
        const samples = new Float32Array(analyser!.fftSize);
        analyser!.getFloatTimeDomainData(samples);
        const level = Math.sqrt(
          samples.reduce((sum, value) => sum + value * value, 0) /
            samples.length,
        );
        rms.textContent = `Decoded browser audio RMS: ${level.toFixed(5)} · listening review remains manual`;
      }, 250);
    });
    proxy.append(video, clock, audioCheck, rms);
    const first = input("0", "number"),
      end = input(
        String(Math.min(view.episode.duration_frames, 900)),
        "number",
      );
    first.min = "0";
    end.min = "1";
    const generate = actionForm(
      "Generate proxy",
      [field("First global frame", first), field("End frame (exclusive)", end)],
      async () => {
        await api(route, "preview_selection", {
          expected_revision: view.episode.revision,
          first_frame: number(first),
          end_frame: number(end),
        });
        await reload();
        return "Snapshot queued. You can keep editing or close this tab while it renders.";
      },
    );
    const inspect = section(
      "Exact frame",
      "This image comes from Python at the selected global frame. It is independent of the player's rounded clock.",
    );
    const cursor = input(String(Math.max(0, selectedFrame)), "number");
    cursor.min = "0";
    cursor.step = "1";
    const scrub = input(cursor.value, "range");
    scrub.min = "0";
    scrub.step = "1";
    const frameStatus = element("p", { className: "state" });
    frameStatus.setAttribute("role", "status");
    const image = element("img", { className: "preview-media" });
    image.alt = "Exact renderer frame pending";
    image.hidden = true;
    const frameHash = element("p", { className: "mono" });
    function select(value: number) {
      const duration =
        view.snapshot_episode?.duration_frames ?? view.episode.duration_frames;
      if (!Number.isSafeInteger(value)) return;
      value = Math.max(0, Math.min(duration - 1, value));
      selectFrame(value);
      cursor.value = scrub.value = String(value);
      image.hidden = true;
      frameHash.textContent = "";
      frameAbort?.abort();
      clearTimeout(timer);
      const revision = ++generation;
      if (!view.selection) {
        frameStatus.textContent =
          "Generate a preview snapshot to inspect its frames.";
        return;
      }
      frameStatus.textContent = `Requesting exact global frame ${value}…`;
      timer = window.setTimeout(() => {
        void exact(value, revision);
      }, 250);
    }
    async function exact(frame: number, revision: number) {
      frameAbort = new AbortController();
      try {
        const result = await api(
          `${base}/frames`,
          "web_frame",
          { snapshot_sha256: view.selection!.snapshot_sha256, frame },
          "POST",
          frameAbort.signal,
        );
        if (!active() || revision !== generation) return;
        image.onload = () => {
          if (revision !== generation || !active()) return;
          image.hidden = false;
          frameStatus.textContent = `Exact global frame ${result.report.first_frame} · ${view.stale ? "older snapshot" : "current snapshot"}`;
        };
        image.onerror = () => {
          if (revision === generation)
            frameStatus.textContent =
              "Frame image unavailable; check the session or request it again.";
        };
        image.alt = `Exact global frame ${result.report.first_frame}`;
        image.src = `/api/v1${base}/frames/${result.id}/image`;
        frameHash.textContent = `PNG SHA-256 ${result.report.output_sha256}`;
      } catch (error) {
        if (!active() || revision !== generation) return;
        frameStatus.textContent = String(error);
        if (String(error).includes("exact frame is finishing"))
          timer = window.setTimeout(() => {
            void exact(frame, revision);
          }, 400);
      }
    }
    cursor.addEventListener("input", () => select(cursor.valueAsNumber));
    scrub.addEventListener("input", () => select(scrub.valueAsNumber));
    inspect.append(
      field("Global frame", cursor),
      field("Scrub exact frames", scrub),
      button("Previous frame", () => select(Number(cursor.value) - 1)),
      button("Next frame", () => select(Number(cursor.value) + 1)),
      button("Render selected frame", () => select(Number(cursor.value))),
      button("Seek proxy near selected frame", () => {
        const job =
            view.previous_job?.id === showingJob ? view.previous_job : view.job,
          fps = job?.profile.fps;
        if (!job || !fps || job.state !== "verified") return;
        video.currentTime =
          (Math.max(
            0,
            Math.min(
              job.duration_frames,
              Number(cursor.value) - (job.first_frame || 0),
            ),
          ) *
            fps.den) /
          fps.num;
      }),
      frameStatus,
      image,
      frameHash,
    );
    const notes = section(
      "Review markers",
      "Notes refer to the exact selected frame and snapshot. They do not approve content for publication.",
    );
    const note = element("textarea");
    note.rows = 2;
    note.required = true;
    const markers = element("div");
    notes.append(
      actionForm(
        "Mark selected frame",
        [field("Review note", note)],
        async () => {
          if (!view.selection) throw new Error("Generate a preview first.");
          view.selection = await api(`${route}/markers`, "preview_selection", {
            snapshot_sha256: view.selection.snapshot_sha256,
            frame: number(cursor),
            note: note.value,
          });
          note.value = "";
          showMarkers();
          return "Review marker saved.";
        },
      ),
      markers,
    );
    function showMarkers() {
      markers.replaceChildren();
      for (const marker of view.selection?.markers || []) {
        const old = marker.snapshot_sha256 !== view.selection?.snapshot_sha256;
        const row = element("p", {
          text: `Frame ${marker.frame} · ${marker.note} ${old ? "(earlier snapshot)" : ""}`,
        });
        if (!old)
          row.append(
            button("Inspect marked frame", () => select(marker.frame)),
          );
        markers.append(row);
      }
    }
    function showJob(job: Documents["render_job"] | null) {
      if (!job) {
        status.textContent = "No proxy yet. Choose a range and generate it.";
        video.hidden = true;
        return;
      }
      status.textContent = `${view.stale ? "STALE — episode, media or renderer changed. " : "Current snapshot. "}${job.state} · ${job.completed_frames}/${job.duration_frames} verified frames${job.error ? ` · ${job.error.message}` : ""}`;
      if (job.state !== "verified" && view.previous_job && !showingJob) {
        video.src = `/api/v1${base}/jobs/${view.previous_job.id}/video`;
        video.hidden = false;
        showingJob = view.previous_job.id;
      }
      if (job.state === "verified" && showingJob !== job.id) {
        video.src = `/api/v1${base}/jobs/${job.id}/video`;
        video.hidden = false;
        showingJob = job.id;
      }
      // Keep the last verified video playable while a replacement is pending.
      if (job.state !== "verified" && showingJob)
        status.textContent +=
          " · Player retains the previous proxy until this one is verified.";
    }
    async function pollJob() {
      if (
        !active() ||
        !view.job ||
        !["queued", "running"].includes(view.job.state)
      )
        return;
      try {
        view.job = await api(`${base}/jobs/${view.job.id}`, "render_job");
        if (active()) showJob(view.job);
      } catch (error) {
        if (active())
          issue.textContent = `Worker/session unavailable: ${String(error)}. Reopen from the launcher; saved work remains on disk.`;
        return;
      }
      if (active())
        poll = window.setTimeout(() => {
          void pollJob();
        }, 1000);
    }
    async function reload() {
      try {
        const result = await api(route, "web_preview");
        if (!active()) return;
        const previousDigest = view.selection?.snapshot_sha256;
        view = result;
        issue.textContent = view.issue || "";
        details.textContent = view.selection
          ? `Snapshot ${view.selection.snapshot_sha256}`
          : "No saved snapshot";
        cursor.max = scrub.max = String(
          (view.snapshot_episode?.duration_frames ??
            view.episode.duration_frames) - 1,
        );
        showJob(view.job);
        showMarkers();
        if (previousDigest !== view.selection?.snapshot_sha256)
          select(Number(cursor.value));
        clearTimeout(poll);
        void pollJob();
      } catch (error) {
        if (active())
          issue.textContent = `Worker/session unavailable: ${String(error)}`;
      }
    }
    const onFocus = () => {
      void reload();
    };
    const keys = (event: KeyboardEvent) => {
      if (
        (event.target as HTMLElement).closest(
          "input,textarea,select,button,[contenteditable]",
        )
      )
        return;
      if (event.code === "Space") {
        event.preventDefault();
        if (video.paused)
          void video.play().catch((e: unknown) => {
            issue.textContent = String(e);
          });
        else video.pause();
      }
      if (event.code === "ArrowRight" || event.code === "ArrowLeft") {
        event.preventDefault();
        select(Number(cursor.value) + (event.code === "ArrowRight" ? 1 : -1));
      }
    };
    window.addEventListener("focus", onFocus);
    window.addEventListener("keydown", keys);
    cleanup = () => {
      frameAbort?.abort();
      ++generation;
      clearTimeout(timer);
      clearTimeout(poll);
      clearInterval(meter);
      video.pause();
      video.removeAttribute("src");
      video.load();
      void audio?.close();
      window.removeEventListener("focus", onFocus);
      window.removeEventListener("keydown", keys);
    };
    root.append(
      status,
      issue,
      details,
      button("Refresh preview status", onFocus),
      generate,
      proxy,
      inspect,
      notes,
    );
    await reload();
    select(Number(cursor.value));
  });
  return {
    root: page.root,
    dispose: () => {
      page.dispose();
      cleanup();
    },
  };
}
