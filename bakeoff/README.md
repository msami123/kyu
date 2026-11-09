# BAKE-OFF: which model writes better Saudi comedy?

Goal: decide by evidence, not by brand, which model gets the Writer role (and therefore which
models get the Creative Director and Critic roles, which must differ from the Writer's).
Time: about 1 hour.

## Steps
1. Give `task.md` to both models, unchanged, in fresh conversations with no other context.
   Save the answers as `answers/claude.md` and `answers/gpt.md`.
2. Run `python3 scripts/bakeoff_blind.py` from the project root. It mixes the hooks and the
   scenes from both answers, removes any trace of the source, and writes:
   - `blind/sheet.md` — what the judges see (items numbered in random order)
   - `blind/key.json` — which item came from which model (do not open until scoring is done)
3. Judges: you plus 2–3 Saudi friends or colleagues. Not the models. Each judge fills
   `scoring-sheet.md` independently, without discussing.
4. Run `python3 scripts/bakeoff_blind.py --reveal` to total the scores per model.
5. Write the result in `results.md` and update `config/agents.yaml`:
   - Writer = the winner.
   - Creative Director and Critic = the other provider.
   Then run `python3 scripts/build.py`.

Also compare character-sheet images: same character description to both image tools; judge
which sheet is clearer, more consistent across views and easier to keep consistent.
