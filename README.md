# Kyu Creative Studio — The Creative Agency's Brain

For a clear picture of the team, the libraries, the inputs and their current status, see the [system map](SYSTEM-OVERVIEW.md).

**Language:** project files and agent outputs (analysis, reviews, logs) are in English. The ad's audience-facing content (hooks, dialogue, voice-over, on-screen text, captions) stays in Saudi Arabic. Arabic quotes are kept with an English translation.

Nine agents in eight roles work from the command line **on your subscriptions, with no API key at all**:
- Claude agents via **Claude Code** (sign in with a Claude account)
- ChatGPT agents via **Codex CLI** (sign in with a ChatGPT account)

Each agent reads its inputs and writes **its own file** in `work/`, and the runner verifies that the file was written.

## Who writes which file

| Agent | Tool | Files it writes |
|---|---|---|
| creative-director | Claude Code | `01-brief.md`, `06-concept-decision.md`, `09-casting-approval.md`, `09-quality-approval.md`, `13-final.md` |
| researcher-strategist | Claude Code | `02-research-product.md`, `02-research-audience.md`, `02-research-competitors.md`, `02-research-library.md`, `02-research-trends.md`, then `02-research.md` |
| generator-a | Codex | `03-concepts-A.md` |
| generator-b | Claude Code | `03-concepts-B.md` |
| critic | Claude Code | `04-tournament-juror.md`, `04-tournament-scroller.md`, `04-tournament-shopper.md`, `04-tournament-brand.md`, then `04-tournament.md`; adds its verdict inside the script files; `10-review-critic.md` |
| producer | Claude Code | `05-feasibility.md`; adds the plan check inside `09-shotlist.md`; `10-review-producer.md` |
| writer | Codex | `07-characters.md`, `08-script-v1-a.md`, `08-script-v1-b.md` |
| dop | Codex | `09-shotlist.md`; adds prompt fixes in `12-qc-log.md` |
| qc-supervisor | Claude Code | `11-qc-spec.md`, `11-video-readiness.md`, `12-qc-log.md`, `10-review-qc.md` |

All agents append their decisions to `decision-log.md` (append only, no edits).

**Files you write:**
- `00-client-notes.md`: what the client said.
- `08-script-approved.md`: a copy of the script that passed the gate.
- `work/production/`: the stage 08 images.
- `work/cut/`: the cut's frames for review.

## First-time setup

```bash
# 1) Tools and sign-in (one time)
claude auth login          # with a Claude account (subscription)
codex login                # choose Sign in with ChatGPT

# 2) The project
cd kyu-creative-studio
pip install pyyaml
git init && git add -A && git commit -m "init"     # Codex needs a git repo, and it gives you a history of every change
python3 scripts/build.py
python3 scripts/run.py --doctor                    # checks everything before you start
```

## Daily use

```bash
python3 scripts/run.py --list               # all steps and their status (✓ done · remaining)
python3 scripts/run.py --stage 01           # a full stage; parallel steps run together
python3 scripts/run.py --stage 06 --step 2  # a single step of a stage
python3 scripts/run.py --run 08-7-1-qc-supervisor.md   # check a shot's video after it passes the approval gates
python3 scripts/run.py --stage 02 --dry-run # shows the commands without running them
```

**How the runner behaves:**
- **Skipping:** it skips any run whose file already exists. To rerun it, use `--force`.
- **On failure:** it stops if an agent fails or doesn't write its file, and saves the log in `logs/`.
- **End of stage:** it **always stops** and shows the gate or the client-approval point. It never starts the next stage by itself.
- **Production stage 08:** manual. It starts with choosing the characters and the visual look, then the sheets, the quality sample, the client's visual approval, and the face and wardrobe consistency check before any video. That is followed by shot-frame approval and a motion test before scaling up. The command order is in `PIPELINE.md`; each review is run on its own with `--run`.
- **Parallelism:** `--parallel 3` by default. Lower it if you hit your subscription limits, because every parallel run draws on the same subscription.

**Or from inside Claude Code:** open `claude` in the folder. The main session knows from `CLAUDE.md` that it is the orchestrator, so it runs the Claude agents as subagents, and the Codex agents via `scripts/run.py --run`.

## Monitoring the agents from Terminal (macOS / Ubuntu / WSL)

On the Mac, double-click `scripts/monitor.command`; a separate monitoring window opens.
Or open Terminal inside the project folder, then run:

```bash
python3 scripts/monitor.py --watch
```

The screen always shows all nine agents: each agent's name, its provider, an English description of its role, and its status and task.
While running via `scripts/run.py`, it shows the stage, the required file, the duration and the process ID; the
last result stays visible after it finishes. If several instances of the researcher run, for example, each instance's task is shown.
It refreshes every second. `Ctrl+C` closes only the monitor screen, and does not stop the agents.

- A single snapshot: `python3 scripts/monitor.py`.
- All of your Claude and Codex sessions on the machine, including those outside the project:
  `python3 scripts/monitor.py --watch --all`.
- The role name appears when the runner passes it: Claude via `--agent`, and Codex via the run's output file.
  A session that doesn't specify a role appears as `session`.
- `IDLE` idle; `QUEUED` waiting its turn; `RUNNING` a process has started; `LAST` the last recorded run.
  `COMPLETED` means the run finished and the required file was verified; it does not grant a creative PASS or a gate approval.
- `ACTIVE` means the process exists; it may be working or waiting for input. A process disappearing does not prove it succeeded;
  check the run's result and its file. The screen does not show the prompt text or the contents of client files.
- Assigned tasks come from the stage's run file, not from a guessed description of what the model is thinking.
  The runner keeps the text details until completion; this is not a live stream of internal reasoning.
- Small run metadata is saved in `logs/agent-runs/`, without the prompts or responses.
- The Codex app's internal agents don't appear as separate CLI processes; follow them from the conversation.
- The old processes-only view: `python3 scripts/monitor.py --watch --processes-only`.
- The `scripts/run.py --list` command shows whether output files exist, not a list of the agents working right now.

### Testing responses while keeping all names visible

Leave the monitor screen open, and from a second Ubuntu window run:

```bash
python3 scripts/test_agents.py
```

The nine agents' names appear from the start of the test: `QUEUED` waiting, `RUNNING` working,
then `PASS` or `FAIL` or `TIMEOUT`. The names and results stay visible after the processes finish.
The test screen neither saves nor shows the responses; it saves only run statuses and model data.
Each name's test is isolated and loads no production role files or client data, and it respects the pinned Codex model and effort.
The test runs in batches of three, and the number can be changed via `--parallel`.
If the screen was open before it was updated, close the monitor with `Ctrl+C` and rerun the monitor command once.
The results are saved locally in `logs/agent-tests-latest.json` even if you close the monitor window.

## Current assignment

| Agent | Model |
|---|---|
| creative-director, producer, researcher-strategist, generator-b, critic, qc-supervisor | Claude |
| generator-a, writer, dop | GPT-6 Astra — Extra High (`xhigh`) via Codex |

The `model` and `model_reasoning_effort` settings are pinned for the three Codex agents in `config/agents.yaml`,
and the runner passes them explicitly on every run.

The rule: **whoever makes doesn't judge.** `build.py` refuses to build if the critic and the writer, or the QC supervisor and the director of photography, are on the same model. After the comparison test (`bakeoff/`), edit `config/agents.yaml` and rebuild.

## Structure

```
agents/            ← source: the shared base + one file per role (edit here)
config/            ← agents.yaml (the model per agent) and pipeline.yaml (stages and parallelism)
knowledge/         ← Kyu file, hook taxonomy, breakdown template, trends, technical test, library
work/              ← agent outputs and logs
bakeoff/           ← blind comparison test
scripts/           ← build.py (build and validate), run.py (run), bakeoff_blind.py
── generated (don't edit by hand) ──
CLAUDE.md, AGENTS.md, .claude/agents/, codex/, kickoffs/
```

## Warnings

- **No keys:** there is no API key anywhere in the project. Treat the saved sign-in files (`~/.codex/auth.json` and Claude Code's credentials) like a password, and don't upload them anywhere.
- **Permissions:** Claude agents edit files inside the folder only (`acceptEdits`), and Codex inside the folder only and without internet (`workspace-write`). No permission-bypassing mode is used.
- **Client data:** it goes to two providers. Record Kyu's approval in `kyu-brand.md`. Mohammed Omar appears in the ad with his consent (recorded in `kyu-brand.md`, DL-016); no customer data in the POC.
- **Compliance:** reviewing Saudi advertising regulations and TikTok's labeling of generated content is a human responsibility before publishing.
