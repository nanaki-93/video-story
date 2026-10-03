import pytest

from tabi.core.assets import AssetService
from tabi.core.authoring import AuthoringService
from tabi.core.fixtures import generate_fixtures
from tabi.core.models import SceneTemplate
from tabi.core.models.base import AssetRef
from tabi.core.persistence import ProjectStore, RevisionConflict, StorageError, document_path
from tabi.core.timeline.compiler import ActionCompiler


def reference(doc):
    return AssetRef(id=doc.id, version=doc.version)


def review(author, doc, **changes):
    return author.review_metadata(
        doc.document_type,
        reference(doc),
        **{
            "expected_hash": doc.approval_hash,
            "reviewer": "Temporary automated test",
            "note": "Exercise review guards only; not real creative approval",
            **changes,
        },
    )


def approve_media(author):
    for asset in author.assets.list_assets():
        author.assets.approve(
            reference(asset),
            expected_hash=asset.approval_hash,
            reviewer="Temporary automated test",
            note="Owned policy fixture only",
        )


def test_review_requires_current_hash_approved_media_then_template(review_project):
    author, template, pack, episode = review_project
    with pytest.raises(RevisionConflict, match="changed"):
        review(author, template, expected_hash="0" * 64)
    with pytest.raises(ValueError, match="not approved"):
        review(author, template)
    approve_media(author)
    with pytest.raises(ValueError, match="approval"):
        review(author, pack)
    approved_template = review(author, template)
    approved_pack = review(author, pack)
    assert approved_template.approval.content_sha256 == template.approval_hash
    assert approved_pack.approval.content_sha256 == pack.approval_hash
    assert ActionCompiler(author.assets, purpose="production").compile(episode).locked_assets
    before = (author.store.root / document_path(approved_template)).read_bytes()
    with pytest.raises(StorageError, match="already approved"):
        review(author, approved_template)
    assert (author.store.root / document_path(approved_template)).read_bytes() == before
    # Editing creates a draft version and cannot silently carry approval forward.
    data = approved_template.model_dump(mode="json")
    data.update(version="1.1", revision=0, approval={"status": "draft"})
    next_version = author.install(data)
    assert next_version.approval.status == "draft"


def test_pack_review_uses_compiler_compatibility_and_rechecks_source_bytes(review_project):
    author, template, pack, _ = review_project
    approve_media(author)
    review(author, template)
    wrong = pack.model_dump(mode="json")
    wrong["actions"][0]["frame_count"] = 3
    changed = author.install(wrong, expected_revision=pack.revision)
    with pytest.raises(ValueError, match="frame count"):
        review(author, changed)
    restored = author.install(
        {**pack.model_dump(mode="json"), "revision": changed.revision},
        expected_revision=changed.revision,
    )
    media = author.assets.load(AssetRef(id="test-body", version="1.0"))
    author.assets.resolve(media.files[0].location).write_bytes(b"test corruption")
    with pytest.raises(ValueError, match="changed"):
        review(author, restored)
    assert author.metadata("action_pack", reference(pack)).approval.status == "draft"


def test_synthetic_metadata_cannot_be_approved(tmp_path):
    root = tmp_path / "Synthetic rejected"
    generate_fixtures(root)
    author = AuthoringService(AssetService(ProjectStore(root)))
    template = author.templates()[0]
    with pytest.raises(ValueError, match="not approved"):
        review(author, template)
    assert author.metadata("scene_template", reference(template)).approval.status == "draft"


def test_metadata_review_rechecks_revision_after_dependency_validation(review_project, monkeypatch):
    author, template, _, _ = review_project
    approve_media(author)
    original = author.assets.require_valid
    changed = False

    def concurrent_edit(*args, **kwargs):
        nonlocal changed
        result = original(*args, **kwargs)
        if not changed:
            changed = True
            data = template.model_dump(mode="json")
            data["fit"] = "crop"
            author.install(data, expected_revision=template.revision)
        return result

    monkeypatch.setattr(author.assets, "require_valid", concurrent_edit)
    with pytest.raises(RevisionConflict):
        review(author, template)
    current = author.metadata("scene_template", reference(template))
    assert isinstance(current, SceneTemplate) and current.fit == "crop"
    assert current.approval.status == "draft"
