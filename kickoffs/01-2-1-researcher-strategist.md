KICKOFF
agent: researcher-strategist
role: researcher-strategist
stage: 01 — Research and strategy
mode: SYNTHESIS
params: -
inputs:
  - work/01-brief.md
  - work/02-research-product.md
  - work/02-research-audience.md
  - work/02-research-competitors.md
  - work/02-research-library.md
  - work/02-research-trends.md
output: work/02-research.md
rules: Read the shared foundation and your role file. Write only the output named above. End with the HANDOFF block.
gate after this stage: creative-director reads work/02-research.md; REVISE if the insight fails its test
