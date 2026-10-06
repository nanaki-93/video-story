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
import { flowHandoff, FlowRequests } from "./flow-state";

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
function referenceImage(url: string, title: string) {
  const box = section(title);
  const img = element("img", { className: "flow-reference" });
  img.src = url;
  img.alt = title;
  const download = element("a", {
    className: "button",
    text: "Download starting image",
  });
  download.href = url;
  download.download = title;
  box.append(img, download);
  return box;
}
function flowAllowance(recipe: Recipe) {
  const independent =
    !!recipe.shots?.length && recipe.shots.every((s) => s.max_extensions === 0);
  const allowance = input("", "number");
  const start = input("", "number");
  const extension = input("", "number");
  const ceiling = input("70", "number");
  const node = details(
    "Flow allowance",
    element("p", {
      text: "Check your balance and the displayed costs in Flow. These limits guide manual requests; the app cannot enforce spending in Flow.",
    }),
    field("Credits currently remaining", allowance),
    field("Displayed credits for a fresh 8-second shot", start),
    ...(independent
      ? [
          element("p", {
            text: "Every shot starts independently. This plan uses no Flow extensions. More fresh shots can cost more; check the full video budget.",
          }),
        ]
      : [field("Displayed credits for an extension", extension)]),
    field("Maximum credits for this video", ceiling),
  );
  return {
    node,
    value: () => ({
      credit_ceiling: number(ceiling),
      remaining_allowance: number(allowance),
      estimated_start_credit: number(start),
      estimated_credit_per_attempt: number(independent ? start : extension),
      max_retries_per_beat: 1,
      max_attempts: 30,
      allowance_checked_at: new Date().toISOString(),
    }),
  };
}
function recipeFields(recipe: Recipe) {
  const outfit = input(recipe.outfit);
  const setting = input(recipe.setting);
  const exterior = input(recipe.exterior);
  const url = input(recipe.project_url || "", "url");
  const inventory = input((recipe.opening_inventory || []).join("; "));
  const scenes = (recipe.shots || [])
    .filter((shot) => shot.exterior)
    .map((shot) => ({ shot, control: input(shot.exterior || "") }));
  return {
    node: details(
      "Edit settings",
      field("Outfit", outfit),
      field("Interior", setting),
      field("Outside movement", exterior),
      ...scenes.map(({ shot, control }) =>
        field(`Window view · ${shot.title}`, control),
      ),
      field("Opening objects (separate with semicolons)", inventory),
      field("Your Google Flow project link", url),
    ),
    value: (): Recipe => ({
      ...recipe,
      outfit: outfit.value,
      setting: setting.value,
      exterior: exterior.value,
      shots: recipe.shots?.map((shot) => {
        const scene = scenes.find((item) => item.shot.id === shot.id);
        return scene ? { ...shot, exterior: scene.control.value } : shot;
      }),
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
    extra: () => object = () => ({}),
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
            const values = extra();
            const id = await upload(source);
            return api(`${path()}${route}`, "web_flow", {
              ...payload,
              ...values,
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
        "Train · Tokyo · 90 seconds. Twelve independent shots explore six Tokyo districts in two framings each. Generate an 8-second clip from each reviewed image; the app sets a 7.5-second cut. No Flow Extend or matching generated endings. TABI rests and watches; music comes at Finish.",
      );
      const title = input("TABI in Tokyo");
      const allowance = flowAllowance(view.preset);
      const settings = recipeFields(view.preset);
      setup.append(
        field("Video title", title),
        settings.node,
        allowance.node,
        button("Start video", () => {
          try {
            void change(
              base(),
              {
                title: title.value,
                recipe: settings.value(),
                limits: allowance.value(),
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
    const planned = !!episode.recipe.shots?.length;
    const starting = view.reference_slots?.find(
      (r) => r.key === view.starting_reference_key,
    );
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
    for (const label of planned
      ? ["Setup", "References", "Shots", "Finish"]
      : ["Setup", "Opening", "Continue", "Finish"])
      steps.append(element("li", { text: label }));
    body.append(steps);
    if (view.shots?.length) {
      const shots = element("ol", { className: "flow-shots" });
      for (const shot of view.shots) {
        const item = element("li", { className: `flow-shot-${shot.state}` });
        if (shot.state === "current") item.setAttribute("aria-current", "step");
        item.append(
          element("strong", {
            text: `${seconds(shot.start_frame)}–${seconds(shot.start_frame + shot.duration_frames)}s · ${shot.framing}`,
          }),
          element("span", { text: shot.title }),
          element("small", {
            text: `${seconds(shot.accepted_frames)} / ${seconds(shot.duration_frames)}s reviewed`,
          }),
        );
        shots.append(item);
      }
      body.append(shots);
    }
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
    if (step.action === "choose_reference") {
      const slot = view.reference_slots?.find(
        (r) => r.key === view.next_reference_key,
      );
      if (slot) {
        const shot = episode.recipe.shots?.find(
          (item) => item.reference_key === slot.key,
        );
        const title = shot?.title || slot.framing;
        const preparation = section(
          `2 · Prepare reference: ${title}`,
          `Use your approved train image in Flow to prepare this ${slot.framing} view. Review all ${view.reference_slots?.length || 0} starting images before generating video.`,
        );
        const instructions = element("textarea");
        instructions.value = slot.instruction;
        instructions.rows = 6;
        instructions.readOnly = true;
        instructions.setAttribute("aria-label", "Reference preparation prompt");
        const facts = stateFields(undefined, "Confirm visible starting facts");
        const clean = checkbox(
          "I checked the whole image: TABI, gills, connected neck, outfit and objects are correct; the air is clear" +
            (shot?.exterior
              ? "; the planned scenery is visible outside the window with correct perspective"
              : ""),
        );
        preparation.append(
          instructions,
          button("Copy reference prompt", () => {
            void navigator.clipboard
              .writeText(slot.instruction)
              .then(() => {
                status.textContent =
                  "Reference prompt copied. Attach your approved train image in Flow.";
              })
              .catch(error);
          }),
        );
        const master = view.reference_slots?.find((r) => r.url);
        if (master?.url)
          preparation.append(
            referenceImage(
              master.url,
              "Approved camera reference for this journey",
            ),
          );
        preparation.append(
          facts.node,
          clean.node,
          importControl(
            `Import reference: ${title}`,
            "image/png,image/jpeg,image/webp",
            "/reference",
            {
              expected_revision: episode.revision,
              key: slot.key,
              title: `${episode.title} · ${title}`,
            },
            () => {
              if (!clean.control.checked)
                throw new Error(
                  "Review the image and confirm its starting facts before importing.",
                );
              return {
                starting_state: facts.value(),
                review_note:
                  "Starting image, visible facts, character, gills and props reviewed; air is clear" +
                  (shot?.exterior
                    ? "; assigned window scenery and perspective reviewed"
                    : ""),
              };
            },
          ),
        );
        body.append(preparation);
      } else
        body.append(
          importControl(
            "Import TABI reference",
            "image/png,image/jpeg,image/webp",
            "/reference",
            { expected_revision: episode.revision },
          ),
        );
    } else if (step.action === "prepare")
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
      const guide = flowHandoff(attempt.mode);
      const handoff = section(`3 · ${guide.title}`, guide.instruction);
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
              status.textContent = guide.instruction;
            })
            .catch(error);
        }),
        link,
      );
      if (guide.useReference) {
        const url = starting?.url || view.reference_urls?.[0];
        if (url)
          handoff.append(
            referenceImage(
              url,
              `${starting?.framing || "Opening"} starting reference`,
            ),
          );
      }
      if (view.parent_url && guide.extendParent)
        handoff.append(
          video(view.parent_url, "Accepted parent · extend this clip"),
        );
      else if (view.parent_url)
        handoff.append(
          details(
            "Previous shot · review the camera cut",
            video(view.parent_url, "Editorial predecessor"),
          ),
        );
      const providerModel = input("");
      handoff.append(
        field("Model shown in Flow (for release evidence)", providerModel),
      );
      handoff.append(
        importControl(
          "Import Flow result",
          "video/mp4",
          "/import",
          {
            expected_revision: episode.revision,
            attempt_id: attempt.id,
          },
          () => ({ provider_model: providerModel.value || null }),
        ),
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
      const attempt = (episode.attempts || []).find(
        (a) => a.id === candidate.attempt_id,
      )!;
      const guide = flowHandoff(attempt.mode);
      const review = section(
        "Review this clip",
        "Watch the whole clip and its ending. Check TABI, objects, outside motion and the requested action before accepting.",
      );
      if (view.candidate_url)
        review.append(video(view.candidate_url, "Selected clip section"));
      const startFrame = input(String(candidate.trim.start_frame), "number");
      const endFrame = input(String(candidate.trim.end_frame), "number");
      startFrame.min = "0";
      startFrame.max = String(candidate.frame_count - 1);
      endFrame.min = "1";
      endFrame.max = String(candidate.frame_count);
      startFrame.step = endFrame.step = "1";
      const selection = details(
        "Keep a section of this clip",
        element("p", {
          text: `Selected source frames ${candidate.trim.start_frame}–${candidate.trim.end_frame} · ${seconds(candidate.trim.start_frame)}–${seconds(candidate.trim.end_frame)}s. Source: ${candidate.frame_count} frames. The end frame is excluded.`,
        }),
        element("p", {
          text: "The whole clip is selected by default. Adjust these only to exclude an unwanted opening or ending, then watch the rebuilt section and join. Original files stay unchanged.",
        }),
        field("Start at source frame", startFrame),
        field("End before source frame", endFrame),
        button("Use this section", () => {
          try {
            void change(`/clips/${candidate.id}/section`, {
              expected_revision: episode.revision,
              media_sha256: candidate.media.sha256,
              trim: {
                start_frame: number(startFrame),
                end_frame: number(endFrame),
              },
            });
          } catch (e) {
            status.textContent = String(e);
          }
        }),
      );
      if (view.candidate_source_url)
        selection.append(
          video(view.candidate_source_url, "Original complete clip"),
        );
      review.append(selection);
      if (view.review?.join_url)
        review.append(
          video(
            view.review.join_url,
            attempt.mode === "shot_start"
              ? "Camera cut · previous shot to clean new shot"
              : "Continuous join with accepted parent",
          ),
        );
      const frames = element("div", { className: "flow-filmstrip" });
      for (const img of view.review?.images || []) {
        const image = element("img");
        image.src = img.url;
        image.alt = `${img.role} frame ${img.frame}`;
        frames.append(image);
      }
      review.append(frames);
      const facts = stateFields(
        (attempt.mode === "shot_start"
          ? starting?.starting_state
          : parent?.observed_state) || undefined,
      );
      const checked = checkbox(
        "I watched the clip and join; the action finishes and continuity is good",
      );
      for (const control of [startFrame, endFrame])
        control.addEventListener("input", () => {
          checked.control.checked = false;
          if (cut) cut.control.checked = false;
        });
      const cut =
        view.safe_cut_frame != null
          ? checkbox(
              `I checked the ${planned ? "shot ending" : "final cut"} at clip frame ${view.safe_cut_frame}: the action is complete and TABI is settled`,
            )
          : undefined;
      const note = input("");
      const correction = choice([
        ["particles", "Floating dots / particles"],
        ["mouth", "Mouth"],
        ["identity", "Character / gills / outfit"],
        ["props", "Objects / hands"],
        ["motion", "Outside motion / freeze"],
        ["action", "Action incomplete"],
      ]);
      review.append(
        facts.node,
        field("Review note / reason for retry", note),
        field("One correction for a retry", correction),
        checked.node,
      );
      if (cut) review.append(cut.node);
      review.append(
        button("Accept clip", () => {
          if (
            startFrame.value !== String(candidate.trim.start_frame) ||
            endFrame.value !== String(candidate.trim.end_frame)
          ) {
            status.textContent =
              "Use this section and watch its rebuilt review before accepting.";
            return;
          }
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
        button(guide.retry, () => {
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
            retry_focus: correction.value,
          });
        }),
      );
      if (view.review)
        review.append(
          details(
            "What to check",
            ...view.review.checklist.map((text) => element("p", { text })),
          ),
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
      if (step.next_retry_limit != null)
        attention.append(
          element("p", {
            text: "Keep the accepted footage and allow another correction. Your credit ceiling stays unchanged; this does not start a generation.",
          }),
          button(
            `Raise retry limit to ${step.next_retry_limit} per action`,
            () =>
              void change("/increase-retry-limit", {
                expected_revision: episode.revision,
              }),
          ),
        );
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
    if (step.restart_shot_id)
      body.append(
        details(
          "Start this shot again",
          element("p", {
            text: "Keep earlier completed shots and restart this partial shot from its clean image. All previous takes stay in history. Credit and retry limits remain unchanged.",
          }),
          button(
            "Restart this shot from its clean image",
            () =>
              void change("/restart-shot", {
                expected_revision: episode.revision,
              }),
          ),
        ),
      );
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
        box.append(
          download,
          button("Prepare YouTube delivery", () => {
            if (requests.busy) return;
            status.textContent = "Opening delivery review…";
            void requests
              .change(async () => {
                const list = await api(
                  `${prefix(project)}/releases`,
                  "web_releases",
                );
                const id = `flow-release-${exportItem.id}`;
                if (!list.preparations.some((p) => p.id === id))
                  await api(
                    `${prefix(project)}/releases`,
                    "release_preparation",
                    {
                      preparation: {
                        schema_version: "1.0",
                        document_type: "release_preparation",
                        id,
                        revision: 0,
                        source_kind: "flow",
                        job_id: exportItem.id,
                        title: episode.title,
                      },
                      expected_revision: null,
                    },
                  );
                sessionStorage.setItem("tabi-release", id);
                location.hash = "release";
                return view;
              })
              .catch(error);
          }),
        );
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
    const variationAllowance = flowAllowance(episode.recipe);
    const title = input(`${episode.title} · variation`);
    body.append(
      details(
        "New variation",
        field("Title", title),
        variation.node,
        element("p", {
          text: "Changing one window view keeps the other reviewed images. Outfit or interior changes require new references. Check the Flow balance and costs for this new run.",
        }),
        variationAllowance.node,
        button("Start a fresh variation", () => {
          try {
            void change("/clone", {
              title: title.value,
              recipe: variation.value(),
              limits: variationAllowance.value(),
            });
          } catch {
            status.textContent =
              "Enter the current Flow balance and displayed costs for this variation.";
          }
        }),
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
    if (
      !episode.recipe.shots?.length ||
      episode.recipe.shots.some((s) => s.max_extensions! > 0)
    ) {
      const current = recipeFields({
        ...view.preset,
        identity: episode.recipe.identity,
        outfit: episode.recipe.outfit,
        setting: episode.recipe.setting,
        camera: episode.recipe.camera,
        exterior: episode.recipe.exterior,
        opening_inventory: episode.recipe.opening_inventory,
        project_url: episode.recipe.project_url,
      });
      const costs = flowAllowance(view.preset);
      const name = input(`${episode.title} · independent shots`);
      body.append(
        details(
          "New Tokyo video without Flow extensions",
          element("p", {
            text: "Use the current twelve-shot plan with fixed camera cuts. Matching reviewed references are reused; additional framings and districts need their own images. The saved video keeps its existing plan.",
          }),
          field("Video title", name),
          current.node,
          costs.node,
          button("Create independent-shot variation", () => {
            try {
              void change("/clone", {
                title: name.value,
                recipe: current.value(),
                limits: costs.value(),
              });
            } catch {
              status.textContent =
                "Enter the current Flow balance and fresh-shot cost for this variation.";
            }
          }),
        ),
      );
    }
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
  function stateFields(
    initial: State | undefined,
    title = "Confirm actual ending state",
  ) {
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
      title,
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
