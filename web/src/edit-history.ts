/** Serialized document commands. Undo/redo are new guarded saves, never disk rollback. */
export class EditHistory<T extends { revision?: number }> {
  current: T;
  past: T[] = [];
  future: T[] = [];
  pending = 0;
  tail: Promise<void> = Promise.resolve();
  transport: (revision: number, command: unknown) => Promise<T>;
  constructor(
    initial: T,
    transport: (revision: number, command: unknown) => Promise<T>,
  ) {
    this.current = structuredClone(initial);
    this.transport = transport;
  }
  private enqueue(operation: () => Promise<T>): Promise<T> {
    this.pending++;
    const next = this.tail.then(operation);
    this.tail = next
      .then(
        () => {},
        () => {},
      )
      .finally(() => {
        this.pending--;
      });
    return next;
  }
  apply(command: unknown) {
    return this.enqueue(async () => {
      const before = structuredClone(this.current);
      const saved = await this.transport(this.current.revision || 0, command);
      this.past.push(before);
      this.past = this.past.slice(-100);
      this.future = [];
      this.current = structuredClone(saved);
      return saved;
    });
  }
  undo() {
    return this.enqueue(async () => {
      const before = this.past.at(-1);
      if (!before) return this.current;
      const saved = await this.transport(this.current.revision || 0, {
        kind: "replace",
        episode: before,
      });
      this.past.pop();
      this.future.push(structuredClone(this.current));
      this.current = structuredClone(saved);
      return saved;
    });
  }
  redo() {
    return this.enqueue(async () => {
      const after = this.future.at(-1);
      if (!after) return this.current;
      const saved = await this.transport(this.current.revision || 0, {
        kind: "replace",
        episode: after,
      });
      this.future.pop();
      this.past.push(structuredClone(this.current));
      this.current = structuredClone(saved);
      return saved;
    });
  }
}
