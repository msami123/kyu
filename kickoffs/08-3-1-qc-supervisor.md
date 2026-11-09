KICKOFF
agent: qc-supervisor
role: qc-supervisor
stage: 08 — Production (human-driven, looped per item)
mode: Stage 8 audio and Arabic text QC
params: -
inputs:
  - work/11-qc-spec.md
  - work/production/edit-check/
output: append to work/12-qc-log.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
