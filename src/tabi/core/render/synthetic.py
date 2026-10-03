"""Owned geometric inputs for the T02 spike, not a Tabi character or T04 pack."""

import math
import struct
import sys
import wave
import zlib
from array import array
from pathlib import Path

WIDTH, HEIGHT, FPS, FRAMES = 960, 540, 30, 300
CABIN = (32, 48, 64)
ACTOR = (244, 164, 132)
FOREGROUND = (120, 80, 152)
PALETTE = [
    (208, 224, 232),
    (56, 96, 112),
    (176, 216, 168),
    (224, 184, 112),
    (88, 120, 160),
    (176, 136, 184),
]
# Original 5x7 bitmap lettering: no system or commercial font dependency.
LETTERS = {
    "D": [30, 17, 17, 17, 17, 17, 30],
    "V": [17, 17, 17, 17, 17, 10, 4],
    "W": [17, 17, 17, 21, 21, 21, 10],
    "S": [15, 16, 16, 14, 1, 1, 30],
    "Y": [17, 17, 10, 4, 4, 4, 4],
    "N": [17, 25, 25, 21, 19, 19, 17],
    "T": [31, 4, 4, 4, 4, 4, 4],
    "H": [17, 17, 17, 31, 17, 17, 17],
    "E": [31, 16, 16, 30, 16, 16, 31],
    "I": [31, 4, 4, 4, 4, 4, 31],
    "C": [15, 16, 16, 16, 16, 16, 15],
    "O": [14, 17, 17, 17, 17, 17, 14],
    "F": [31, 16, 16, 30, 16, 16, 16],
    "R": [30, 17, 17, 30, 20, 18, 17],
    "P": [30, 17, 17, 30, 16, 16, 16],
    "U": [17, 17, 17, 17, 17, 17, 14],
    "B": [30, 17, 17, 30, 17, 17, 30],
    "L": [16, 16, 16, 16, 16, 16, 31],
    "A": [14, 17, 17, 31, 17, 17, 17],
    "0": [14, 17, 19, 21, 25, 17, 14],
    "1": [4, 12, 4, 4, 4, 4, 14],
    "2": [14, 17, 1, 2, 4, 8, 31],
    "3": [30, 1, 1, 14, 1, 1, 30],
    "4": [2, 6, 10, 18, 31, 2, 2],
    "5": [31, 16, 16, 30, 1, 1, 30],
    "6": [14, 16, 16, 30, 17, 17, 14],
    "7": [31, 1, 2, 4, 8, 8, 8],
    "8": [14, 17, 17, 14, 17, 17, 14],
    "9": [14, 17, 17, 15, 1, 1, 14],
}


def png(path: Path, width: int, height: int, pixels: bytes, channels: int = 3) -> None:
    """Encode unprofiled 8-bit RGB/RGBA/gray fixture pixels without external libraries."""
    assert len(pixels) == width * height * channels

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        )

    stride = width * channels
    rows = b"".join(b"\0" + pixels[y * stride : (y + 1) * stride] for y in range(height))
    payload = b"\x89PNG\r\n\x1a\n" + chunk(
        b"IHDR", struct.pack(">2I5B", width, height, 8, {1: 0, 3: 2, 4: 6}[channels], 0, 0, 0)
    )
    path.write_bytes(payload + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


def label(pixels: bytearray, width: int, text: str, x: int, y: int, scale: int = 3) -> None:
    for index, letter in enumerate(text):
        for row, bits in enumerate(LETTERS.get(letter, [0] * 7)):
            for column in range(5):
                if bits & (1 << (4 - column)):
                    for dy in range(scale):
                        for dx in range(scale):
                            offset = (
                                (y + row * scale + dy) * width
                                + x
                                + index * 6 * scale
                                + column * scale
                                + dx
                            ) * 3
                            pixels[offset : offset + 3] = bytes((248, 248, 240))


def generate_inputs(root: Path) -> list[Path]:
    root.mkdir()
    cabin = bytearray(bytes(CABIN) * WIDTH * HEIGHT)
    label(cabin, WIDTH, "SYNTHETIC TEST", 36, 24)
    label(cabin, WIDTH, "NOT FOR PUBLICATION", 36, 500, 2)
    png(root / "cabin.png", WIDTH, HEIGHT, cabin)
    strip_width = 1920
    row = b"".join(bytes(PALETTE[(x // 80) % len(PALETTE)]) for x in range(strip_width))
    strip = bytearray(row * HEIGHT)
    for index in range(strip_width // 80):
        label(strip, strip_width, f"{index:02}", index * 80 + 14, 190, 3)
    png(root / "exterior.png", strip_width, HEIGHT, strip)
    mask = bytes(
        255 if 120 <= x < 840 and 80 <= y < 390 else 0 for y in range(HEIGHT) for x in range(WIDTH)
    )
    png(root / "window mask.png", WIDTH, HEIGHT, mask, 1)
    actor = bytearray()
    for y in range(200):
        for x in range(200):
            edge = min(x, y, 199 - x, 199 - y)
            alpha = 0 if edge < 16 else 128 if edge < 40 else 255
            actor.extend((*ACTOR, alpha))
    png(root / "transparent actor.png", 200, 200, actor, 4)
    foreground = bytes(
        channel
        for y in range(HEIGHT)
        for x in range(WIDTH)
        for channel in (*FOREGROUND, 255 if 320 <= x < 660 and 410 <= y < 478 else 0)
    )
    png(root / "foreground.png", WIDTH, HEIGHT, foreground, 4)
    samples = array("h")
    for sample in range(480000):
        fade = min(1, sample / 480, (479999 - sample) / 480)
        value = round(4096 * fade * math.sin(2 * math.pi * 440 * sample / 48000))
        samples.extend((value, value))
    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(str(root / "synthetic tone.wav"), "wb") as target:
        target.setnchannels(2)
        target.setsampwidth(2)
        target.setframerate(48000)
        target.writeframes(samples.tobytes())
    return [
        root / name
        for name in [
            "cabin.png",
            "exterior.png",
            "window mask.png",
            "transparent actor.png",
            "foreground.png",
            "synthetic tone.wav",
        ]
    ]


def expected_pixel(frame: int, x: int, y: int) -> tuple[int, int, int]:
    """Independent scalar reference; FFmpeg evaluates its own expression graph."""
    distance = 2 * min(frame, 90) + 4 * max(0, frame - 180)
    color = PALETTE[((x + distance) // 80) % 6] if 120 <= x < 840 and 80 <= y < 390 else CABIN
    if 60 <= frame < 240 and 380 <= x < 580 and 250 <= y < 450:
        edge = min(x - 380, y - 250, 579 - x, 449 - y)
        alpha = 0 if edge < 16 else 128 if edge < 40 else 255
        color = tuple(
            round((front * alpha + back * (255 - alpha)) / 255)
            for front, back in zip(ACTOR, color, strict=True)
        )
    if 320 <= x < 660 and 410 <= y < 478:
        color = FOREGROUND
    return color
