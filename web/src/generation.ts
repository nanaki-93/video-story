import { api } from "./session";
import { button, element, field, section } from "./dom";
import { actionForm, choice, jsonEditor } from "./workspace";

export function generationPanel(base: string, active: () => boolean) {
  const root = section(
    "Optional local generation",
    "Use an installed ComfyUI server and an explicitly reviewed workflow. Results enter Assets as drafts. Rendering works with this server disabled or offline.",
  );
  const message = element("p", { className: "notice" }),
    content = element("div");
  root.append(message, content);
  async function refresh(probe = false) {
    try {
      const status = await api(
        `${base}/generation?probe=${probe}`,
        "generation_status",
      );
      if (!active()) return;
      message.textContent = `${status.availability}: ${status.message}`;
      content.replaceChildren();
      const workflows = status.workflows || [],
        hashes = status.workflow_hashes || {};
      const list = element("div");
      for (const workflow of workflows) {
        const key = `${workflow.id}@${workflow.version}`,
          hash = hashes[key];
        list.append(
          element("p", { text: `${key} · ${workflow.description}` }),
          element("p", {
            className: "mono",
            text: `Execution manifest SHA-256: ${hash}`,
          }),
        );
      }
      const selected = choice(
        workflows.map((w) => [
          `${w.id}@${w.version}`,
          `${w.id}@${w.version} · ${w.description}`,
        ]),
      );
      const submit = actionForm(
        "Submit selected workflow",
        [field("Registered generation workflow", selected)],
        async () => {
          const [id, version] = selected.value.split("@");
          const result = await api(
            `${base}/generation/submit`,
            "generation_run",
            {
              workflow: { id, version },
              expected_hash: hashes[selected.value],
            },
          );
          await refresh();
          return `${result.id}: ${result.state}. ${result.error || "Refresh its status to follow the server."}`;
        },
      );
      submit.inert = !status.policy.enabled || !workflows.length;
      content.append(list, submit);
      if (!workflows.length)
        content.append(
          element("p", {
            text: "Register a reviewed API workflow manifest below, then add its exact hash to local preferences before execution.",
          }),
        );
      const register = element("details");
      register.append(
        element("summary", { text: "Register a workflow manifest" }),
      );
      const data = jsonEditor({});
      register.append(
        element("p", {
          text: "Include versioned workflow/model file hashes and installed node-definition hashes. Files must be beneath registered local roots. Registration never grants execution permission.",
        }),
        actionForm(
          "Register checked workflow",
          [field("Comfy workflow manifest JSON", data)],
          async () => {
            await api(
              `${base}/generation/workflows`,
              "comfy_workflow",
              JSON.parse(data.value),
            );
            await refresh();
            return "Registered. Review its manifest hash before adding it to the execution allowlist.";
          },
        ),
      );
      content.append(register);
      const runs = section(
        "Generation history",
        "Status comes from the saved prompt ID and the server queue/history. An uncertain submission is never retried automatically. Stop or manage generation in ComfyUI itself.",
      );
      for (const run of status.runs || []) {
        const row = section(
          run.id,
          `${run.manifest.id}@${run.manifest.version} · ${run.state}${run.queue_position !== null && run.queue_position !== undefined ? ` · queue position ${run.queue_position + 1}` : ""}`,
        );
        if (run.error)
          row.append(element("p", { className: "notice", text: run.error }));
        row.append(
          element("p", {
            className: "mono",
            text: `Prompt ${run.prompt_id} · ${run.endpoint}`,
          }),
        );
        const poll = actionForm(`Refresh ${run.id}`, [], async () => {
          const result = await api(
            `${base}/generation/${run.id}/refresh`,
            "generation_run",
            {},
          );
          await refresh();
          return `${result.state}: ${result.error || "Status updated."}`;
        });
        poll.inert =
          !status.policy.enabled || ["failed", "imported"].includes(run.state);
        row.append(poll);
        if (run.state === "succeeded")
          row.append(
            actionForm(`Import drafts from ${run.id}`, [], async () => {
              const result = await api(
                `${base}/generation/${run.id}/import`,
                "generation_run",
                {},
              );
              await refresh();
              return `Imported ${result.imported_assets?.length || 0} draft stills. Review them in Assets.`;
            }),
          );
        for (const asset of run.imported_assets || [])
          row.append(
            element("p", { text: `Draft asset ${asset.id}@${asset.version}` }),
          );
        runs.append(row);
      }
      content.append(runs);
    } catch (error) {
      if (active()) message.textContent = String(error);
    }
  }
  root.append(
    button("Check local generation server", () => {
      void refresh(true);
    }),
  );
  void refresh();
  return root;
}
