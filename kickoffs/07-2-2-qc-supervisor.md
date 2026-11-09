KICKOFF
agent: qc-supervisor
role: qc-supervisor
stage: 07 — Visual plan
mode: Stage 7 locked QC spec
params: -
inputs:
  - work/07-characters.md
  - work/08-script-approved.md
  - work/09-shotlist.md
  - knowledge/kyu-brand.md
output: work/11-qc-spec.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: producer PASS on the production plan
