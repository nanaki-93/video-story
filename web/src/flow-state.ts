// Request ordering only. Python owns the video state and the next action.
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
