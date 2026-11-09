#!/usr/bin/env python3
"""Run the agents from the command line with your subscriptions (no API keys).

  provider anthropic -> Claude Code:  claude -p "<kickoff>" --agent <id> --permission-mode acceptEdits
  provider openai    -> Codex CLI:    codex exec -C <project> --sandbox workspace-write -   (prompt on stdin)

Each agent reads its inputs and writes its own output file. Runs in the same step run in
parallel; steps run in order; the runner always stops at the end of a stage (gate or client
checkpoint) and never starts the next stage by itself.

Usage (from the project root):
  python3 scripts/run.py --doctor                 check CLIs, logins, git, build
  python3 scripts/run.py --list                   every run with its status
  python3 scripts/run.py --stage 02               run stage 02 (skips runs whose output exists)
  python3 scripts/run.py --stage 06 --step 2      run one step of a stage
  python3 scripts/run.py --run 02-1-1-generator-a.md   run one kickoff
Options: --dry-run (print commands only), --force (re-run even if the output exists),
         --parallel N (max simultaneous runs, default 3), --timeout SECONDS (default 1800)

Before the first run:  claude auth login    and    codex login   (sign in with ChatGPT)
"""
from __future__ import annotations

import argparse
import os
import signal
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import ROOT, BuildError, load_yaml  # noqa: E402
from run_state import RunState  # noqa: E402

LOGS = ROOT / "logs"
DEFAULT_MODELS = {None, "", "inherit", "default"}


@dataclass
class Run:
    name: str          # kickoff file name
    stage: str
    stage_name: str
    step: int
    agent: str
    provider: str
    model: str | None
    extra_tools: list
    output: str
    manual: bool
    reasoning_effort: str | None = None
    task: str = ''

    @property
    def checks_file(self) -> bool:
        return self.output.startswith("work/")

    def status(self) -> str:
        if not self.checks_file:
            return "append"
        path = ROOT / self.output
        return "done" if path.exists() and path.stat().st_size > 0 else "pending"


def load_runs() -> tuple[list[Run], dict]:
    agents = load_yaml("config/agents.yaml")["agents"]
    pipeline = load_yaml("config/pipeline.yaml")
    runs = []
    for stage in pipeline["stages"]:
        sid = stage["id"]
        for si, step in enumerate(stage["steps"], start=1):
            for ri, r in enumerate(step, start=1):
                a = agents[r["agent"]]
                runs.append(Run(
                    name=f"{sid}-{si}-{ri}-{r['agent']}.md", stage=sid, stage_name=stage["name"],
                    step=si, agent=r["agent"], provider=a["provider"], model=a.get("model"),
                    extra_tools=a.get("extra_tools", []), output=str(r.get("output", "")),
                    manual=bool(stage.get("manual")),
                    reasoning_effort=a.get("model_reasoning_effort"),
                    task=str(r.get('mode', stage['name'])) +
                         (" / " + ", ".join(f'{k}={v}' for k, v in r['params'].items())
                          if r.get('params') else '')))
    return runs, {s["id"]: s for s in pipeline["stages"]}


# --------------------------------------------------------------------------- commands
def command_for(run: Run, kickoff: str) -> tuple[list[str], str | None]:
    """Return (argv, stdin_text)."""
    if run.provider == "anthropic":
        argv = ["claude", "-p", kickoff, "--agent", run.agent,
                "--permission-mode", "acceptEdits", "--output-format", "text"]
        if run.model not in DEFAULT_MODELS:
            argv += ["--model", run.model]
        if run.extra_tools:  # variadic flag goes last
            argv += ["--allowedTools", *run.extra_tools]
        return argv, None
    role_file = ROOT / "codex" / f"{run.agent}.md"
    if not role_file.exists():
        raise BuildError(f"missing {role_file.relative_to(ROOT)}; run scripts/build.py")
    prompt = role_file.read_text(encoding="utf-8") + "\n\n" + kickoff
    argv = ["codex", "exec", "-C", str(ROOT), "--sandbox", "workspace-write",
            "-o", str(LOGS / f"{run.name[:-3]}.last.md")]
    if run.model not in DEFAULT_MODELS:
        argv += ["-m", run.model]
    if run.reasoning_effort is not None:
        argv += ["-c", f'model_reasoning_effort="{run.reasoning_effort}"']
    argv.append("-")  # read the prompt from stdin
    return argv, prompt


def execute(run: Run, dry: bool, timeout: int, state: RunState | None = None) -> tuple[Run, str]:
    kickoff_path = ROOT / "kickoffs" / run.name
    if not kickoff_path.exists():
        if state:
            state.finish('FAILED', reason='kickoff missing')
        return run, "ERROR kickoff missing (run scripts/build.py)"
    argv, stdin_text = command_for(run, kickoff_path.read_text(encoding="utf-8"))
    tool = "Claude Code" if run.provider == "anthropic" else "Codex"
    if dry:
        shown = [a if len(a) < 60 else a[:40].replace("\n", " ") + "…" for a in argv]
        stdin_note = f"  (+ {len(stdin_text)} chars on stdin)" if stdin_text else ""
        return run, f"DRY  [{tool}] {' '.join(shown)}{stdin_note}"

    LOGS.mkdir(exist_ok=True)
    log = LOGS / f"{run.name[:-3]}.log"
    started = time.time()
    state = state or RunState(run)
    proc = None
    def stop_child():
        if proc is None or proc.poll() is not None:
            return
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        except ProcessLookupError:
            pass
    try:
        proc = subprocess.Popen(argv, cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding='utf-8',
                                start_new_session=True)
        state.started(proc.pid)
        stdout, stderr = proc.communicate(input=stdin_text, timeout=timeout)
        state.update(status='FINALIZING')
        log.write_text(f"$ {argv[0]} … (exit {proc.returncode})\n\n--- stdout ---\n"
                       f"{stdout}\n--- stderr ---\n{stderr}", encoding="utf-8")
        code = proc.returncode
    except subprocess.TimeoutExpired:
        stop_child()
        proc.communicate()
        log.write_text(f"timeout after {timeout}s", encoding="utf-8")
        state.finish('TIMEOUT', reason='time limit reached')
        return run, f"FAIL timeout after {timeout}s (log: {log.relative_to(ROOT)})"
    except KeyboardInterrupt:
        stop_child()
        if proc is not None:
            proc.communicate()
        state.finish('CANCELLED', reason='operator interrupted run')
        raise
    except OSError as exc:
        stop_child()
        if proc is not None:
            proc.communicate()
        state.finish('FAILED', reason=type(exc).__name__)
        return run, f"FAIL could not start or record {tool}: {exc}"
    secs = int(time.time() - started)
    if code != 0:
        state.finish('FAILED', exit_code=code, reason='CLI returned an error')
        return run, f"FAIL exit {code} after {secs}s (log: {log.relative_to(ROOT)})"
    if run.checks_file:
        out = ROOT / run.output
        if not out.exists() or out.stat().st_mtime < started or out.stat().st_size == 0:
            state.finish('FAILED', exit_code=code, reason='required output not written')
            return run, (f"FAIL finished but did not write {run.output} "
                         f"(log: {log.relative_to(ROOT)})")
    state.finish('COMPLETED', exit_code=code, reason='CLI finished; required output checks passed')
    return run, f"OK   {run.output}  [{tool}, {secs}s]"


def run_batch(batch: list[Run], args) -> bool:
    todo = [r for r in batch if args.force or r.status() != "done"]
    for r in batch:
        if r not in todo:
            print(f"SKIP {r.name}: {r.output} already exists (use --force to re-run)")
    if not todo:
        return True
    print(f"\n▶ {len(todo)} run(s) in parallel: {', '.join(r.agent for r in todo)}")
    states = {r.name: RunState(r) for r in todo} if not args.dry_run else {}
    ok = True
    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as pool:
        for run, msg in pool.map(lambda r: execute(r, args.dry_run, args.timeout, states.get(r.name)), todo):
            print(f"  {run.name}: {msg}")
            ok &= not msg.startswith(("FAIL", "ERROR"))
    return ok


# --------------------------------------------------------------------------- modes
def doctor(runs: list[Run]) -> int:
    problems = 0
    providers = {r.provider for r in runs}
    checks = []
    if "anthropic" in providers:
        checks.append(("claude", ["claude", "auth", "status", "--text"], "claude auth login"))
    if "openai" in providers:
        checks.append(("codex", ["codex", "login", "status"], "codex login  (choose Sign in with ChatGPT)"))
    for name, argv, fix in checks:
        if not shutil.which(name):
            print(f"✗ {name} not installed")
            problems += 1
            continue
        try:
            res = subprocess.run(argv, capture_output=True, text=True, timeout=30)
            if res.returncode == 0:
                first = (res.stdout or res.stderr).strip().splitlines()[:1]
                print(f"✓ {name} signed in  {first[0] if first else ''}")
            else:
                print(f"✗ {name} not signed in → run: {fix}")
                problems += 1
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"✗ {name}: {exc}")
            problems += 1
    if (ROOT / ".git").exists():
        print("✓ git repository (Codex requires one; it also gives you a history of every agent's edits)")
    else:
        print("✗ not a git repository → run: git init && git add -A && git commit -m init")
        problems += 1
    index = ROOT / "kickoffs" / "INDEX.md"
    sources = list((ROOT / "agents").glob("*.md")) + list((ROOT / "config").glob("*.yaml"))
    if not index.exists():
        print("✗ not built → run: python3 scripts/build.py")
        problems += 1
    elif max(p.stat().st_mtime for p in sources) > index.stat().st_mtime:
        print("✗ sources changed since the last build → run: python3 scripts/build.py")
        problems += 1
    else:
        print("✓ build is up to date")
    brand = (ROOT / "knowledge" / "kyu-brand.md").read_text(encoding="utf-8")
    todo = brand.count("TO CONFIRM")
    print(("✓" if todo == 0 else "!") + f" knowledge/kyu-brand.md: {todo} field(s) still TO CONFIRM")
    print("\nOK" if problems == 0 else f"\n{problems} problem(s) to fix")
    return 1 if problems else 0


def list_runs(runs: list[Run]) -> int:
    marks = {"done": "✓", "pending": "·", "append": "~"}
    current = None
    for r in runs:
        if r.stage != current:
            current = r.stage
            print(f"\n{r.stage} {r.stage_name}{'  (manual)' if r.manual else ''}")
        tool = "claude" if r.provider == "anthropic" else "codex "
        print(f"  {marks[r.status()]} step {r.step}  {tool}  {r.agent:<22} → {r.output}   [{r.name}]")
    print("\n✓ output exists   · pending   ~ appends to a shared file")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--doctor", action="store_true")
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--stage", help="stage id, e.g. 02")
    mode.add_argument("--run", help="one kickoff file name, e.g. 02-1-1-generator-a.md")
    ap.add_argument("--step", type=int, help="with --stage: run only this step")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args()

    try:
        runs, stages = load_runs()
        if args.doctor:
            return doctor(runs)
        if args.list:
            return list_runs(runs)
        if args.run:
            name = args.run if args.run.endswith(".md") else args.run + ".md"
            match = [r for r in runs if r.name == Path(name).name]
            if not match:
                print(f"unknown kickoff {name}; see kickoffs/INDEX.md")
                return 1
            args.force = True  # an explicit single run always runs
            return 0 if run_batch(match, args) else 1

        sid = args.stage.zfill(2)
        if sid not in stages:
            print(f"unknown stage {sid}")
            return 1
        stage = stages[sid]
        if stage.get("manual"):
            print(f"stage {sid} is manual: run its kickoffs one at a time with --run "
                  "as items come out of production (see PIPELINE.md)")
            return 1
        stage_runs = [r for r in runs if r.stage == sid]
        steps = sorted({r.step for r in stage_runs})
        if args.step:
            steps = [s for s in steps if s == args.step]
        for s in steps:
            if not run_batch([r for r in stage_runs if r.step == s], args):
                print(f"\n■ stopped: step {s} of stage {sid} has failures; fix them and re-run "
                      "(finished runs are skipped)")
                return 1
        print(f"\n■ stage {sid} finished.")
        if stage.get("gate"):
            print(f"  gate: {stage['gate']}")
        if stage.get("checkpoint"):
            print(f"  client checkpoint: {stage['checkpoint']}")
        print("  The runner does not start the next stage. Review the outputs, then run it yourself.")
        return 0
    except BuildError as exc:
        print(f"ERROR {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
