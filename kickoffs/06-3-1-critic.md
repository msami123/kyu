KICKOFF
agent: critic
role: critic
stage: 06 — Characters, script, punch-up
mode: B
params: -
inputs:
  - work/07-characters.md
  - work/08-script-v1-a.md
  - work/08-script-v1-b.md
  - work/06-concept-decision.md
  - work/01-brief.md
output: append to each script file
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: critic Mode B returns PASS on one script (loop REVISE up to 3 times; then escalate)
