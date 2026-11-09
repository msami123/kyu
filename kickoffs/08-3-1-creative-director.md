KICKOFF
agent: creative-director
role: creative-director
stage: 08 — Visual approvals and production (human-driven, looped per item)
mode: Stage 8B quality benchmark approval (actual project stills; request human checkpoint 2V)
params: -
inputs:
  - work/01-brief.md
  - work/09-shotlist.md
  - work/09-casting-approval.md
  - work/12-qc-log.md
  - work/production/references/
  - work/production/quality-sample/
output: work/09-quality-approval.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: No video before casting/look PASS, whole-pack LOCK, quality PASS, human visual approval 2V and QC pre-video PASS; each input needs KEYFRAME PASS; bulk video needs MOTION PILOT PASS
