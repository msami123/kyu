# PRODUCTION FOLDERS (filled by the human during stage 08)

Keep assets versioned. Archive current-shot files by shot/attempt before preparing the next item;
do not delete reviewed evidence. Agents write only their kickoff outputs.

- casting/        candidate portraits/full-body outfit views, look boards and manifest.md.
                   Give each candidate/look an ID/version and actual source paths.
- references/     selected masters, all character/product/prop/location sheets and style boards,
                   clean views, contact sheets, original product sources and manifest.md.
- quality-sample/ actual project benchmark hero frame/close-up and continuity stills for every
                   principal character: changed angle, expression, wardrobe-visible view and
                   relevant interaction. Record exact source versions and tool/settings.
- approvals/      visual-approval.md: checkpoint 2V. Record reviewer/delegate, date, actual answer,
                   selected character/look/benchmark versions and scope. Missing, rejected or
                   superseded approval is not permission to generate video.
- motion-pilot/   pilot clip, first/middle/last frames, transcript when applicable, manifest and
                   full playback review: inspector/date/clip version/timecoded observations.
- current-shot/   proposed keyframe BEFORE animation; then clip, shot-<n>-first.png,
                   shot-<n>-middle.png, shot-<n>-last.png, transcript.txt and playback evidence.
                   Manifest names shot/attempt, source versions and current gate verdicts.
- repair-request/ request naming failed review report/path/version, affected image paths,
                   exact corrections and attempt count. The DoP reads that report, repairs
                   separately from reviewers, then the failed gate is rerun.
- edit-check/     screenshots of every Arabic overlay, final dialogue transcript and available
                   audio/full playback evidence for the edit review.

The operator creates these folders when needed; this README does not imply assets or approvals
exist. Use simple names and preserve reviewed versions.

Order: CD casting/look PASS -> whole-pack QC LOCK -> CD quality PASS -> human visual approval
and QC pre-video PASS -> KEYFRAME PASS -> motion pilot PASS -> bulk video with per-shot reviews.
Run manual kickoffs from PIPELINE.md; repairs and reviews must run separately.
