import { fetchDocument } from "./contracts";
import { button, element, field, section } from "./dom";

export function playbackSpike() {
  const root = element("div");
  const status = element("p", {
    className: "notice",
    text: "Loading the registered synthetic proxy…",
  });
  status.setAttribute("role", "status");
  root.append(status);
  const layout = element("div", { className: "preview-layout" });
  const player = section(
    "Rendered proxy",
    "Continuous playback uses approximate browser time.",
  );
  const video = element("video", { id: "proxy-video" });
  video.controls = true;
  video.preload = "metadata";
  video.playsInline = true;
  video.volume = 0.15;
  const clock = element("p", {
    className: "mono",
    text: "Player time: 0.000 s (approximate)",
  });
  const controls = element("div", { className: "toolbar" });
  let audio: AudioContext | undefined;
  let analyser: AnalyserNode | undefined;
  let audioData: Uint8Array<ArrayBuffer> | undefined;
  let disposed = false;
  let maxRms = 0;
  let decodedFrames = 0;
  let totalFrames = 0;
  let exactRequest = 0;
  let abort: AbortController | undefined;
  const events: { name: string; time: number; readyState: number }[] = [];
  const diagnosticText = element("pre");
  const observed = () => ({
    userAgent: navigator.userAgent,
    content:
      "Synthetic playback engineering check; not artistic/listening approval",
    h264AacSupport: video.canPlayType(
      'video/mp4; codecs="avc1.640028, mp4a.40.2"',
    ),
    currentTime: video.currentTime,
    duration: Number.isFinite(video.duration) ? video.duration : null,
    videoWidth: video.videoWidth,
    videoHeight: video.videoHeight,
    paused: video.paused,
    muted: video.muted,
    volume: video.volume,
    decodedFrames,
    maximumDecodedAudioRms: maxRms,
    audioContext: audio?.state ?? "not_started",
    error: video.error?.message ?? null,
    events,
  });
  function update() {
    if (disposed) return;
    clock.textContent = `Player time: ${video.currentTime.toFixed(3)} s (approximate)`;
    if (analyser && audioData) {
      analyser.getByteTimeDomainData(audioData);
      const rms = Math.sqrt(
        audioData.reduce((sum, value) => sum + ((value - 128) / 128) ** 2, 0) /
          audioData.length,
      );
      maxRms = Math.max(maxRms, rms);
    }
    diagnosticText.textContent = JSON.stringify(observed(), null, 2);
  }
  async function play() {
    try {
      audio ??= new AudioContext();
      if (!analyser) {
        analyser = audio.createAnalyser();
        audioData = new Uint8Array(new ArrayBuffer(analyser.fftSize));
        audio.createMediaElementSource(video).connect(analyser);
        analyser.connect(audio.destination);
      }
      await audio.resume();
      await video.play();
    } catch (error) {
      status.textContent = `Playback unavailable: ${String(error)}`;
    }
  }
  controls.append(
    button("Play with audio", () => void play(), "button primary"),
    button("Pause", () => video.pause()),
    button("Seek to middle", () => {
      if (Number.isFinite(video.duration))
        video.currentTime = video.duration / 2;
    }),
  );
  for (const name of [
    "loadedmetadata",
    "playing",
    "pause",
    "seeking",
    "seeked",
    "ended",
    "error",
    "waiting",
  ]) {
    video.addEventListener(name, () => {
      events.push({
        name,
        time: video.currentTime,
        readyState: video.readyState,
      });
      if (events.length > 40) events.shift();
      if (name === "error")
        status.textContent =
          "The proxy could not load. Check the local worker and registered media.";
      update();
    });
  }
  const countFrame: VideoFrameRequestCallback = () => {
    decodedFrames += 1;
    if (!disposed) video.requestVideoFrameCallback(countFrame);
  };
  video.requestVideoFrameCallback?.(countFrame);
  player.append(video, controls, clock);
  const exact = section(
    "Exact renderer frame",
    "Python supplies this still. Video seeking does not determine its pixels.",
  );
  const image = element("img", { className: "frame-image" });
  image.alt = "Awaiting a rendered frame";
  const frame = element("input");
  frame.type = "number";
  frame.min = "0";
  frame.step = "1";
  frame.value = "151";
  frame.disabled = true;
  const frameStatus = element("p", {
    text: "Awaiting frame",
    className: "mono",
  });
  async function loadFrame() {
    const value = Number(frame.value);
    if (!Number.isSafeInteger(value) || value < 0 || value >= totalFrames) {
      frameStatus.textContent = `Choose an integer frame from 0 to ${totalFrames - 1}.`;
      return;
    }
    const request = ++exactRequest;
    abort?.abort();
    abort = new AbortController();
    frameStatus.textContent = `Rendering frame ${value}…`;
    try {
      const report = await fetchDocument(
        `/spike/frame/${value}.json`,
        "render_report",
        abort.signal,
      );
      if (request !== exactRequest || disposed) return;
      if (report.first_frame !== value || report.frame_count !== 1)
        throw new Error("Renderer frame report differs from the request");
      image.src = `/spike/frame/${value}.png`;
      image.alt = `Synthetic Python-rendered frame ${value}`;
      image.onload = () => {
        if (request === exactRequest)
          frameStatus.textContent = `Renderer frame ${value} · exact`;
      };
      image.onerror = () => {
        frameStatus.textContent = "The rendered still could not load.";
      };
    } catch (error) {
      if (request === exactRequest) frameStatus.textContent = String(error);
    }
  }
  frame.addEventListener("change", () => void loadFrame());
  const step = (direction: number) => {
    frame.value = String(
      Math.max(0, Math.min(totalFrames - 1, Number(frame.value) + direction)),
    );
    void loadFrame();
  };
  const stepButtons = element("div", { className: "toolbar" });
  stepButtons.append(
    button("Previous frame", () => step(-1)),
    button("Next frame", () => step(1)),
  );
  exact.append(image, field("Global frame", frame), stepButtons, frameStatus);
  layout.append(player, exact);
  root.append(layout);
  const identity = element("p", { className: "identity" });
  const details = element("details", { className: "panel" });
  details.append(
    element("summary", { text: "Observed playback diagnostics" }),
    diagnosticText,
  );
  details.append(button("Refresh diagnostics", update));
  details.append(
    button("Save diagnostic report", () => {
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(observed(), null, 2)], {
          type: "application/json",
        }),
      );
      const link = element("a");
      link.href = url;
      link.download = "tabi-browser-playback.json";
      link.click();
      URL.revokeObjectURL(url);
    }),
  );
  root.append(identity, details);
  void fetchDocument("/spike/export.json", "export_verification")
    .then((report) => {
      if (disposed) return;
      video.src = "/spike/video.mp4";
      totalFrames = report.video.frame_count;
      frame.max = String(totalFrames - 1);
      frame.value = String(Math.min(151, totalFrames - 1));
      frame.disabled = false;
      status.textContent = `SYNTHETIC TEST · Verified ${report.video.canvas.width} × ${report.video.canvas.height} H.264 / ${report.audio?.codec?.toUpperCase() ?? "no audio"} · ${totalFrames} frames`;
      identity.textContent = `Snapshot ${report.snapshot_sha256} · Video ${report.output.sha256}`;
      void loadFrame();
    })
    .catch((error: unknown) => {
      status.textContent = String(error);
    });
  const keyboard = (event: KeyboardEvent) => {
    if (
      event.target instanceof HTMLElement &&
      (event.target.matches("input,textarea,select,button,video,a,summary") ||
        event.target.isContentEditable)
    )
      return;
    if (event.code === "Space") {
      event.preventDefault();
      if (video.paused) void play();
      else video.pause();
    }
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      step(event.key === "ArrowLeft" ? -1 : 1);
    }
  };
  window.addEventListener("keydown", keyboard);
  // Media events and a modest timer also update background Safari tabs, where
  // requestAnimationFrame may be suspended while audio playback continues.
  video.addEventListener("timeupdate", update);
  const observationTimer = window.setInterval(update, 250);
  update();
  return {
    root,
    dispose: () => {
      disposed = true;
      video.pause();
      video.removeAttribute("src");
      video.load();
      abort?.abort();
      window.clearInterval(observationTimer);
      void audio?.close();
      window.removeEventListener("keydown", keyboard);
    },
  };
}
