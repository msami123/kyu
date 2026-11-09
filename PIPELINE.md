# PIPELINE

The machine-readable version is `config/pipeline.yaml`; `scripts/build.py` renders one ready
kickoff message per run into `kickoffs/`. This file explains how to run it.

## 1. Flow at a glance

```
00 Brief ─────────────── creative-director ──────────────────────────── [client checkpoint 1]
01 Research   ┌ researcher (product)      ┐
              ├ researcher (audience)     │ parallel
              ├ researcher (competitors)  │ ──► researcher (SYNTHESIS) ── gate: creative-director
              ├ researcher (library)      │
              └ researcher (trends)       ┘
02 Ideation   ┌ generator-a  (L1–L3)  ┐ parallel, two models
              └ generator-b  (L4–L6)  ┘
03 Tournament ┌ critic A1 juror    ┐
              ├ critic A1 scroller │ parallel ──► critic A2 aggregation (Borda) ── top 3
              ├ critic A1 shopper  │
              └ critic A1 brand    ┘
04 Feasibility ── producer ─────────────────────────────────────────── gate: GO on ≥ 1 concept
05 Decision ───── creative-director ────────────────────────────────── [client checkpoint 2]
06 Writing ────── writer 6a characters
                  ┌ writer script variant a ┐ parallel ──► critic B (script gate) ── loop ≤ 3
                  └ writer script variant b ┘
07 Visual plan ── dop ──► ┌ producer plan check ┐ parallel ── gate: producer PASS
                          └ qc locked spec      ┘
08 Production ─── human generates ──► qc per item ──► PASS → edit / REGENERATE → dop fix ↺
09 Review         ┌ critic C        ┐
                  ├ producer specs  │ parallel ─────────────────────────── [client checkpoint 3]
                  └ qc continuity   ┘
10 Final ──────── creative-director
```

## 2. Kickoff message format
Every run starts with exactly one kickoff message (see `kickoffs/`):

```
KICKOFF
agent: <agent id>
role: <role id>
stage: <stage id> — <stage name>
mode: <mode>
params: <KEY=value; …>
inputs:
  - <path>
output: <path or instruction>
rules: Read the shared foundation and your role file. Write only the output named above.
       End with the HANDOFF block.
```

## 3. Running a run (subscriptions only, no API keys)
`scripts/run.py` runs every kickoff with the right CLI; each agent writes its own file.

| Provider | CLI and login | Command the runner uses |
|---|---|---|
| anthropic | Claude Code, `claude auth login` | `claude -p "<kickoff>" --agent <id> --permission-mode acceptEdits` |
| openai | Codex CLI, `codex login` (Sign in with ChatGPT) | `codex exec -C <project> --sandbox workspace-write -` with the role prompt `codex/<id>.md` + kickoff on stdin |

- Claude Code loads `CLAUDE.md` and the subagent definition in `.claude/agents/<id>.md`.
- Codex loads `AGENTS.md` automatically and receives `codex/<id>.md` in the prompt.
- Codex needs the project to be a git repository (`git init`).
- After each run the runner checks that the output file was written; logs go to `logs/`.
- Runs in one step are launched together (`--parallel`, default 3).

Alternatively, open `claude` in the project: the main session is the orchestrator (see
CLAUDE.md), runs Claude-side agents as subagents and Codex-side agents through
`python3 scripts/run.py --run <kickoff>`.

## 4. Human actions the pipeline expects
| When | You do |
|---|---|
| Before stage 00 | Write the client's words in `work/00-client-notes.md`; fill `knowledge/kyu-brand.md` |
| Before stage 01 | Put deconstructions in `knowledge/library/`, trends in `knowledge/trends-snapshot.md`, comment extracts in `knowledge/comments/` |
| Day 1 | Run the tech test (`knowledge/tech-test.md`) and the bake-off (`bakeoff/`) |
| Checkpoints 1–3 | Show the output to the client; paste their answer back to the creative-director |
| After the script gate PASS | Copy the passing script to `work/08-script-approved.md` |
| Stage 08 | Generate in the tools; put 3 frames per shot (first, middle, last) + transcript.txt in work/production/current-shot/, then run the QC kickoff with --run |
| Stage 09 | Put one frame per shot in edit order + notes.md in work/cut/ |

## 5. Loop limits and escalation
- Any gate: maximum 3 REVISE loops. Then stop: the gate-keeper writes the two best options and
  a recommendation, and you decide.
- Per shot: maximum 4 generation attempts, then the DoP's fallback shot.
- RESTART from the script gate goes back to stage 06 (rewrite) or stage 02/05 (new concept),
  as the Critic names.

## 6. Suggested timebox for the POC week
| Day | Stages |
|---|---|
| 1 | Setup, tech test, bake-off, library deconstructions |
| 2 | 00 → 01 (client checkpoint 1) |
| 3 | 02 → 05 (client checkpoint 2) → 06 |
| 4 | 06 gate → 07 → 08 starts (character sheets and hook shot first) |
| 5 | 08 production |
| 6 | Edit, 08 audio/text QC, 09 (client checkpoint 3) |
| 7 | 10 final, cutdown, "how it was made" presentation |
