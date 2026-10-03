"""Reproducible development pack manifest; never production approval."""

from typing import Literal, Self

from pydantic import Field, model_validator

from .base import SHA256, Document, HashedFile, RelativePath, unique


class FixtureManifest(Document):
    document_type: Literal["fixture_manifest"] = "fixture_manifest"
    generator: Literal["tabi-fixtures-v1"] = "tabi-fixtures-v1"
    generator_sha256: SHA256
    synthetic: bool = True
    production_approved: bool = False
    project: RelativePath = "project.json"
    episode: RelativePath = "episodes/episode.synthetic.json"
    files: list[HashedFile] = Field(min_length=1)

    @model_validator(mode="after")
    def synthetic_only(self) -> Self:
        if not self.synthetic or self.production_approved:
            raise ValueError("fixture packs must remain synthetic and unapproved")
        unique([f.location.path for f in self.files], "manifest paths")
        if any(f.location.root_id != "project" for f in self.files):
            raise ValueError("fixture files must be portable project-relative paths")
        return self
