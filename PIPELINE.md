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
08 Production ─── casting/look → CD PASS → full sheets → QC LOCK
                  └ quality sample → CD PASS → human 2V + QC pre-video PASS
                  └ keyframe PASS → motion pilot PASS → per-shot video QC → edit / dop fix ↺
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
| Checkpoints 1, 2, 2V and 3 | Show outputs to the client/delegate and record their actual answers. 2V approves exact casting/look/benchmark versions before video |
| After the script gate PASS | Copy the passing script to `work/08-script-approved.md` |
| Stage 08 casting/look | Render candidates/look boards in work/production/casting/; obtain CD selection before full sheets |
| Stage 08 references | Put masters, clean views, contact sheets and manifest.md in work/production/references/; obtain whole-pack QC LOCK |
| Stage 08 quality/2V | Render benchmark and continuity stills in work/production/quality-sample/; obtain CD quality approval, record human visual approval and run QC pre-video readiness |
| Stage 08 pilot/shots | Obtain KEYFRAME PASS before animation. After pre-video PASS, generate/review one pilot; bulk video waits for MOTION PILOT PASS. Supply full playback evidence plus sampled frames/transcript for each shot |
| Stage 09 | Put one frame per shot in edit order + notes.md in work/cut/ |

### Casting, visual quality and continuity before video
Stage 7 plans casting/look, full sheets, the quality benchmark and continuity tests in
work/09-shotlist.md. The Producer checks feasibility; QC writes acceptance criteria. Plans and
prompts do not count as rendered images or approval. Stage 8 is manual: invoke only the relevant
kickoff after actual inputs are ready.

| Order | Kickoff | Evidence and outcome |
|---|---|---|
| 1 | 08-1-1-creative-director.md | Actual casting/look images -> selected versions in work/09-casting-approval.md; PASS before full sheets |
| 2 | 08-2-1-qc-supervisor.md | Complete sheets from selected masters -> R1-R11 checks and whole-pack LOCK in work/12-qc-log.md |
| 3 | 08-3-1-creative-director.md | Actual project benchmark/close-up -> work/09-quality-approval.md; CD PASS |
| 2V | Human approval | Show selected characters/look/benchmark; operator records real response and exact versions in work/production/approvals/visual-approval.md |
| 4 | 08-4-1-qc-supervisor.md | Benchmark/continuity stills, prior approvals and 2V -> work/11-video-readiness.md; PASS before ANY video |
| 5 | 08-5-1-qc-supervisor.md | Actual pilot or later shot input frame -> KEYFRAME PASS before animation |
| 6 | 08-6-1-qc-supervisor.md | Representative pilot clip, sampled frames and full playback evidence -> MOTION PILOT PASS before bulk video |
| 7 | 08-7-1-qc-supervisor.md | Each generated shot with current keyframe/asset approvals -> per-shot video QC |
| Repair loop | 08-8-1-dop.md | Review failure -> scoped repair/new version, then rerun the affected gate; never self-approve |
| 9 | 08-9-1-qc-supervisor.md | Edit screenshots, dialogue and available audio/playback evidence -> Arabic text/audio review |

For a repair, the operator puts a request in work/production/repair-request/ naming the failed
report/path/version, affected image paths, required corrections and current attempt count. The
DoP reads the relevant report and appends repairs to the QC log; later approvals may not exist yet.

Manifests record actual files, asset versions and tool/settings when available. Casting defaults
to contemporary Saudi context with concrete visible features and styling; do not infer ethnicity
or nationality from a face or use ethnic exclusion as a quality criterion. The human approval
records who approved, date, exact character/look/benchmark versions, actual answer and scope.
Silence or generic permission to proceed is not a visual approval.

Continuity stills cover EVERY principal character: close-up, changed angle, required expression,
wardrobe-visible view and relevant interaction. Character-free films give reasoned N/A for those
checks and still test product/place/style. Independent QC compares face/hair, wardrobe cut/colour/
fabric and accessory sides to the selected masters, and technical quality to the benchmark.

No video, including the pilot, before all visual gates and QC pre-video PASS. The first video is
one approved pilot; later production needs MOTION PILOT PASS plus every shot's own KEYFRAME PASS.
Stills do not prove temporal stability: inspect full playback or obtain a named/date/versioned
human review with timecoded observations. Missing media/evidence remains PENDING.

Material changes to faces, outfits, style, benchmark or workflow reopen affected approvals and
dependent work. Never run repair and review of the same asset simultaneously. Sheets and upstream
identity/wardrobe defects cannot pass as FIX IN EDIT. After 3 review loops, escalate with two
options and a recommendation under the existing rules.

These are mandatory operator/agent gates. The runner requires individual --run calls for Stage 8;
it does not parse verdicts, inspect images or block external generation tools automatically.
File existence or a successful process exit is not an artistic or QC pass.

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
| 4 | 06 gate → 07 → 08 casting/look, sheets, benchmark and human visual checkpoint 2V |
| 5 | 08 pre-video gate → motion pilot → shot production with per-shot checks |
| 6 | Edit, 08 audio/text QC, 09 (client checkpoint 3) |
| 7 | 10 final, "how it was made" presentation |
