#!/usr/bin/env python3
"""Blind bake-off between two models' answers to bakeoff/task.md.

Step 1 (mix):    python3 scripts/bakeoff_blind.py
    reads  bakeoff/answers/claude.md and bakeoff/answers/gpt.md
    writes bakeoff/blind/sheet.md  (items in random order, source removed)
           bakeoff/blind/key.json  (item -> model; do not open before scoring)
Step 2 (score):  each judge saves a filled copy of bakeoff/scoring-sheet.md in bakeoff/scores/
Step 3 (reveal): python3 scripts/bakeoff_blind.py --reveal
    prints average scores per model and criterion.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BAKE = ROOT / "bakeoff"
MODELS = {"claude": BAKE / "answers" / "claude.md", "gpt": BAKE / "answers" / "gpt.md"}
ITEM_RE = re.compile(r"^\s*(\d+)[.)\-]\s*(.*)$")


def parse_answer(text: str) -> tuple[list[str], str]:
    """Return (hooks, scene) from an answer written in the task's format."""
    sections = re.split(r"^##\s*", text, flags=re.MULTILINE)
    hooks_txt = next((s for s in sections if s.upper().startswith("HOOKS")), "")
    scene_txt = next((s for s in sections if s.upper().startswith("SCENE")), "")
    hooks: list[str] = []
    for line in hooks_txt.splitlines()[1:]:
        m = ITEM_RE.match(line)
        if m:
            hooks.append(m.group(2).strip())
        elif hooks and line.strip():
            hooks[-1] += " " + line.strip()  # continuation of a multi-line hook
    scene = "\n".join(scene_txt.splitlines()[1:]).strip()
    return [h for h in hooks if h], scene


def mix() -> int:
    items = []  # (kind, model, text)
    for model, path in MODELS.items():
        if not path.exists():
            print(f"missing {path.relative_to(ROOT)}")
            return 1
        hooks, scene = parse_answer(path.read_text(encoding="utf-8"))
        if len(hooks) != 10 or not scene:
            print(f"WARNING {model}: found {len(hooks)} hooks and "
                  f"{'a' if scene else 'no'} scene; check the answer follows the task format")
        items += [("H", model, h) for h in hooks]
        if scene:
            items.append(("S", model, scene))

    rng = secrets.SystemRandom()
    hooks = [i for i in items if i[0] == "H"]
    scenes = [i for i in items if i[0] == "S"]
    rng.shuffle(hooks)
    rng.shuffle(scenes)

    key, lines = {}, ["# BLIND SHEET", "", "Score each item on bakeoff/scoring-sheet.md.", "", "## Hooks", ""]
    for n, (_, model, text) in enumerate(hooks, start=1):
        iid = f"H-{n:02d}"
        key[iid] = model
        lines += [f"**{iid}** {text}", ""]
    lines += ["## Scenes", ""]
    for n, (_, model, text) in enumerate(scenes, start=1):
        iid = f"S-{n:02d}"
        key[iid] = model
        lines += [f"### {iid}", "", text, ""]

    out = BAKE / "blind"
    out.mkdir(parents=True, exist_ok=True)
    (out / "sheet.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "key.json").write_text(json.dumps(key, indent=2), encoding="utf-8")
    print(f"OK  {len(hooks)} hooks and {len(scenes)} scenes -> bakeoff/blind/sheet.md")
    print("    Read the sheet once before sharing it: remove anything that reveals a model.")
    return 0


def reveal() -> int:
    key_path = BAKE / "blind" / "key.json"
    if not key_path.exists():
        print("run the mix step first")
        return 1
    key = json.loads(key_path.read_text(encoding="utf-8"))
    sheets = sorted((BAKE / "scores").glob("*.md"))
    if not sheets:
        print("no filled sheets in bakeoff/scores/")
        return 1

    hook_cols, scene_cols = ["Funny", "Saudi", "Stop"], ["Funny", "Saudi"]
    totals: dict[tuple[str, str, str], list[float]] = {}
    row_re = re.compile(r"^\|\s*([HS]-\d{2})\s*\|(.*)$")
    for sheet in sheets:
        for line in sheet.read_text(encoding="utf-8").splitlines():
            m = row_re.match(line)
            if not m or m.group(1) not in key:
                continue
            iid = m.group(1)
            cells = [c.strip() for c in m.group(2).split("|")]
            cols = hook_cols if iid.startswith("H") else scene_cols
            for col, val in zip(cols, cells):
                try:
                    score = float(val)
                except ValueError:
                    continue
                if 1 <= score <= 5:
                    totals.setdefault((key[iid], iid[0], col), []).append(score)

    print(f"Judges: {len(sheets)}\n")
    print("| Model | Hooks Funny | Hooks Saudi | Hooks Stop | Scene Funny | Scene Saudi |")
    print("|---|---|---|---|---|---|")
    for model in MODELS:
        cells = []
        for kind, cols in (("H", hook_cols), ("S", scene_cols)):
            for col in cols:
                vals = totals.get((model, kind, col), [])
                cells.append(f"{sum(vals) / len(vals):.2f} (n={len(vals)})" if vals else "-")
        print(f"| {model} | " + " | ".join(cells) + " |")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reveal", action="store_true", help="total the judges' scores per model")
    args = ap.parse_args()
    return reveal() if args.reveal else mix()


if __name__ == "__main__":
    sys.exit(main())
