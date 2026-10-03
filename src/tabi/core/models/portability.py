"""Private portable backup manifests; embedded roots can only resolve inside the project."""

from typing import Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from .base import Document, Frame, HashedFile, Identifier, Text, unique


class PortableRoots(Document):
    document_type: Literal["portable_roots"] = "portable_roots"
    roots: list[Identifier] = Field(max_length=1000)

    @model_validator(mode="after")
    def safe_roots(self) -> Self:
        unique(self.roots, "portable roots")
        if "project" in self.roots:
            raise ValueError("the project root cannot be overridden")
        return self


class BackupManifest(Document):
    document_type: Literal["backup_manifest"] = "backup_manifest"
    project_id: Identifier
    created_at: AwareDatetime
    files: list[HashedFile] = Field(min_length=1, max_length=100000)
    total_bytes: Frame
    warnings: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def contained(self) -> Self:
        paths = [f.location.path for f in self.files]
        unique(paths, "backup files")
        if "project/project.json" not in paths or any(
            f.location.root_id != "project" or not f.location.path.startswith("project/")
            for f in self.files
        ):
            raise ValueError("backup files must stay within the private project directory")
        if self.total_bytes != sum(f.size_bytes for f in self.files):
            raise ValueError("backup size differs from its file inventory")
        return self
