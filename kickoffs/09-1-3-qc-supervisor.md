KICKOFF
agent: qc-supervisor
role: qc-supervisor
stage: 09 — Review
mode: Stage 9 full-ad continuity pass
params: -
inputs:
  - work/cut/
  - work/11-qc-spec.md
  - work/11-video-readiness.md
  - work/09-quality-approval.md
  - work/production/references/
  - work/production/quality-sample/
output: work/10-review-qc.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
client checkpoint after this stage: Client reviews the cut with the three reviews (checkpoint 3)
