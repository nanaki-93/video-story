import { api, request } from "./session";
import { document as checked } from "./contracts";
import type { Documents } from "./contracts";
import { button, element, field, section } from "./dom";
import {
  choice,
  currentProject,
  input,
  number,
  prefix,
  projectsPage,
} from "./workspace";
import type { Panel, Project } from "./workspace";
import { FlowRequests } from "./flow-state";

type View = Documents["web_flow"];
type Recipe = Documents["flow_episode"]["recipe"];
type State = NonNullable<
  NonNullable<Documents["flow_episode"]["candidates"]>[number]["observed_state"]
>;

function details(title: string, ...nodes: HTMLElement[]) {
  const box = element("details");
  box.append(element("summary", { text: title }), ...nodes);
  return box;
}
function video(url: string, label: string) {
  const box = section(label);
  const player = element("video");
  player.controls = true;
  player.preload = "metadata";
  player.src = url;
  player.setAttribute("aria-label", label);
  box.append(player);
  return box;
}
function checkbox(label: string, initial = false) {
  const control = input("", "checkbox");
  control.checked = initial;
  return { control, node: field(label, control) };
}
function recipeFields(recipe: Recipe) {
  const outfit = input(recipe.outfit);
  const setting = input(recipe.setting);
  const exterior = input(recipe.exterior);
  const url = input(recipe.project_url || "", "url");
  const inventory = input((recipe.opening_inventory || []).join("; "));
  return {
    node: details(
      "Edit settings",
      field("Outfit", outfit),
      field("Interior", setting),
      field("Outside movement", exterior),
      field("Opening objects (separate with semicolons)", inventory),
      field("Your Google Flow project link", url),
    ),
    value: (): Recipe => ({
      ...recipe,
      outfit: outfit.value,
      setting: setting.value,
      exterior: exterior.value,
      opening_inventory: inventory.value
        .split(";")
        .map((v) => v.trim())
        .filter(Boolean),
      project_url: url.value || null,
    }),
  };
}

export function flowPage(): Panel {
  const root = element("div", { className: "flow-workflow" });
  const status = element("p", { className: "notice" });
  status.setAttribute("role", "status");
  const body = element("div");
  root.append(status, body);
  const requests = new FlowRequests<View>();
  let project: Project;
  let fallback: Panel | undefined;
  let alive = true;
  const abort = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let selected = "";
  const base = () => `${prefix(project)}/flow`;
  const path = () => `${base()}/${selected}`;

  function error(e: unknown) {
    if (!alive) return;
    status.textContent = `${String(e)} Reload saved progress before retrying.`;
    status.append(button("Reload saved progress", () => void load()));
  }
  async function change(suffix: string, value: unknown, absolute = false) {
    if (requests.busy) return;
    status.textContent = "Saving and checking…";
    body.inert = true;
    try {
      const result = await requests.change(() =>
        api(absolute ? suffix : `${path()}${suffix}`, "web_flow", value),
      );
      if (result && alive) draw(result);
    } catch (e) {
      error(e);
    } finally {
      body.inert = false;
    }
  }
  async function load() {
    try {
      const result = await requests.read(() =>
        api(selected ? path() : base(), "web_flow"),
      );
      if (result && alive) {
        if (!selected && result.episodes.length) {
          selected = result.episodes.at(-1)!.id;
          await load();
        } else draw(result);
      }
    } catch (e) {
      error(e);
    }
  }
  async function upload(file: File) {
    const key = `tabi-flow-upload-${project.project.id}-${file.name}-${file.size}-${file.lastModified}`;
    let id = localStorage.getItem(key);
    if (!id) {
      id = (
        await api(`${prefix(project)}/uploads`, "web_upload", {
          name: file.name,
          size_bytes: file.size,
        })
      ).id;
      localStorage.setItem(key, id);
    }
    // Recheck acknowledged bytes too; a matching filename alone is insufficient.
    for (let offset = 0; offset < file.size; offset += 4 * 1024 ** 2) {
      const receipt = checked(
        "web_upload",
        await request(
          `${prefix(project)}/uploads/${id}/chunk?offset=${offset}`,
          file.slice(offset, offset + 4 * 1024 ** 2),
          "PUT",
          abort.signal,
        ),
      );
      status.textContent = `Importing ${file.name}: ${Math.round((100 * receipt.received_bytes) / receipt.size_bytes)}%`;
    }
    await api(`${prefix(project)}/uploads/${id}/finish`, "web_upload", {});
    return id;
  }
  function importControl(
    label: string,
    accept: string,
    route: string,
    payload: object,
  ) {
    const file = input("", "file");
    file.accept = accept;
    const synthetic = checkbox("This is synthetic test media");
    const box = section(
      label,
      "Copied and checked locally. Source files stay unchanged.",
    );
    box.append(
      field("Choose local file", file),
      synthetic.node,
      button(label, () => {
        if (requests.busy) return;
        const source = file.files?.[0];
        if (!source) {
          status.textContent = "Choose a file first.";
          return;
        }
        status.textContent = "Importing and checking…";
        body.inert = true;
        void requests
          .change(async () => {
            const id = await upload(source);
            return api(`${path()}${route}`, "web_flow", {
              ...payload,
              upload_id: id,
              synthetic: synthetic.control.checked,
            });
          })
          .then((value) => {
            if (value && alive) draw(value);
          })
          .catch(error)
          .finally(() => {
            body.inert = false;
          });
      }),
    );
    return box;
  }
  function draw(view: View) {
    if (!alive) return;
    clearTimeout(timer);
    const episode = view.episode;
    if (episode) {
      selected = episode.id;
      sessionStorage.setItem(`tabi-flow-${project.project.id}`, selected);
    }
    status.textContent = "Saved locally · Google Flow generation is assisted";
    body.replaceChildren();
    const toolbar = element("div", { className: "toolbar" });
    const chooser = choice(
      [
        ["", "New video"],
        ...view.episodes.map((e) => [e.id, e.title] as [string, string]),
      ],
      episode?.id || "",
    );
    chooser.addEventListener("change", () => {
      selected = chooser.value;
      if (!selected) draw({ ...view, episode: null, next_step: null });
      else void load();
    });
    toolbar.append(
      field("Video", chooser),
      button("Reload saved progress", () => void load()),
    );
    body.append(toolbar);
    if (!episode) {
      const setup = section(
        "1 · Setup",
        "Train · Tokyo · 90 seconds · calm TABI. Look outside, drink, sway and take a deep breath. Music comes at Finish.",
      );
      const title = input("TABI in Tokyo");
      const allowance = input("", "number");
      const cost = input("", "number");
      const ceiling = input("70", "number");
      const settings = recipeFields(view.preset);
      setup.append(
        field("Video title", title),
        settings.node,
        details(
          "Flow allowance",
          element("p", {
            text: "Check your current balance and the displayed cost in Flow. These limits guide manual requests; the app cannot enforce spending inside Google Flow.",
          }),
          field("Credits currently remaining", allowance),
          field("Displayed credits per clip", cost),
          field("Maximum credits for this video", ceiling),
        ),
        button("Start video", () => {
          try {
            const remaining = number(allowance),
              limit = number(ceiling),
              estimated = number(cost);
            void change(
              base(),
              {
                title: title.value,
                recipe: settings.value(),
                limits: {
                  credit_ceiling: limit,
                  remaining_allowance: remaining,
                  estimated_credit_per_attempt: estimated,
                  max_retries_per_beat: 1,
                  max_attempts: 30,
                  allowance_checked_at: new Date().toISOString(),
                },
              },
              true,
            );
          } catch (e) {
            status.textContent =
              "Open Flow allowance and enter the current balance and cost, then start.";
          }
        }),
      );
      body.append(setup);
      return;
    }
    const step = view.next_step!;
    const seconds = (frames: number) =>
      ((frames * episode.recipe.fps!.den) / episode.recipe.fps!.num).toFixed(1);
    const progress = element("progress");
    progress.max = step.target_frames;
    progress.value = step.accepted_frames;
    progress.setAttribute("aria-label", "Reviewed video progress");
    body.append(
      element("h2", { text: episode.title }),
      progress,
      element("p", {
        text: `${seconds(step.accepted_frames)} / ${seconds(step.target_frames)} seconds reviewed · ${step.credit_units} / ${episode.limits.credit_ceiling} credits reserved or observed`,
      }),
      element("p", { text: step.message, className: "flow-next" }),
    );
    const steps = element("ol", { className: "flow-steps" });
    for (const label of ["Setup", "Opening", "Continue", "Finish"])
      steps.append(element("li", { text: label }));
    body.append(steps);
    if ((view.reference_urls || []).length) {
      const refs = details("TABI reference");
      for (const [i, url] of (view.reference_urls || []).entries()) {
        const img = element("img", { className: "flow-reference" });
        img.src = url;
        img.alt = (episode.references || [])[i].title;
        refs.append(img);
      }
      body.append(refs);
    }
    if (step.action === "choose_reference")
      body.append(
        importControl(
          "Import TABI reference",
          "image/png,image/jpeg,image/webp",
          "/reference",
          { expected_revision: episode.revision },
        ),
      );
    else if (step.action === "prepare")
      body.append(
        button(
          "Prepare next prompt",
          () =>
            void change("/prepare", { expected_revision: episode.revision }),
        ),
      );
    else if (step.action === "paused")
      body.append(
        button(
          "Resume video",
          () => void change("/resume", { expected_revision: episode.revision }),
        ),
      );
    else if (step.action === "waiting_flow") {
      const attempt = (episode.attempts || []).find(
        (a) => a.id === step.attempt_id,
      )!;
      const handoff = section(
        (episode.accepted_ids || []).length
          ? "3 · Continue in Flow"
          : "2 · Opening in Flow",
        "Use this saved prompt once. Download the new native clip, rather than the full scene, and import it below.",
      );
      const prompt = element("textarea");
      prompt.value = attempt.prompt;
      prompt.rows = 7;
      prompt.readOnly = true;
      prompt.setAttribute("aria-label", "Focused Flow prompt");
      const link = element("a", {
        className: "button",
        text: "Open Google Flow",
      });
      link.href = episode.recipe.project_url || "https://flow.google.com/";
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      handoff.append(
        prompt,
        button("Copy prompt", () => {
          void navigator.clipboard
            .writeText(attempt.prompt)
            .then(() => {
              status.textContent =
                "Prompt copied. Attach the reference for the opening, or extend the accepted parent.";
            })
            .catch(error);
        }),
        link,
      );
      if (view.parent_url)
        handoff.append(
          video(view.parent_url, "Accepted parent · extend this clip"),
        );
      handoff.append(
        importControl("Import Flow result", "video/mp4", "/import", {
          expected_revision: episode.revision,
          attempt_id: attempt.id,
        }),
        details(
          "Generation failed or connection lost",
          element("p", {
            text: "Do not submit a second request while the first outcome is unknown. Check Flow first.",
          }),
          button(
            "Mark outcome unknown",
            () =>
              void change(`/attempts/${attempt.id}`, {
                expected_revision: episode.revision,
                state: "unknown",
                diagnostic: "Connection lost; checking Flow",
              }),
          ),
          button(
            "Confirm generation failed",
            () =>
              void change(`/attempts/${attempt.id}`, {
                expected_revision: episode.revision,
                state: "failed",
                diagnostic: "User confirmed provider generation failed",
              }),
          ),
        ),
      );
      body.append(handoff);
    } else if (step.action === "review") {
      const candidate = (episode.candidates || []).find(
        (c) => c.id === step.candidate_id,
      )!;
      const parent = (episode.candidates || []).find(
        (c) => c.id === candidate.parent_id,
      );
      const review = section(
        "Review this clip",
        "Watch the whole clip and its ending. Check TABI, objects, outside motion and the requested action before accepting.",
      );
      if (view.candidate_url)
        review.append(video(view.candidate_url, "New clip"));
      if (view.review?.join_url)
        review.append(video(view.review.join_url, "Join with accepted parent"));
      const frames = element("div", { className: "flow-filmstrip" });
      for (const img of view.review?.images || []) {
        const image = element("img");
        image.src = img.url;
        image.alt = `${img.role} frame ${img.frame}`;
        frames.append(image);
      }
      review.append(frames);
      const facts = stateFields(parent?.observed_state || undefined);
      const checked = checkbox(
        "I watched the clip and join; the action finishes and continuity is good",
      );
      const cut =
        view.safe_cut_frame != null
          ? checkbox(
              `I checked the final cut at clip frame ${view.safe_cut_frame}: TABI is settled`,
            )
          : undefined;
      const note = input("");
      review.append(
        facts.node,
        field("Review note / reason for retry", note),
        checked.node,
      );
      if (cut) review.append(cut.node);
      review.append(
        button("Accept clip", () => {
          if (!checked.control.checked) {
            status.textContent =
              "Watch the clip, confirm the ending facts, then tick the review box.";
            return;
          }
          void change(`/clips/${candidate.id}/review`, {
            expected_revision: episode.revision,
            media_sha256: candidate.media.sha256,
            decision: "accepted",
            note: note.value || "Continuity and completed action reviewed",
            observed_state: facts.value(),
            safe_end_frame: cut?.control.checked ? view.safe_cut_frame : null,
          });
        }),
        button("Retry from accepted parent", () => {
          if (!note.value.trim()) {
            status.textContent =
              "Describe the visible defect so the retry prompt stays focused.";
            return;
          }
          void change(`/clips/${candidate.id}/review`, {
            expected_revision: episode.revision,
            media_sha256: candidate.media.sha256,
            decision: "rejected",
            note: note.value,
          });
        }),
      );
      if (view.review)
        review.append(
          details(
            "Technical review (advisory)",
            ...view.review.diagnostics.map((text) => element("p", { text })),
          ),
        );
      body.append(review);
    } else if (step.action === "finish") {
      const finish = section(
        "4 · Finish",
        "Export the reviewed footage at its native resolution and frame rate. Music stays local and plays continuously.",
      );
      const music = choice([
        ["", "Silent for now"],
        ...(view.audio_sources || []).map(
          (a) =>
            [
              a.asset.id,
              `${a.asset.id} · ${(a.prepared_samples / 48000).toFixed(1)} seconds`,
            ] as [string, string],
        ),
      ]);
      const trim = checkbox(
        "Use the first video-length section of this music master if it is longer",
      );
      finish.append(
        field("Soundtrack", music),
        trim.node,
        details(
          "Add a local music file",
          importControl(
            "Import music",
            "audio/wav,audio/x-wav",
            "/music/import",
            { expected_revision: episode.revision },
          ),
        ),
        button("Export video", () => {
          if (
            (view.exports || []).some((e) =>
              ["queued", "running"].includes(e.state),
            )
          ) {
            status.textContent =
              "The export is already running. Wait or cancel it below.";
            return;
          }
          const source = (view.audio_sources || []).find(
            (a) => a.asset.id === music.value,
          );
          if (source && source.prepared_samples < view.target_samples!) {
            status.textContent =
              "This master is shorter than the video. Choose a full-length master or export silently.";
            return;
          }
          if (
            source &&
            source.prepared_samples > view.target_samples! &&
            !trim.control.checked
          ) {
            status.textContent =
              "Confirm the explicit music trim or select an exact-length master.";
            return;
          }
          void change("/exports", {
            expected_revision: episode.revision,
            tracks: source
              ? [
                  {
                    id: "soundtrack",
                    asset: {
                      id: source.asset.id,
                      version: source.asset.version,
                    },
                    start_sample: 0,
                    trim_start_sample: 0,
                    trim_end_sample: view.target_samples!,
                  },
                ]
              : [],
          });
        }),
      );
      body.append(finish);
    } else {
      const attention = section("Progress needs your review", step.message);
      attention.append(
        button(
          "Return to previous accepted clip",
          () =>
            void change("/branch", {
              expected_revision: episode.revision,
              parent_id: (episode.accepted_ids || []).at(-2) || null,
            }),
        ),
      );
      body.append(attention);
    }
    for (const exportItem of view.exports || []) {
      const box = section(
        `Video export · ${exportItem.state}`,
        exportItem.diagnostic || undefined,
      );
      if (exportItem.state === "verified") {
        const url = `/api/v1${path()}/exports/${exportItem.id}/video`;
        box.append(video(url, "Full video · final review pending"));
        const download = element("a", {
          className: "button",
          text: "Download draft MP4",
        });
        download.href = url;
        download.download = `${episode.title}.mp4`;
        box.append(download);
      } else if (["queued", "running"].includes(exportItem.state))
        box.append(
          button(
            "Cancel this export",
            () =>
              void change(`/exports/${exportItem.id}/cancel`, {
                expected_revision: exportItem.revision,
              }),
          ),
        );
      else if (["interrupted", "failed"].includes(exportItem.state))
        box.append(
          button(
            "Resume frozen export",
            () =>
              void change(`/exports/${exportItem.id}/resume`, {
                expected_revision: exportItem.revision,
              }),
          ),
        );
      body.append(box);
    }
    const variation = recipeFields(episode.recipe);
    const title = input(`${episode.title} · variation`);
    body.append(
      details(
        "New variation",
        field("Title", title),
        variation.node,
        button(
          "Start a fresh variation",
          () =>
            void change("/clone", {
              title: title.value,
              recipe: variation.value(),
            }),
        ),
      ),
      details(
        "Remaining routine",
        ...(view.remaining_beats || []).map((b) =>
          element("p", {
            text: `${seconds(b.target_frame)}s · ${b.kind.replaceAll("_", " ")}`,
          }),
        ),
      ),
    );
    if (step.action !== "paused")
      body.append(
        button(
          "Stop and save progress",
          () => void change("/pause", { expected_revision: episode.revision }),
        ),
      );
    if (
      (view.exports || []).some((e) => ["queued", "running"].includes(e.state))
    )
      timer = setTimeout(() => {
        void requests
          .read(() => api(path(), "web_flow"))
          .then((value) => {
            if (value && alive) draw(value);
          })
          .catch(error);
      }, 1500);
  }
  function stateFields(initial: State | undefined) {
    const state = initial || {
      cup_kind: "unknown",
      cup_position: "unknown",
      has_handle: null,
      has_saucer: null,
      hands: "unknown",
      pose: "unknown",
      district: "Tokyo",
      inventory: [],
    };
    const select = (values: string[], value: string) =>
      choice(
        values.map((v) => [v, v.replaceAll("_", " ")]),
        value,
      );
    const cup = select(
      ["unknown", "takeaway", "ceramic", "none"],
      state.cup_kind || "unknown",
    );
    const position = select(
      ["unknown", "table", "held"],
      state.cup_position || "unknown",
    );
    const hands = select(
      ["unknown", "resting", "holding_cup"],
      state.hands || "unknown",
    );
    const pose = select(
      ["unknown", "resting", "watching", "sipping"],
      state.pose || "unknown",
    );
    const handle = choice(
      [
        ["unknown", "Not checked"],
        ["false", "No"],
        ["true", "Yes"],
      ],
      String(state.has_handle ?? "unknown"),
    );
    const saucer = choice(
      [
        ["unknown", "Not checked"],
        ["false", "No"],
        ["true", "Yes"],
      ],
      String(state.has_saucer ?? "unknown"),
    );
    const inventory = input((state.inventory || []).join("; "));
    const district = input(state.district || "Tokyo");
    const node = details(
      "Confirm actual ending state",
      field("Cup type", cup),
      field("Cup position", position),
      field("Cup has a handle", handle),
      field("Saucer present", saucer),
      field("Hands", hands),
      field("Pose", pose),
      field("Outside district", district),
      field("Objects present (semicolons)", inventory),
    );
    node.open = !initial;
    return {
      node,
      value: () => ({
        cup_kind: cup.value,
        cup_position: position.value,
        has_handle: handle.value === "unknown" ? null : handle.value === "true",
        has_saucer: saucer.value === "unknown" ? null : saucer.value === "true",
        hands: hands.value,
        pose: pose.value,
        district: district.value,
        inventory: inventory.value
          .split(";")
          .map((v) => v.trim())
          .filter(Boolean),
      }),
    };
  }
  status.textContent = "Opening saved workflow…";
  void currentProject()
    .then(async (value) => {
      project = value;
      selected =
        sessionStorage.getItem(`tabi-flow-${project.project.id}`) || "";
      await load();
    })
    .catch(() => {
      if (!alive) return;
      status.textContent = "Choose or create a local project to start.";
      fallback = projectsPage();
      body.replaceChildren(fallback.root);
    });
  return {
    root,
    dispose: () => {
      alive = false;
      requests.dispose();
      abort.abort();
      clearTimeout(timer);
      fallback?.dispose();
    },
  };
}
