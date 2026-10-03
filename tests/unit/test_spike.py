from pathlib import Path

import pytest

from tabi.core.render.spike import SpikeError, render_spike


def test_unknown_spike_encoder_fails_before_filesystem_access(tmp_path):
    target = tmp_path / "must not be created"
    with pytest.raises(SpikeError, match="Unsupported"):
        render_spike(None, target, "not-an-encoder")
    assert not target.exists()


def test_fixture_png_preserves_hidden_rgb_and_partial_alpha(tmp_path):
    # Inspect the actual interchange bytes through an independent decoder.
    # Pillow is the image-audit extra already installed by make setup.
    from PIL import Image

    from tabi.core.render.synthetic import ACTOR, generate_inputs

    inputs = generate_inputs(tmp_path / "inputs")
    with Image.open(inputs[3]) as image:
        assert image.mode == "RGBA"
        assert image.getpixel((4, 60)) == (*ACTOR, 0)
        assert image.getpixel((28, 60)) == (*ACTOR, 128)
        assert image.getpixel((70, 60)) == (*ACTOR, 255)
    assert all(Path(path).is_file() for path in inputs)
