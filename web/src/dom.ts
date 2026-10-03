export function element<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  options: { className?: string; text?: string; id?: string } = {},
): HTMLElementTagNameMap[K] {
  const result = document.createElement(tag);
  if (options.className) result.className = options.className;
  if (options.text !== undefined) result.textContent = options.text;
  if (options.id) result.id = options.id;
  return result;
}

export function button(
  label: string,
  handler: () => void,
  className = "button",
) {
  const result = element("button", { text: label, className });
  result.type = "button";
  result.addEventListener("click", handler);
  return result;
}

export function field(label: string, control: HTMLElement) {
  const wrapper = element("label", { className: "field" });
  wrapper.append(element("span", { text: label }), control);
  return wrapper;
}

export function section(title: string, hint?: string) {
  const result = element("section", { className: "panel" });
  result.append(element("h2", { text: title }));
  if (hint) result.append(element("p", { text: hint, className: "muted" }));
  return result;
}
