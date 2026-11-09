KICKOFF
agent: writer
role: writer
stage: 06 — Characters, script, punch-up
mode: 6b script + 6c punch-up
params: VARIANT=a
inputs:
  - work/07-characters.md
  - work/06-concept-decision.md
  - work/02-research.md
  - knowledge/kyu-brand.md
output: work/08-script-v1-a.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: critic Mode B returns PASS on one script (loop REVISE up to 3 times; then escalate)
