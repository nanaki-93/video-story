"""Strict JSON/safe YAML loading and deterministic schema publication."""

import json
from pathlib import Path

import yaml
from pydantic import ValidationError

from .models import DOCUMENT_MODELS, SCHEMA_MODELS, ValidationReport
from .models.base import Document, canonical_bytes, version_tuple
from .models.production import ValidationIssue

MAX_DOCUMENT_BYTES = 16 * 1024 * 1024


class DocumentError(ValueError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        location: list | None = None,
        issues: list[ValidationIssue] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.issues = issues or [
            ValidationIssue(
                severity="error",
                code=code,
                location=location or [],
                message=message,
                suggested_fix="Correct the document using its versioned contract.",
            )
        ]

    def report(self) -> ValidationReport:
        return ValidationReport(
            schema_version="1.0", document_type="validation_report", valid=False, issues=self.issues
        )


def _pairs(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if not isinstance(key, str) or key in result:
            raise ValueError("mapping keys must be strings and cannot be duplicated")
        result[key] = value
    return result


class _SafeLoader(yaml.SafeLoader):
    pass


# Keep ISO timestamps as strings, so JSON and YAML follow identical validation.
_SafeLoader.yaml_implicit_resolvers = {
    key: [(tag, regex) for tag, regex in rules if tag != "tag:yaml.org,2002:timestamp"]
    for key, rules in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _mapping(loader: _SafeLoader, node: yaml.MappingNode) -> dict:
    return _pairs(
        [
            (loader.construct_object(key), loader.construct_object(value))
            for key, value in node.value
        ]
    )


_SafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def _check_tree(value: object, depth: int = 0) -> None:
    if depth > 64:
        raise ValueError("document nesting exceeds 64 levels")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("mapping keys must be strings")
        for child in value.values():
            _check_tree(child, depth + 1)
    elif isinstance(value, list):
        for child in value:
            _check_tree(child, depth + 1)
    elif value is not None and type(value) not in {str, int, float, bool}:
        raise ValueError("document contains a non-JSON value")


def decode_data(payload: bytes | str, *, format: str = "json") -> dict:
    try:
        text = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        if len(text.encode("utf-8")) > MAX_DOCUMENT_BYTES:
            raise ValueError("document exceeds the 16 MiB limit")
        if format == "json":
            data = json.loads(text, object_pairs_hook=_pairs)
        elif format in {"yaml", "yml"}:
            if any(
                isinstance(token, (yaml.AliasToken, yaml.AnchorToken)) for token in yaml.scan(text)
            ):
                raise ValueError("YAML aliases and anchors are not supported")
            data = yaml.load(text, Loader=_SafeLoader)
        else:
            raise ValueError("document format must be JSON or YAML")
        if not isinstance(data, dict):
            raise ValueError("document root must be an object")
        _check_tree(data)
        canonical_bytes(data)  # Reject NaN and infinity even in unrecognized fields.
        return data
    except (ValueError, TypeError, RecursionError, yaml.YAMLError) as error:
        raise DocumentError("invalid_document", str(error)) from error


def validate_data(data: dict, *, model: type[Document] | None = None) -> Document:
    try:
        _check_tree(data)
    except (ValueError, TypeError, RecursionError) as error:
        raise DocumentError("invalid_document", str(error)) from error
    try:
        version = data.get("schema_version")
        major, _ = version_tuple(version)
        if major != 1:
            raise ValueError(f"unsupported schema major {major}; this application supports major 1")
    except (ValueError, TypeError) as error:
        raise DocumentError(
            "unsupported_schema_version", str(error), location=["schema_version"]
        ) from error
    if model is None:
        if version != "1.0":
            raise DocumentError(
                "unsupported_schema_version",
                "unsupported schema minor; an explicit migration is required",
                location=["schema_version"],
            )
        kind = data.get("document_type")
        if not isinstance(kind, str) or kind not in DOCUMENT_MODELS:
            raise DocumentError(
                "unknown_document_type",
                "missing or unknown document_type",
                location=["document_type"],
            )
        model = DOCUMENT_MODELS[kind]
    try:
        return model.model_validate_json(canonical_bytes(data))
    except ValidationError as error:
        issues = [
            ValidationIssue(
                severity="error",
                code=item["type"],
                location=list(item["loc"]),
                message=item["msg"],
                suggested_fix="Correct this field using the schema and contract constraints.",
            )
            for item in error.errors(include_input=False, include_context=False)
        ]
        raise DocumentError(
            "validation_failed", "document failed structural validation", issues=issues
        ) from error
    except (ValueError, TypeError, RecursionError) as error:
        raise DocumentError("invalid_document", str(error)) from error


def parse_document(payload: bytes | str, *, format: str = "json") -> Document:
    return validate_data(decode_data(payload, format=format))


def read_data(path: Path) -> dict:
    """Bounded JSON/YAML reading for documents and shared service requests."""
    with path.open("rb") as source:
        payload = source.read(MAX_DOCUMENT_BYTES + 1)
    return decode_data(payload, format=path.suffix.lower().removeprefix("."))


def read_document(path: Path) -> Document:
    return validate_data(read_data(path))


def schema_documents() -> dict[str, dict]:
    result = {}
    for name, model in SCHEMA_MODELS.items():
        schema = model.model_json_schema()
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["$id"] = f"urn:tabi:schema:1.0:{name}"
        result[f"{name}.schema.json"] = schema
    return result
