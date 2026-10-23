#!/usr/bin/env python3
"""Checks on the preset lint, run in CI beside it."""

import json
import pathlib
import sys
import tempfile

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from preset_lint import missing_labels  # noqa: E402


def store(root, presets, index):
    services = root / "services"
    services.mkdir(parents=True)
    for name, body in presets.items():
        (services / f"{name}.yaml").write_text(body)
    (services / "index.json").write_text(json.dumps({"services": index}))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        store(root, {"good": "name: good\nlabel: Good\n", "bare": "name: bare\n", "blank": "name: blank\nlabel: ' '\n"},
              [{"name": "good", "label": "Good"}, {"name": "bare"}])
        found = missing_labels(root)
    assert len(found) == 3, found
    assert any("bare.yaml" in f for f in found), found
    assert any("blank.yaml" in f for f in found), found
    assert any("entry `bare`" in f for f in found), found
    assert not any("good" in f for f in found), found
    print("preset lint checks passed.")


if __name__ == "__main__":
    main()
