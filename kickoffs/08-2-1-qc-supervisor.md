KICKOFF
agent: qc-supervisor
role: qc-supervisor
stage: 08 — Production (human-driven, looped per item)
mode: Stage 8 per-shot QC (repeat for every attempt)
params: -
inputs:
  - work/11-qc-spec.md
  - work/09-shotlist.md
  - work/production/current-shot/
output: append to work/12-qc-log.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
