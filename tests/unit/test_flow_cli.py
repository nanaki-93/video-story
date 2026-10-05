import json

from tabi.cli.main import main
from tabi.core.flow.service import FlowService
from tabi.core.models.flow import FlowLimits, FlowRecipe
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
