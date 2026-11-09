KICKOFF
agent: qc-supervisor
role: qc-supervisor
stage: 08 — Visual approvals and production (human-driven, looped per item)
mode: Stage 8 audio and Arabic text QC
params: -
inputs:
  - work/11-qc-spec.md
  - work/production/edit-check/
output: append to work/12-qc-log.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: No video before casting/look PASS, whole-pack LOCK, quality PASS, human visual approval 2V and QC pre-video PASS; each input needs KEYFRAME PASS; bulk video needs MOTION PILOT PASS
