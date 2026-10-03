"""Bounded top-level ISO BMFF box inspection; never load media payloads into memory."""

import struct
from pathlib import Path

from ..models.rendering import MP4Layout
from .backend import RenderError


def verify_fast_start(path):
    offsets = {}
    with Path(path).open("rb") as stream:
        size = stream.seek(0, 2)
        stream.seek(0)
        count = 0
        while stream.tell() < size:
            start = stream.tell()
            header = stream.read(8)
            if len(header) != 8 or count >= 10000:
                raise RenderError("invalid or excessive MP4 box headers")
            length, kind = struct.unpack(">I4s", header)
            minimum = 8
            if length == 1:
                extended = stream.read(8)
                if len(extended) != 8:
                    raise RenderError("truncated extended MP4 box")
                length, minimum = struct.unpack(">Q", extended)[0], 16
            elif length == 0:
                length = size - start
            if length < minimum or start + length > size:
                raise RenderError("MP4 box extends outside the file")
            offsets.setdefault(kind, []).append(start)
            stream.seek(start + length)
            count += 1
    if (
        len(offsets.get(b"ftyp", [])) != 1
        or len(offsets.get(b"moov", [])) != 1
        or not offsets.get(b"mdat")
        or offsets[b"moov"][0] > offsets[b"mdat"][0]
    ):
        raise RenderError("MP4 needs one movie header before its media payload (Fast Start)")
    return MP4Layout(moov_offset=offsets[b"moov"][0], first_mdat_offset=offsets[b"mdat"][0])
