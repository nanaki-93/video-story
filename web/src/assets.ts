import { api, request } from "./session";
import { document as checked } from "./contracts";
import type { Documents } from "./contracts";
import { button, element, field, section } from "./dom";
import {
  actionForm,
  choice,
  input,
  jsonEditor,
  number,
  prefix,
  projectPage,
  refreshPage,
} from "./workspace";

let inspecting = sessionStorage.getItem("tabi-asset") || "";
function selectAsset(id: string) {
  inspecting = id;
  sessionStorage.setItem("tabi-asset", id);
}
function provenanceForm(initial?: Documents["asset"]["provenance"]) {
  const origin = choice(
    [
      ["unknown", "Unknown"],
      ["user_supplied", "User supplied"],
      ["synthetic", "Synthetic test asset"],
      ["generated", "Generated — record workflow below"],
    ],
    initial?.origin || "unknown",
  );
  const creator = input(initial?.creator || "");
  const rights = choice(
    [
      ["pending", "Rights pending"],
      ["confirmed", "Commercial use confirmed by me"],
      ["not-permitted", "Commercial use not permitted"],
    ],
    initial?.commercial_use || "pending",
  );
  const notes = input(initial?.notes || "");
  const evidence = jsonEditor(initial?.licence_evidence || []);
  const generation = jsonEditor(initial?.generation || null);
  const nodes = [
    field("Origin", origin),
    field("Creator (if known)", creator),
    field("Commercial rights", rights),
    field("Provenance notes", notes),
    field("Licence evidence paths (JSON; registered root IDs)", evidence),
    field("Generation record (JSON or null; factual values only)", generation),
  ];
  return {
    nodes,
    value: () => ({
      origin: origin.value,
      creator: creator.value || null,
      commercial_use: rights.value,
      notes: notes.value || null,
      reference_ids: initial?.reference_ids || [],
      licence_evidence: JSON.parse(evidence.value),
      generation: JSON.parse(generation.value),
    }),
  };
}

export function assetsPage() {
  let cancel: AbortController | undefined;
  const panel = projectPage((root, project, catalog) => {
    const base = prefix(project);
    const library = section(
      "Asset library",
      "Versions and approvals refer to exact content hashes. Synthetic media cannot be production approved.",
    );
    const filter = choice([
      ["", "All types"],
      ...["still", "mask", "sequence", "video", "audio", "font"].map(
        (v): [string, string] => [v, v],
      ),
    ]);
    const list = element("div", { className: "asset-grid" });
    function draw() {
      list.replaceChildren();
      for (const asset of catalog.assets.filter(
        (a) => !filter.value || a.kind === filter.value,
      )) {
        const card = section(
          `${asset.id} · ${asset.version}`,
          `${asset.kind} · ${asset.approval?.status || "draft"} · rights ${asset.provenance?.commercial_use || "pending"}`,
        );
        if (["still", "mask", "sequence"].includes(asset.kind)) {
          const img = element("img", { className: "asset-thumb checker" });
          img.alt = `${asset.id} ${asset.kind} preview`;
          img.loading = "lazy";
          img.src = `/api/v1${base}/assets/${asset.id}/${asset.version}/media${asset.proxies?.length || 0 ? "?proxy=true" : ""}`;
          card.append(img);
        }
        card.append(
          element("p", {
            text: `${asset.provenance?.origin || "unknown"} · ${asset.files.length} source files`,
            className: "muted",
          }),
          button("Inspect asset", () => {
            selectAsset(`${asset.id}@${asset.version}`);
            location.hash = "inspector";
          }),
        );
        list.append(card);
      }
      if (!list.children.length)
        list.append(
          element("p", {
            text: "No assets of this type. Import local files below.",
          }),
        );
    }
    filter.addEventListener("change", draw);
    library.append(field("Filter assets", filter), list);
    draw();
    root.append(library);
    const importing = section(
      "Import media",
      "Files are copied to this Mac in 4 MiB chunks. Choose the same files again to resume an interrupted import; verified source copies remain untouched.",
    );
    const id = input(""),
      version = input("1.0"),
      kind = choice(
        ["still", "mask", "sequence", "video", "audio", "font"].map((v) => [
          v,
          v,
        ]),
      );
    const files = input("", "file");
    files.multiple = true;
    const order = element("p", { className: "mono" });
    let selected: File[] = [];
    function chooseMedia(values: File[]) {
      selected = values;
      order.textContent = values
        .map((f) => `${f.name} (${f.size} bytes)`)
        .join(" → ");
    }
    files.addEventListener("change", () =>
      chooseMedia(Array.from(files.files || [])),
    );
    const drop = element("div", {
      className: "drop-zone",
      text: "Drop files here, or use Choose files. Sequence order follows the displayed filenames.",
    });
    drop.addEventListener("dragover", (e) => {
      e.preventDefault();
    });
    drop.addEventListener("drop", (e) => {
      e.preventDefault();
      chooseMedia(
        Array.from(e.dataTransfer?.files || []).sort((a, b) =>
          a.name.localeCompare(b.name),
        ),
      );
    });
    const fpsNum = input("30", "number"),
      fpsDen = input("1", "number");
    const provenance = provenanceForm();
    const progress = element("p", { className: "notice" });
    progress.setAttribute("role", "status");
    const uploadKey = `tabi-uploads-${project.project.id}`;
    type Saved = { id: string; name: string; size: number; modified: number };
    let saved: Saved[] = [];
    try {
      const value = JSON.parse(localStorage.getItem(uploadKey) || "[]");
      if (Array.isArray(value)) saved = value;
    } catch {
      /* disposable upload preferences */
    }
    if (saved.length)
      progress.textContent = `${saved.length} staged file(s). Reselect them to resume, or discard staging.`;
    const stash = () => localStorage.setItem(uploadKey, JSON.stringify(saved));
    importing.append(
      actionForm(
        "Copy and import selected files",
        [
          field("Asset ID", id),
          field("New immutable version", version),
          field("Media type", kind),
          field("Selected files", files),
          drop,
          order,
          field("Sequence/video fps numerator", fpsNum),
          field("Sequence/video fps denominator", fpsDen),
          ...provenance.nodes,
        ],
        async () => {
          if (!selected.length)
            throw new Error("Select one or more media files first.");
          cancel = new AbortController();
          const ids: string[] = [];
          for (const file of selected) {
            let found = saved.find(
              (s) =>
                s.name === file.name &&
                s.size === file.size &&
                s.modified === file.lastModified,
            );
            if (!found) {
              const upload = await api(`${base}/uploads`, "web_upload", {
                name: file.name,
                size_bytes: file.size,
              });
              found = {
                id: upload.id,
                name: file.name,
                size: file.size,
                modified: file.lastModified,
              };
              saved.push(found);
              stash();
            }
            // Replay acknowledged chunks too: the worker checks actual bytes, not just filename/size.
            for (let offset = 0; offset < file.size; offset += 4 * 1024 ** 2) {
              const result = checked(
                "web_upload",
                await request(
                  `${base}/uploads/${found.id}/chunk?offset=${offset}`,
                  file.slice(offset, offset + 4 * 1024 ** 2),
                  "PUT",
                  cancel.signal,
                ),
              );
              progress.textContent = `${file.name}: ${result.received_bytes}/${result.size_bytes} bytes checked`;
            }
            await api(`${base}/uploads/${found.id}/finish`, "web_upload", {});
            ids.push(found.id);
          }
          const asset = await api(`${base}/uploads/import`, "asset", {
            uploads: ids,
            request: {
              id: id.value,
              version: version.value,
              kind: kind.value,
              fps: ["sequence", "video"].includes(kind.value)
                ? { num: number(fpsNum), den: number(fpsDen) }
                : null,
              provenance: provenance.value(),
            },
          });
          for (const identity of ids) {
            await api(`${base}/uploads/${identity}/discard`, "web_upload", {});
            saved = saved.filter((s) => s.id !== identity);
            stash();
          }
          selectAsset(`${asset.id}@${asset.version}`);
          cancel = undefined;
          location.hash = "inspector";
        },
      ),
      progress,
      button("Interrupt upload", () => {
        cancel?.abort();
        progress.textContent =
          "Upload interrupted. Select the same files and submit again to resume.";
      }),
      actionForm("Discard staged uploads", [], async () => {
        cancel?.abort();
        for (const upload of saved)
          await api(`${base}/uploads/${upload.id}/discard`, "web_upload", {});
        saved = [];
        stash();
        return "Only upload staging was removed. Imported source copies are preserved.";
      }),
    );
    root.append(importing);
    const advanced = section(
      "Import authored metadata",
      "Paste a versioned scene_template, action_pack, episode or release_record document. Unknown fields and asserted approvals are rejected.",
    );
    const data = jsonEditor({
      schema_version: "1.0",
      document_type: "scene_template",
    });
    advanced.append(
      actionForm(
        "Import new document",
        [field("Document JSON", data)],
        async () => {
          await request(`${base}/documents`, {
            document: JSON.parse(data.value),
            expected_revision: null,
          });
          return "Document saved. Reopen this page or New episode to use it.";
        },
      ),
    );
    const links = section(
      "Link existing files",
      "Select paths inside registered folders. Linked files must stay available; edits invalidate their content hashes. Use ordered paths for a sequence.",
    );
    const link = jsonEditor({
      id: "",
      version: "1.0",
      kind: "audio",
      paths: [{ root_id: project.root_id, path: "" }],
      mode: "link",
      provenance: { origin: "unknown", commercial_use: "pending" },
    });
    links.append(
      actionForm(
        "Import registered paths",
        [field("Import request JSON", link)],
        async () => {
          const result = await api(
            `${base}/assets/import`,
            "asset",
            JSON.parse(link.value),
          );
          selectAsset(`${result.id}@${result.version}`);
          location.hash = "inspector";
        },
      ),
    );
    const details = element("details");
    details.append(
      element("summary", { text: "Templates, action packs and linked media" }),
      advanced,
      links,
    );
    root.append(details);
  });
  return {
    ...panel,
    dispose: () => {
      cancel?.abort();
      panel.dispose();
    },
  };
}

export function inspectorPage() {
  return projectPage(async (root, project, catalog, active) => {
    if (!catalog.assets.length) {
      root.append(
        section("No assets", "Import media on the Assets page first."),
      );
      return;
    }
    if (!catalog.assets.some((a) => `${a.id}@${a.version}` === inspecting))
      selectAsset(`${catalog.assets[0].id}@${catalog.assets[0].version}`);
    const selector = choice(
      catalog.assets.map((a) => [
        `${a.id}@${a.version}`,
        `${a.id} ${a.version} · ${a.approval?.status || "draft"}`,
      ]),
      inspecting,
    );
    selector.addEventListener("change", () => {
      selectAsset(selector.value);
      refreshPage();
    });
    root.append(field("Inspect version", selector));
    const asset = catalog.assets.find(
      (a) => `${a.id}@${a.version}` === inspecting,
    )!;
    const base = `${prefix(project)}/assets/${asset.id}/${asset.version}`;
    const visual = section(
      asset.id,
      `${asset.kind} · version ${asset.version} · ${asset.approval?.status || "draft"} · ${asset.provenance?.origin || "unknown"} · rights ${asset.provenance?.commercial_use || "pending"}`,
    );
    if (["still", "mask", "sequence"].includes(asset.kind)) {
      const image = element("img", { className: "asset-full checker" });
      image.alt = `${asset.id} source inspection`;
      const index = input("0", "number");
      index.min = "0";
      index.max = String(asset.files.length - 1);
      const proxy = input("", "checkbox");
      proxy.disabled = !(asset.proxies?.length || 0);
      const alpha = input("", "checkbox");
      alpha.checked = true;
      const show = () => {
        image.src = `/api/v1${base}/media?index=${number(index)}&proxy=${proxy.checked}`;
        image.classList.toggle("checker", alpha.checked);
      };
      for (const control of [index, proxy, alpha])
        control.addEventListener("change", show);
      show();
      visual.append(
        image,
        field("Source frame index", index),
        field("Show proxy", proxy),
        field("Alpha checkerboard", alpha),
      );
    } else if (["audio", "video"].includes(asset.kind)) {
      const media = element(asset.kind === "audio" ? "audio" : "video");
      media.controls = true;
      media.preload = "metadata";
      media.src = `/api/v1${base}/media`;
      visual.append(media);
    }
    const facts = element("details");
    facts.append(
      element("summary", {
        text: "Source, probe, pivots, masks and compatibility",
      }),
      element("pre", {
        text: JSON.stringify(
          {
            source: asset.source,
            files: asset.files,
            probe: asset.probe,
            compatibility: asset.compatibility,
            provenance: asset.provenance,
          },
          null,
          2,
        ),
      }),
    );
    visual.append(facts);
    root.append(visual);
    const health = await api(`${base}/health`, "asset_health");
    if (!active()) return;
    root.append(
      element("p", {
        className: "notice",
        text: `Media ${health.media_valid ? "verified" : "missing or changed"} · approval ${health.approval_valid ? "valid" : "not approved"} · rights ${health.rights} · publication ${health.publication_ready ? "ready" : "not ready"}`,
      }),
    );
    for (const file of health.files.filter((f) => f.status !== "ok"))
      root.append(
        element("p", {
          className: "state error",
          text: `${file.location.path}: ${file.status}. Relink matching bytes below, or import changed media as a new version.`,
        }),
      );
    const next = `${asset.version.split(".")[0]}.${Number(asset.version.split(".")[1]) + 1}`;
    const revision = section(
      "Create a new version",
      "The existing version and any approval stay immutable. A new version begins as draft.",
    );
    const version = input(next),
      provenance = provenanceForm(asset.provenance),
      compatibility = jsonEditor(asset.compatibility || {});
    revision.append(
      actionForm(
        "Save new draft version",
        [
          field("Version", version),
          ...provenance.nodes,
          field("Compatibility, pivot and crop JSON", compatibility),
        ],
        async () => {
          const updated = await api(`${base}/version`, "asset", {
            version: version.value,
            provenance: provenance.value(),
            compatibility: JSON.parse(compatibility.value),
          });
          selectAsset(`${updated.id}@${updated.version}`);
          refreshPage();
        },
      ),
    );
    root.append(revision);
    if (["still", "mask", "sequence"].includes(asset.kind)) {
      const normalize = section(
        "Prepare image proxies",
        "Creates colour-managed PNG previews in a new draft version. Working source files are retained.",
      );
      const version = input(next),
        edge = input("640", "number");
      normalize.append(
        actionForm(
          "Prepare proxies",
          [
            field("New version", version),
            field("Maximum edge in pixels", edge),
          ],
          async () => {
            const updated = await api(`${base}/proxy`, "asset", {
              version: version.value,
              max_edge: number(edge),
            });
            selectAsset(`${updated.id}@${updated.version}`);
            refreshPage();
          },
        ),
      );
      root.append(normalize);
    }
    if (asset.kind === "still") {
      const template = section(
        "Use as a still scene",
        "Creates an explicit one-layer scene template; it remains draft.",
      );
      const id = input(`${asset.id}-scene`),
        version = input("1.0");
      template.append(
        actionForm(
          "Create still scene template",
          [field("Template ID", id), field("Template version", version)],
          async () => {
            await api(`${prefix(project)}/templates/still`, "scene_template", {
              asset: { id: asset.id, version: asset.version },
              id: id.value,
              version: version.value,
              camera_id: "still",
            });
            return "Scene template saved. Open New episode to select it.";
          },
        ),
      );
      root.append(template);
    }
    const relink = section(
      "Relink matching source bytes",
      "Choose registered-root paths in the original sequence order. Every hash must match; this creates a new draft version.",
    );
    const paths = jsonEditor(asset.files.map((f) => f.location)),
      relinkVersion = input(next);
    relink.append(
      actionForm(
        "Verify and relink",
        [
          field("New version", relinkVersion),
          field("Ordered media paths JSON", paths),
        ],
        async () => {
          const updated = await api(`${base}/relink`, "asset", {
            version: relinkVersion.value,
            paths: JSON.parse(paths.value),
          });
          selectAsset(`${updated.id}@${updated.version}`);
          refreshPage();
        },
      ),
    );
    root.append(relink);
    const review = section(
      "Approve this content",
      "Use after visually reviewing the source and verifying its provenance and commercial rights. Approval is bound to this content hash.",
    );
    const hash = input(health.content_sha256);
    hash.readOnly = true;
    const reviewer = input(""),
      note = input("");
    if (
      ["synthetic", "unknown"].includes(
        asset.provenance?.origin || "unknown",
      ) ||
      (asset.provenance?.commercial_use || "pending") !== "confirmed" ||
      !health.media_valid ||
      (asset.approval?.status || "draft") === "approved"
    )
      review.append(
        element("p", {
          text: "Approval unavailable: content must be valid, rights confirmed, provenance known and non-synthetic, and the version still draft.",
        }),
      );
    else
      review.append(
        actionForm(
          "Record my approval",
          [
            field("Reviewed content SHA-256", hash),
            field("Reviewer", reviewer),
            field("Review note", note),
          ],
          async () => {
            await api(`${base}/approve`, "asset", {
              expected_hash: hash.value,
              reviewer: reviewer.value,
              note: note.value,
            });
            refreshPage();
          },
        ),
      );
    root.append(review);
  });
}
