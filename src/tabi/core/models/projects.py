"""Portable project index and registered local media roots."""

from typing import Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from .base import AbsolutePath, DraftDocument, Identifier, Text, unique


class Project(DraftDocument):
    document_type: Literal["project"]
    title: Text
    root: Literal["."] = "."
    media_roots: dict[Identifier, AbsolutePath] = Field(default_factory=dict)
    created_at: AwareDatetime
    updated_at: AwareDatetime
    episode_ids: list[Identifier] = Field(default_factory=list)

    @model_validator(mode="after")
    def project_shape(self) -> Self:
        if "project" in self.media_roots:
            raise ValueError("root ID 'project' is reserved for the containing project folder")
        if self.updated_at < self.created_at:
            raise ValueError("updated_at cannot precede created_at")
        unique(self.episode_ids, "project episode IDs")
        return self
