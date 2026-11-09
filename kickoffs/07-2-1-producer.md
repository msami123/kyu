KICKOFF
agent: producer
role: producer
stage: 07 — Visual plan
mode: Stage 7 production plan check
params: -
inputs:
  - work/09-shotlist.md
  - work/07-characters.md
  - knowledge/tech-test.md
output: append to work/09-shotlist.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: producer PASS on the production plan
