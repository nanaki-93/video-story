"""Small original geometric assets for lo-fi verification; never approved TABI artwork."""

import wave
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin

from .assets import AssetService
from .models.base import AssetRef, FrameRate
from .models.lofi import LofiScene
from .models.registry import ImportRequest
from .persistence import ProjectStore


def generate_lofi_fixtures(root):
    root = Path(root)
    store = ProjectStore.initialize(root, "SYNTHETIC lo-fi asset test")
    assets = AssetService(store)
    folder = root / "sources" / "東京 loop assets"
    folder.mkdir(parents=True)
    info = PngImagePlugin.PngInfo()
    info.add(b"sRGB", b"\x00")
    fps = FrameRate(num=24, den=1)

    def register(identity, images, *, kind="still"):
        paths = []
        for index, image in enumerate(images):
            path = folder / f"{identity} {index:03}.png"
            image.save(path, pnginfo=info if kind != "mask" else None)
            paths.append({"path": str(path.relative_to(root))})
        return assets.import_asset(
            ImportRequest(
                id=f"lofi.test.{identity}",
                version="1.0",
                kind=kind,
                paths=paths,
                fps=fps if kind == "sequence" else None,
                provenance={"origin": "synthetic", "notes": "Original test geometry; not TABI art"},
            )
        )

    master = Image.new("RGB", (320, 180), (64, 42, 58))
    draw = ImageDraw.Draw(master)
    draw.rectangle((24, 44, 134, 150), fill=(120, 174, 155))
    draw.rectangle((52, 65, 88, 80), fill=(220, 210, 190))
    register("master", [master])
    mask = Image.new("L", (320, 180))
    ImageDraw.Draw(mask).rectangle((170, 12, 312, 140), fill=255)
    register("window", [mask], kind="mask")
    strip = Image.new("RGB", (448, 180))
    draw = ImageDraw.Draw(strip)
    for x in range(448):
        draw.line((x, 0, x, 179), fill=(50 + (x % 128), 110, 165))
    register("scenery", [strip])
    frames = []
    for color in [None, (220, 80, 70), (50, 30, 40), None]:
        image = Image.new("RGBA", (320, 180), (0, 0, 0, 0))
        if color:
            ImageDraw.Draw(image).rectangle((52, 65, 88, 80), fill=(*color, 255))
        frames.append(image)
    register("blink", frames, kind="sequence")
    audio = folder / "original synthetic tone.wav"
    with wave.open(str(audio), "wb") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(48000)
        stream.writeframes(b"\x00\x00\x00\x00" * 96000)
    assets.import_asset(
        ImportRequest(
            id="lofi.test.music",
            version="1.0",
            kind="audio",
            paths=[{"path": str(audio.relative_to(root))}],
            provenance={"origin": "synthetic", "notes": "Two seconds of test silence"},
        )
    )

    def ref(name):
        return AssetRef(id=f"lofi.test.{name}", version="1.0")

    scene = LofiScene(
        schema_version="1.0",
        id="synthetic.sunset",
        title="SYNTHETIC sunset loop",
        master=ref("master"),
        fps=fps,
        window_mask=ref("window"),
        speed=24.0,
        scenery=[{"id": "city", "asset": ref("scenery"), "repeat_width": 128}],
        overlays=[
            {
                "id": "eyes",
                "asset": ref("blink"),
                "timing": {
                    "source": {"start_frame": 0, "end_frame": 4},
                    "repeat_frames": 13,
                    "first_frame": 2,
                },
            }
        ],
    )
    return assets, scene
