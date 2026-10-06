import hashlib
import json

from tabi.cli.main import main
from tabi.core.flow.media import FlowMedia
from tabi.core.flow.service import FlowService
from tabi.core.models.base import HashedFile, MediaPath
from tabi.core.models.flow import FlowLimits, FlowRecipe, FlowReference, FlowState
from tabi.core.persistence import ProjectStore


def test_cli_and_core_share_saved_prompt_and_revision(tmp_path, capsys):
    store = ProjectStore.initialize(tmp_path / "Project 東京", "CLI test")
    limits = tmp_path / "limits.json"
    limits.write_text(
        FlowLimits(
            credit_ceiling=10,
            remaining_allowance=10,
            estimated_credit_per_attempt=5,
            allowance_checked_at="2026-10-06",
        ).model_dump_json()
    )
    recipe = tmp_path / "recipe.json"
    recipe.write_text(FlowRecipe(opening_mode="text_reference").model_dump_json())
    common = ["--project", str(store.root)]
    assert main(["flow", "create", *common, "--limits", str(limits), "--recipe", str(recipe)]) == 0
    episode = json.loads(capsys.readouterr().out)
    assert main(["flow", "prepare", episode["id"], *common, "--revision", "0"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert (
        FlowService(store).get(episode["id"]).attempts[0].prompt == result["attempts"][0]["prompt"]
    )
    assert main(["flow", "status", episode["id"], *common]) == 0
    assert json.loads(capsys.readouterr().out)["next_step"]["action"] == "waiting_flow"
    assert main(["flow", "pause", episode["id"], *common, "--revision", "0"]) == 4


def test_cli_imports_keyed_reviewed_references_and_starts_planned_shot(
    tmp_path, capsys, monkeypatch
):
    store = ProjectStore.initialize(tmp_path / "Project 東京", "CLI planned shots")
    limits = FlowLimits(
        credit_ceiling=100,
        remaining_allowance=100,
        estimated_credit_per_attempt=5,
        estimated_start_credit=10,
        allowance_checked_at="2026-10-06",
    )
    service = FlowService(store)
    episode = service.create("Planned shots", limits)
    common = ["--project", str(store.root)]
    state = tmp_path / "facts.json"
    state.write_text(
        FlowState(cup_kind="takeaway", cup_position="table", hands="resting").model_dump_json()
    )

    def reference(self, source, **values):
        data = values["key"].encode()
        (store.root / "sources" / source.path).write_bytes(data)
        return FlowReference(
            **values,
            media=HashedFile(
                location=MediaPath(path=f"sources/{source.path}"),
                sha256=hashlib.sha256(data).hexdigest(),
                size_bytes=len(data),
            ),
        )

    monkeypatch.setattr(FlowMedia, "reference", reference)
    for shot in episode.recipe.shots:
        key = shot.reference_key
        assert main(["flow", "status", episode.id, *common]) == 0
        guidance = json.loads(capsys.readouterr().out)["next_reference"]
        assert guidance["key"] == key and shot.exterior in guidance["instruction"]
        assert (
            main(
                [
                    "flow",
                    "reference",
                    episode.id,
                    *common,
                    "--revision",
                    str(episode.revision),
                    "--source",
                    f"project:{key}.png",
                    "--key",
                    key,
                    "--title",
                    key,
                    "--state",
                    str(state),
                    "--note",
                    "Unit fixture only",
                    "--synthetic",
                ]
            )
            == 0
        )
        saved = json.loads(capsys.readouterr().out)
        episode = service.get(episode.id)
        assert saved["references"][-1]["starting_state"]["cup_position"] == "table"
    assert main(["flow", "prepare", episode.id, *common, "--revision", str(episode.revision)]) == 0
    attempt = json.loads(capsys.readouterr().out)["attempts"][-1]
    assert attempt["mode"] == "shot_start" and attempt["reserved_credits"] == 10
