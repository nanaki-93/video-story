/** Prevent a late save response from marking newer edits as saved. */
export class SceneDraft {
  private generation = 0;
  dirty = false;
  change() {
    this.generation++;
    this.dirty = true;
  }
  reset() {
    this.generation++;
    this.dirty = false;
  }
  ticket() {
    return this.generation;
  }
  accept(ticket: number) {
    if (ticket !== this.generation) return false;
    this.dirty = false;
    return true;
  }
}
