import { api } from "./session";
import type { Documents } from "./contracts";
import { button, element, field, section } from "./dom";
import {
  actionForm,
  choice,
  folderChooser,
  input,
  jsonEditor,
  prefix,
  projectPage,
  refreshPage,
  remember,
} from "./workspace";

export function releasePage() {
  return projectPage(async (root, project, catalog, active) => {
    const base = prefix(project);
    const [saved, jobs] = await Promise.all([
      api(`${base}/releases`, "web_releases"),
      api(`${base}/jobs`, "web_jobs"),
    ]);
    if (!active()) return;
    const verified = jobs.jobs.filter((j) => j.state === "verified");
    const flow = saved.flow_exports || [];
    const select = choice(
      [
        ["", "New release preparation"],
        ...saved.preparations.map((p) => [p.id, p.title] as [string, string]),
      ],
      sessionStorage.getItem("tabi-release") || "",
    );
    const editor = section(
      "Release preparation",
      "Prepare local files for manual publishing. Saved URLs and claim notes are factual records; the app does not check platform status or upload anything.",
    );
    const content = element("div");
    root.append(editor);
    editor.append(field("Preparation", select), content);
    let generation = 0;
    function show() {
      const visit = ++generation;
      const current = () => active() && visit === generation;
      const prep = saved.preparations.find((p) => p.id === select.value);
      let dirty = !prep;
      let inspection: Documents["release_inspection"] | undefined;
      const identity = input(prep?.id || `release-${Date.now()}`);
      identity.disabled = !!prep;
      const job = choice(
        [
          ...flow.map(
            (e) =>
              [
                `flow:${e.id}`,
                `Flow video · ${e.inputs.duration_frames} verified frames`,
              ] as [string, string],
          ),
          ...verified.map(
            (j) =>
              [
                `layered:${j.id}`,
                `${j.destination} · ${j.completed_frames} verified frames`,
              ] as [string, string],
          ),
        ],
        prep ? `${prep.source_kind || "layered"}:${prep.job_id}` : undefined,
      );
      const title = input(prep?.title || "Untitled release");
      const description = element("textarea");
      description.rows = 5;
      description.value = prep?.description || "";
      const disclosure = element("textarea");
      disclosure.rows = 3;
      disclosure.value = prep?.disclosure_notes || "";
      const chapters = jsonEditor(prep?.chapters || []);
      const thumbnail = choice(
        [
          ["", "No approved thumbnail selected"],
          ...catalog.assets
            .filter(
              (a) => a.kind === "still" && a.approval?.status === "approved",
            )
            .map(
              (a) =>
                [`${a.id}@${a.version}`, `${a.id} @ ${a.version}`] as [
                  string,
                  string,
                ],
            ),
        ],
        prep?.thumbnail ? `${prep.thumbnail.id}@${prep.thumbnail.version}` : "",
      );
      const links = jsonEditor(prep?.manual_links || []);
      const claims = element("textarea");
      claims.rows = 3;
      claims.value = prep?.claim_notes || "";
      const concept = input(prep?.concept_notes || "");
      const models = input(
        (prep?.flow_terms?.provider_models || []).join("; "),
      );
      const termsReviewer = input(prep?.flow_terms?.reviewer || "");
      const termsNote = input(prep?.flow_terms?.note || "");
      const termsLinks = element("textarea");
      termsLinks.value = (
        prep?.flow_terms?.source_links || [
          "https://support.google.com/flow/answer/16353333?hl=en",
          "https://policies.google.com/terms",
        ]
      ).join("\n");
      const termsChecked = input("", "checkbox");
      termsChecked.checked = prep?.flow_terms?.commercial_use === "confirmed";
      const terms = element("details");
      terms.append(
        element("summary", { text: "Flow commercial-use review" }),
        element("p", {
          text: "Review current official terms for the exact models used and your existing entitlement. This records your review; the app does not grant rights or YouTube monetization.",
        }),
        field("Models actually used (semicolons)", models),
        field("Official sources (one Google link per line)", termsLinks),
        field("Terms reviewer", termsReviewer),
        field("Terms review note", termsNote),
        field("I checked commercial-use permission today", termsChecked),
      );
      const outcome = element("div");
      const fields = [
        identity,
        job,
        title,
        description,
        disclosure,
        chapters,
        thumbnail,
        links,
        claims,
        concept,
        models,
        termsReviewer,
        termsNote,
        termsLinks,
        termsChecked,
      ];
      for (const item of fields)
        item.addEventListener("input", () => {
          dirty = true;
          inspection = undefined;
          outcome.replaceChildren(
            element("p", {
              text: "Unsaved metadata. Save and inspect before reviewing or exporting.",
            }),
          );
        });
      const edit = actionForm(
        "Save release draft",
        [
          field("Episode concept / what makes this video distinct", concept),
          field("Verified video", job),
          field("Public title", title),
          field("Public description", description),
          field("Public disclosure notes", disclosure),
          terms,
          field("Approved thumbnail", thumbnail),
        ],
        async () => {
          if (!job.value) throw new Error("Render and verify a video first.");
          content.inert = true;
          try {
            const selected = catalog.assets.find(
              (a) => `${a.id}@${a.version}` === thumbnail.value,
            );
            const result = await api(
              `${base}/releases`,
              "release_preparation",
              {
                preparation: {
                  ...(prep || {
                    schema_version: "1.0",
                    document_type: "release_preparation",
                    revision: 0,
                  }),
                  id: identity.value,
                  job_id: job.value.split(":")[1],
                  source_kind: job.value.split(":")[0],
                  concept_notes: concept.value,
                  flow_terms:
                    job.value.startsWith("flow:") &&
                    models.value.trim() &&
                    termsReviewer.value.trim() &&
                    termsNote.value.trim()
                      ? {
                          provider_models: models.value
                            .split(";")
                            .map((v) => v.trim())
                            .filter(Boolean),
                          commercial_use: termsChecked.checked
                            ? "confirmed"
                            : "pending",
                          reviewed_at: new Date().toISOString(),
                          reviewer: termsReviewer.value,
                          note: termsNote.value,
                          source_links: termsLinks.value
                            .split("\n")
                            .map((v) => v.trim())
                            .filter(Boolean),
                        }
                      : null,
                  title: title.value,
                  description: description.value,
                  disclosure_notes: disclosure.value,
                  chapters: JSON.parse(chapters.value) as unknown,
                  thumbnail: selected
                    ? { id: selected.id, version: selected.version }
                    : null,
                  manual_links: JSON.parse(links.value) as unknown,
                  claim_notes: claims.value,
                },
                expected_revision: prep?.revision ?? null,
              },
            );
            sessionStorage.setItem("tabi-release", result.id);
            if (current()) refreshPage();
          } finally {
            content.inert = false;
          }
        },
      );
      const review = section(
        "Checklist and bundle preview",
        "Inspect the saved draft to decode the export and check media hashes, rights, music metadata, thumbnail and disclosure review.",
      );
      review.append(
        actionForm("Inspect saved release", [], async () => {
          if (dirty || !prep)
            throw new Error("Save the release draft before inspecting it.");
          const result = await api(
            `${base}/releases/${prep.id}/inspect`,
            "release_inspection",
            {},
          );
          if (!current() || dirty)
            return "Metadata changed. Save and inspect again.";
          inspection = result;
          outcome.replaceChildren(
            element("p", {
              className: "notice",
              text: `${result.status} · ${result.blockers.length} unresolved checks`,
            }),
            element("pre", {
              text:
                [...result.blockers, ...result.warnings].join("\n") ||
                "No unresolved checks recorded.",
            }),
            element("p", {
              text: "Public bundle: video, title, description, track list, disclosure notes, metadata, rights summary and README. Valid chapters and an approved thumbnail are included when available. Private evidence stays in a separate folder.",
            }),
          );
          const details = element("details");
          details.append(
            element("summary", {
              text: "Inspect exact public metadata and hashes",
            }),
            element("pre", { text: JSON.stringify(result.public, null, 2) }),
          );
          outcome.append(details);
          return "Technical verification complete. Review the unresolved checks above.";
        }),
        outcome,
      );
      const reviewer = input(""),
        note = input("");
      const kind = choice([
        ["metadata", "I reviewed the public metadata and disclosure"],
        ["creative", "I watched and heard the production export"],
      ]);
      const reviews = element("details");
      reviews.append(
        element("summary", { text: "Record my content review" }),
        actionForm(
          "Record this review",
          [
            field("Review", kind),
            field("Reviewer", reviewer),
            field("Review note", note),
          ],
          async () => {
            if (dirty || !prep || !inspection)
              throw new Error("Save and inspect the current content first.");
            const result = await api(
              `${base}/releases/${prep.id}/review`,
              "release_preparation",
              {
                kind: kind.value,
                expected_revision: prep.revision,
                expected_hash:
                  kind.value === "creative"
                    ? inspection.public.video_sha256
                    : inspection.metadata_sha256,
                reviewer: reviewer.value,
                note: note.value,
              },
            );
            sessionStorage.setItem("tabi-release", result.id);
            if (current()) refreshPage();
          },
        ),
      );
      const bundle = input(`release-${Date.now()}`),
        readiness = choice([
          ["draft", "Export a draft with unresolved checks"],
          ["ready", "Require ready for manual upload"],
        ]);
      const exported = element("div");
      review.append(
        reviews,
        actionForm(
          "Export local release folder",
          [field("New bundle ID", bundle), field("Readiness", readiness)],
          async () => {
            if (dirty || !prep || !inspection)
              throw new Error("Save and inspect before exporting.");
            const report = await api(
              `${base}/releases/${prep.id}/export`,
              "release_bundle_report",
              {
                bundle_id: bundle.value,
                require_ready: readiness.value === "ready",
              },
            );
            if (!current()) return;
            exported.replaceChildren(
              element("p", {
                text: `Saved ${project.path}/${report.bundle_path}. Status: ${report.inspection.status}. Only public/ is prepared for manual sharing.`,
              }),
            );
            const files = element("ul");
            report.files.forEach((f, index) => {
              if (!f.location.path.startsWith(`${report.bundle_path}/public/`))
                return;
              const row = element("li"),
                link = element("a", { text: f.location.path.split("/").pop() });
              link.href = `/api/v1${base}/bundles/${report.bundle_path.split("/")[1]}/files/${index}`;
              link.target = "_blank";
              link.rel = "noopener";
              row.append(link);
              files.append(row);
            });
            exported.append(files);
            return "Bundle copied and verified. No platform upload was performed.";
          },
        ),
        exported,
      );
      const advanced = element("details");
      advanced.append(
        element("summary", { text: "Advanced metadata" }),
        field("Preparation ID", identity),
        field("Chapters (JSON)", chapters),
        field("Manual URLs (JSON)", links),
        field("Private claim notes", claims),
      );
      edit.append(advanced);
      if (!verified.length && !flow.length)
        content.replaceChildren(
          element("p", {
            text: "No verified video yet. Finish a render before preparing a release.",
          }),
          button("Open Renders", () => {
            location.hash = "renders";
          }),
        );
      else content.replaceChildren(edit, review);
    }
    select.addEventListener("change", () => {
      sessionStorage.setItem("tabi-release", select.value);
      show();
    });
    show();

    const backup = section(
      "Private project backup and restore",
      "Backups contain source media, private rights evidence, edits, snapshots, previews and exports. Keep the complete folder private. Pause or finish jobs first; files are checked before the new folder is published.",
    );
    const backupDetails = element("details");
    backupDetails.append(
      element("summary", { text: "Advanced: private project backup" }),
      backup,
    );
    root.append(backupDetails);
    let targetRoot = "",
      parent = "";
    const chooser = await folderChooser((id, path) => {
      targetRoot = id;
      parent = path;
    });
    if (!active()) return;
    const name = input(`tabi-backup-${Date.now()}`),
      output = element("pre");
    const source = input(""),
      restored = input(`tabi-restored-${Date.now()}`);
    chooser.append(
      actionForm(
        "Create private backup here",
        [field("New backup folder", name)],
        async () => {
          chooser.inert = true;
          try {
            const result = await api(`${base}/backup`, "web_backup", {
              root_id: targetRoot,
              parent,
              folder: name.value,
            });
            if (!active()) return;
            source.value = result.path;
            output.textContent = `Verified ${result.manifest.files.length} files, ${result.manifest.total_bytes} bytes at ${result.root_id}/${result.path}\n${(result.manifest.warnings || []).join("\n")}`;
            return "Private backup saved. Sources and approved documents were preserved.";
          } finally {
            chooser.inert = false;
          }
        },
      ),
      actionForm(
        "Restore backup into a new folder",
        [
          field("Backup path relative to the selected registered root", source),
          field("New restored project folder", restored),
        ],
        async () => {
          chooser.inert = true;
          try {
            const result = await api("/backups/restore", "web_project", {
              source_root_id: targetRoot,
              source_path: source.value,
              root_id: targetRoot,
              parent,
              folder: restored.value,
            });
            remember(result);
            if (active()) refreshPage();
          } finally {
            chooser.inert = false;
          }
        },
      ),
      output,
    );
    backup.append(
      chooser,
      element("p", {
        className: "muted",
        text: "To reconnect a moved project instead of restoring a backup, use Projects → Relink. The existing project ID is checked before opening it.",
      }),
    );
  });
}
