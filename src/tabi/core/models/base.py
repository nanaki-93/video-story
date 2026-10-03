"""Shared contract primitives. No filesystem access or render behavior."""

import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, Strict, model_validator

Identifier = Annotated[str, Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")]
Version = Annotated[str, Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")]
Text = Annotated[str, Field(min_length=1), AfterValidator(lambda v: nonblank(v))]
SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Frame = Annotated[int, Strict(), Field(ge=0)]
PositiveInt = Annotated[int, Strict(), Field(gt=0)]
Number = Annotated[float, Field(allow_inf_nan=False)]
FractionValue = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]


def nonblank(value: str) -> str:
    if not value.strip() or "\x00" in value:
        raise ValueError("must be nonblank and contain no NUL")
    return value


def relative_path(value: str) -> str:
    """Require a normalized, portable relative file path; preserve Unicode."""
    nonblank(value)
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or value in {".", ".."}
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or "\\" in value
        or ":" in value
        or value.startswith("~")
        or any(ord(c) < 32 for c in value)
    ):
        raise ValueError(
            "expected a normalized relative path without traversal, URL or drive prefix"
        )
    return value


RelativePath = Annotated[str, AfterValidator(relative_path)]


def absolute_path(value: str) -> str:
    nonblank(value)
    if not value.startswith("/") or "\\" in value or "://" in value:
        raise ValueError("registered roots must be absolute local POSIX paths")
    if value != "/" and str(PurePosixPath(value)) != value:
        raise ValueError("registered roots must be normalized")
    if ".." in PurePosixPath(value).parts or value.startswith("//"):
        raise ValueError("registered roots cannot contain traversal or network prefixes")
    return value


AbsolutePath = Annotated[str, AfterValidator(absolute_path)]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
        validate_default=True,
        revalidate_instances="always",
        allow_inf_nan=False,
    )


class Document(Model):
    schema_version: Literal["1.0"]


class DraftDocument(Document):
    id: Identifier
    revision: Frame = 0


def canonical_bytes(value: BaseModel | dict) -> bytes:
    """Version-1 canonical JSON: UTF-8, sorted keys, compact separators, finite numbers."""
    data = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    return json.dumps(
        data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def content_hash(value: BaseModel | dict) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def unique(values: list, description: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {description}")


class FrameRate(Model):
    num: PositiveInt
    den: PositiveInt

    @model_validator(mode="after")
    def reduced(self) -> Self:
        if math.gcd(self.num, self.den) != 1:
            raise ValueError("fps must be a reduced positive rational")
        return self

    def sample_at(self, frame: int, sample_rate: int = 48000) -> int:
        if type(frame) is not int or frame < 0:
            raise ValueError("frame must be a nonnegative integer")
        if type(sample_rate) is not int or sample_rate <= 0:
            raise ValueError("sample rate must be a positive integer")
        return round(Fraction(frame * sample_rate * self.den, self.num))


class FrameInterval(Model):
    start_frame: Frame
    end_frame: Frame

    @model_validator(mode="after")
    def nonempty(self) -> Self:
        if self.end_frame <= self.start_frame:
            raise ValueError("frame interval must be nonempty and half-open")
        return self


class Canvas(Model):
    width: PositiveInt
    height: PositiveInt


class Point(Model):
    x: Number
    y: Number


class Crop(Model):
    x: Frame
    y: Frame
    width: PositiveInt
    height: PositiveInt


class AssetRef(Model):
    id: Identifier
    version: Version


class AssetLock(AssetRef):
    sha256: SHA256 | None = None


class ResolvedAssetLock(AssetRef):
    sha256: SHA256


class MediaPath(Model):
    root_id: Identifier = "project"
    path: RelativePath


class HashedFile(Model):
    location: MediaPath
    sha256: SHA256
    size_bytes: Frame


def version_tuple(version: str) -> tuple[int, int]:
    if not isinstance(version, str) or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)", version):
        raise ValueError("schema_version must have the form major.minor")
    major, minor = version.split(".")
    return int(major), int(minor)
