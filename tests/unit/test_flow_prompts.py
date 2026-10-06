import pytest
from test_flow_contracts import episode_data

from tabi.core.flow.prompts import compile_prompt, expected_ending
from tabi.core.flow.service import FlowError, updated
from tabi.core.models.flow import FlowBeat, FlowEpisode, FlowReference


def setup_state(**values):
    data = episode_data()
    data["candidates"][0]["observed_state"] = {
        "cup_kind": "takeaway",
        "cup_position": "table",
        "has_handle": False,
        "has_saucer": False,
        "hands": "resting",
        "pose": "watching",
        "inventory": ["one tan takeaway cup", "one open book", "one pen", "one brown bag"],
        **values,
    }
    episode = FlowEpisode.model_validate(data)
    return episode, episode.candidates[0]


def test_pickup_uses_real_cup_and_does_not_reset_scenery_or_hands():
    episode, parent = setup_state(district="Ginza")
    beat = FlowBeat(id="pickup", kind="pickup", target_frame=720)
    mode, prompt = compile_prompt(episode, beat, parent)
    assert mode == "extend"
    assert "body of that same cup" in prompt
    assert "Existing handle" not in prompt and "white ceramic" not in prompt
    assert "outside: Ginza" not in prompt and "enters building" not in prompt
    assert "hands on" not in prompt and "below the mouth" in prompt
    assert "leopard" not in prompt and "one brown bag" not in prompt
    assert expected_ending(parent.observed_state, beat).cup_position == "held"
    assert parent.observed_state.cup_position == "table"


def test_sip_and_return_require_a_held_cup():
    episode, parent = setup_state()
    beat = FlowBeat(id="sip", kind="sip", target_frame=900)
    with pytest.raises(FlowError, match="already held"):
        compile_prompt(episode, beat, parent)
    episode, parent = setup_state(cup_position="held", hands="holding_cup")
    assert "End still holding" in compile_prompt(episode, beat, parent)[1]
    beat = updated(beat, kind="return_cup")
    assert expected_ending(parent.observed_state, beat).hands == "resting"


def test_opening_modes_separate_appearance_from_motion():
    episode, _ = setup_state()
    beat = FlowBeat(id="opening", kind="rest", target_frame=0)
    with pytest.raises(FlowError, match="reference image"):
        compile_prompt(episode, beat, None)
    reference = FlowReference(title="Original", media=episode.candidates[0].media)
    episode = updated(episode, references=[reference])
    assert "leopard" not in compile_prompt(episode, beat, None)[1]
    episode = updated(episode, recipe=updated(episode.recipe, opening_mode="text_reference"))
    assert "leopard" in compile_prompt(episode, beat, None)[1]


def test_incompatible_overrides_and_repeated_district_are_explained():
    episode, parent = setup_state(district="Ginza")
    beat = FlowBeat(id="pickup", kind="pickup", target_frame=720)
    for override in ["Grip the cup handle", "Both hands stay on the lap", "Put it on the saucer"]:
        with pytest.raises(FlowError):
            compile_prompt(episode, beat, parent, override=override)
    beat = FlowBeat(id="district", kind="district", target_frame=720, district="Ginza")
    with pytest.raises(FlowError, match="already established"):
        compile_prompt(episode, beat, parent)


def test_retry_changes_only_current_focus_and_rejected_parent_is_refused():
    episode, parent = setup_state()
    beat = FlowBeat(id="look", kind="look", target_frame=360)
    mode, prompt = compile_prompt(episode, beat, parent, retry_reason="Keep gills attached.")
    assert mode == "extend" and "gills stay attached" in prompt
    assert "takes one" not in prompt and "lifts" not in prompt
    parent = updated(parent, review="rejected")
    with pytest.raises(FlowError, match="accepted parent"):
        compile_prompt(episode, beat, parent)


def test_mouth_retry_allows_the_requested_sip_and_returns_to_resting_shape():
    episode, parent = setup_state(cup_position="held", hands="holding_cup")
    beat = FlowBeat(id="sip", kind="sip", target_frame=900)
    for options in ({"retry_focus": "mouth"}, {"retry_reason": "Mouth changed at the end"}):
        _, prompt = compile_prompt(episode, beat, parent, **options)
        assert "one small sip" in prompt and "lips meet the rim" in prompt
        assert "closed smile throughout" not in prompt and "resting shape" in prompt


def test_identity_retry_protects_accessories_without_replacing_the_current_action():
    episode, parent = setup_state()
    beat = FlowBeat(id="look", kind="look", target_frame=360)
    _, prompt = compile_prompt(
        episode, beat, parent, retry_focus="identity", retry_reason="Invented headphone emblem"
    )
    assert "turns the head slightly toward the window" in prompt
    assert "gills stay attached" in prompt and "neck stays connected" in prompt
    assert (
        "Markings, clothing and accessories keep exactly their starting shapes and colors" in prompt
    )
    assert "Invented headphone emblem" not in prompt


@pytest.mark.parametrize("kind", ["pickup", "sip", "return_cup"])
def test_cup_correction_uses_confirmed_facts_and_keeps_the_requested_action(kind):
    episode, parent = setup_state(
        cup_position="table" if kind == "pickup" else "held",
        hands="resting" if kind == "pickup" else "holding_cup",
    )
    beat = FlowBeat(id=kind, kind=kind, target_frame=720)
    original = compile_prompt(episode, beat, parent)[1]
    _, corrected = compile_prompt(
        episode, beat, parent, retry_focus="props", retry_reason="A handle appeared, plus dots"
    )
    assert corrected.startswith(original)
    assert "same handle-free takeaway cup" in corrected
    assert "original rigid shape and markings" in corrected
    assert "saucer-free" in corrected
    assert "plus dots" not in corrected and "one brown bag" not in corrected


def test_cup_correction_does_not_invent_unknown_facts_or_affect_other_actions():
    episode, parent = setup_state(
        cup_kind="unknown",
        cup_position="held",
        hands="holding_cup",
        has_handle=None,
        has_saucer=None,
    )
    beat = FlowBeat(id="return", kind="return_cup", target_frame=1080)
    prompt = compile_prompt(episode, beat, parent, retry_focus="props")[1]
    assert "same cup keeps" in prompt
    assert not any(word in prompt for word in ("takeaway", "ceramic", "handle", "saucer"))
    episode, parent = setup_state(cup_kind="ceramic", has_handle=True, has_saucer=True)
    beat = updated(beat, kind="pickup")
    prompt = compile_prompt(episode, beat, parent, retry_focus="props")[1]
    assert "same handled ceramic cup" in prompt and "existing saucer stays in place" in prompt
    beat = updated(beat, kind="look")
    prompt = compile_prompt(episode, beat, parent, retry_focus="props")[1]
    assert "Only the object involved" in prompt and "ceramic" not in prompt
