#!/usr/bin/env python3
"""Check that every preset carries what lerd needs to present it.

The schema guard answers whether an older lerd can still read the store. This
answers whether a definition is complete, so the two failures never read the
same: a missing label is something to add, not a change that breaks an install.

Usage: preset_lint.py [store-dir]
"""

import json
import pathlib
import sys
import yaml


def missing_labels(root):
    """Presets and index entries that name no label.

    lerd shows a service under its label, so every preset carries one rather
    than leaving lerd to guess the spelling from the lowercase name.
    """
    missing = []
    for path in sorted(pathlib.Path(root).rglob("*.yaml")):
        if path.parent.name != "services":
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                label = (yaml.safe_load(handle) or {}).get("label")
        except yaml.YAMLError:
            continue
        if not isinstance(label, str) or not label.strip():
            missing.append(f"{path.relative_to(root)}: no `label`, the name lerd shows the service under")
    for path in sorted(pathlib.Path(root).rglob("index.json")):
        if path.parent.name != "services":
            continue
        with open(path, "r", encoding="utf-8") as handle:
            for entry in json.load(handle).get("services", []):
                if not str(entry.get("label", "")).strip():
                    missing.append(f"{path.relative_to(root)}: entry `{entry.get('name')}` has no `label`")
    return missing


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    failures = missing_labels(root)
    for line in failures:
        print(f"error: {line}")
    if failures:
        print(f"\n{len(failures)} preset problem(s) to fix.")
        return 1
    print("preset lint passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
