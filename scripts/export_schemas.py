"""Publish/check deterministic JSON Schemas generated from the Python contracts."""

import argparse
import json
from pathlib import Path

from tabi.core.documents import schema_documents


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("schemas"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = schema_documents()
    stale = []
    if not args.check:
        args.output.mkdir(parents=True, exist_ok=True)
    for name, schema in expected.items():
        path = args.output / name
        text = json.dumps(schema, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    stale.extend(
        path.name for path in args.output.glob("*.schema.json") if path.name not in expected
    )
    if stale:
        print("Schema files need regeneration/removal: " + ", ".join(sorted(stale)))
        return 1
    print(f"{'Checked' if args.check else 'Wrote'} {len(expected)} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
