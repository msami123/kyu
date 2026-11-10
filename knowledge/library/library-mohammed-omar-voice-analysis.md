# Mohammed Omar — Recording and Performance Voice Analysis v1

## Result and its limits

**A local measurement-based analysis of the recording is complete; a listening review of the tone is not.**

Source: [the clip the user selected](https://www.youtube.com/watch?v=6UnyBbimn0I), published 2025-11-26. Decoded audio duration 98.389 seconds. YouTube metadata classifies the selected track as Arabic; we do not have a raw microphone recording or an isolated speech track. The analysis concerns this published version and does not determine Mohammed Omar's natural voice in all conditions.

After the user's explicit consent to sending to OpenAI for this analysis only, the opening sample (8 seconds) was passed to the audio API. The API returned: `audio content omitted because you do not support audio input`. So the audio did not become listenable by the model, and we do not claim to have heard it. The analysis below is based on signal measurements, an earlier automatic transcript, and on-screen texts examined previously. No further upload to any other party and no voice cloning.

## What did we learn from the measurements?

| Aspect | Result | What it means and what it does not |
|---|---|---|
| Speech density | 256 words per the automatic transcript's segmentation, about 156 words/minute over the full clip duration | A rough estimate of speech density; not a precise measure of syllables or pure articulation rate |
| Pitch variation | 10th–90th percentiles of the Praat estimate: about 202–339 Hz; median about 275 Hz | Describes the portions the pitch analyzer selected in this recording; does not establish the natural pitch of the voice or its type |
| Independent check | An independent periodic-difference analyzer agreed within one semitone (half a musical step) in 96.4% of shared frames with a voiced estimate; these agreeing frames make up 47.3% of the file | The agreement supports computational stability in these portions; it does not separate speech from possible music and does not rule out shared errors |
| More conservative joint estimate | The central range of the agreeing frames is about 225–345 Hz, with a median of about 285 Hz | The difference from the Praat calculation is due to different accepted frames; the two numbers are not merged as if they were one vocal fact |
| Digital loudness | Overall RMS about −11.9 dBFS, with clear variation between short windows | This is the loudness of a file published after recording/editing; it does not indicate how much the speaker shouted or his voice level in the room |
| Segments | Median estimated pitch for the opening about 247 Hz, for the cleaning-products bundle offer about 291 Hz, and for the diwaniya segment about 270 Hz | A difference in estimates between segments; not sufficient on its own to name a specific emotion |

[LIB:assets/2026-11-09/mohammed-omar-audio-v1/measurements-v1.json] [LIB:assets/2026-11-09/mohammed-omar-audio-v1/pitch-crosscheck-v1.json]

Terminology note: the agreement criterion used is **one semitone, i.e. half a musical step**. The 96.4% agreement rate does not mean that 96.4% of the file was examined precisely, nor is it our perceptual confidence level.

## Reading of the performance permitted by the evidence

- **Sequential information flow:** the text moves between product, quantity and value, and the measurement estimates an average of about 156 words/minute. The content density in this clip can be described; we do not infer from it that he always speaks at a constant speed. [LIB:library-kyu-white-friday.md#4-time-structure]
- **Variation in the audio signal:** differences in estimated pitch and energy appear between segments. [ASSUMPTION] This is consistent with an offers performance with varied emphasis, but it does not by itself establish an "enthusiastic" or "friendly" tone; those descriptions require listening.
- **Linguistic closeness to the addressee:** the phrasing of the address in the on-screen text and the transcript is colloquial and direct, and the diwaniya part shifts to a social register. This is a textual observation independent of hearing the audio. It does not determine the origin of the dialect or the pronunciation of letters. [LIB:library-kyu-white-friday.md#5-strategy]
- **No guessed timbre description:** roughness, hoarseness, nasality, warmth, clarity, how much smile is in the voice, and degree of shouting: unresolved. We do not infer health, personality or biometric identity from the voice.

## Four temporary samples for later review

| Sample | Time | Suggested check once listening is available |
|---|---|---|
| [Opening](assets/2026-11-09/mohammed-omar-audio-v1/01-opening.wav) | 0–6.64 s | Placement of stress and how the denial relates to the reveal; the actual pauses |
| [Return explanation](assets/2026-11-09/mohammed-omar-audio-v1/02-reassurance.wav) | 23.28–28.60 s | Does the performance actually shift to reassurance? We do not assume so from the words alone |
| [Diwaniya](assets/2026-11-09/mohammed-omar-audio-v1/03-diwaniya.wav) | 38.12–56 s | The difference between calling out to the audience, explaining the offer, and the social phrase |
| [Cartons offer](assets/2026-11-09/mohammed-omar-audio-v1/04-cartons.wav) | 56–68 s | Rhythm of counting and pausing before showing the quantity, and how the voice relates to the action |

The samples are mono 16kHz PCM for analysis, with no pitch change, denoising or voice separation. The original stereo 48kHz M4A is kept at `work/research/2026-11-09-youtube/6UnyBbimn0I/source-audio.m4a`. The timings are taken from the transcript/image review and are not validated phonetic boundaries. The prices in this recording are historical.

## Preliminary writing and performance recommendations

These are development recommendations [ASSUMPTION], not a voice imitation or a claim to have mastered his tone:

1. Write direct colloquial sentences, and separate product, quantity and value into units the viewer can understand.
2. Assign one clear word or value for emphasis, then leave room for it to land; do not put every sentence at the same level of emphasis.
3. Leave room in the script for the comedic reaction; the density of an offers bulletin does not automatically transfer to a narrative ad.
4. Match the counting, pointing and product reveal to the performance, with the actual timing to be reviewed once listening is available.
5. Do not tune a machine-generated voice to the Hz average mentioned; the number is tied to the published version and the analyzer's constraints, and is not a voiceprint or a cloning recipe.

## Analysis method and reviewability

Praat autocorrelation was run at 65–500 Hz, then repeated at 75–400 Hz as a test, with a periodicity threshold of 0.6 and a 10ms step. An independent comparison based on cumulative mean normalized difference was used, with a 60ms window and a 20ms step. The measurements and tracks were saved in `work/research/2026-11-09-youtube/audio-analysis/`, and the summaries and source statement in the samples folder.

We did not separate the voice from any possible background, and we did not use jitter/shimmer indicators to describe voice timbre from this mix. Not finding low-energy gaps of 150ms in a single test does not prove there are no speech pauses; the background may continue during a pause. We did not use this to build a judgment on delivery.

Confidence: High for the file duration, the energy calculation and the word count of the transcript itself; Medium for the pitch estimate of the agreeing portions; Low for generalizing the rate to his natural speaking speed; unverified for the auditory description, timbre and spoken dialect.

## Consent

The user reported Mohammed Omar's consent to the request to analyze the voice and tone, then explicitly consented to sending this clip's audio to OpenAI **for this analysis only**. Both statements were recorded in `knowledge/kyu-brand.md` without turning them into a general consent to voice cloning, publishing, or processing by Anthropic. No separate consent document was presented. [BRAND:Scoped audio-analysis permission — 2026-11-09]

### HANDOFF
- Stage completed: measurement-based analysis of the recording; the listening review is incomplete because audio input is not supported.
- Output file(s) written: `knowledge/library/library-mohammed-omar-voice-analysis.md`; four samples, measurements and a version statement in `knowledge/library/assets/2026-11-09/mohammed-omar-audio-v1/`; measurement files in `work/research/2026-11-09-youtube/audio-analysis/`; updates to the consent record, the index and the character file.
- Next agent and what they need from this output: a reviewer who can actually listen uses the temporary samples and assesses timbre, pronunciation and pauses; do not give the voice a PASS from these measurements alone.
- Open questions for the human (max 3, each with a recommended answer): no additional consent is needed for the specified analysis; the OpenAI consent is recorded. The remaining blocker is technical (listening support), not a lack of permission.
- Decision log lines added: DL-010.
