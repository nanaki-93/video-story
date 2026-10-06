// Presentation and request ordering only. Python owns timing and the next action.
export function flowHandoff(mode: string) {
  if (mode === "shot_start")
    return {
      title: "Start new shot in Flow",
      instruction:
        "Choose Frames to Video, attach this clean starting image, and select 8 seconds, landscape 16:9. Use the saved prompt once and import the downloaded native clip.",
      useReference: true,
      extendParent: false,
      retry: "Retry from clean starting image",
    };
  if (mode === "extend")
    return {
      title: "Extend this shot in Flow",
      instruction:
        "Select the accepted clip below and use Extend. Check the supported model and displayed cost in Flow (currently Veo Lite for native Extend). Import only the new native clip.",
      useReference: false,
      extendParent: true,
      retry: "Retry from accepted parent",
    };
  return {
    title: "Opening in Flow",
    instruction:
      "Use this saved prompt once with your opening reference, then import the downloaded native clip.",
    useReference: true,
    extendParent: false,
    retry: "Retry opening",
  };
}

export class FlowRequests<T> {
  current: T | undefined;
  busy = false;
  private epoch = 0;
  private alive = true;

  async read(task: () => Promise<T>): Promise<T | undefined> {
    if (this.busy || !this.alive) return;
    const epoch = ++this.epoch;
    const value = await task();
    if (!this.alive || epoch !== this.epoch || this.busy) return;
    this.current = value;
    return value;
  }

  async change(task: () => Promise<T>): Promise<T | undefined> {
    if (this.busy || !this.alive) return;
    this.busy = true;
    const epoch = ++this.epoch;
    try {
      const value = await task();
      if (!this.alive || epoch !== this.epoch) return;
      this.current = value;
      return value;
    } finally {
      this.busy = false;
    }
  }

  dispose() {
    this.alive = false;
    this.epoch++;
  }
}
