# QC Review (Limited-Scope Draft) — CHAR-MO-v01

- Role: qc-supervisor (Claude), independent visual-match review. No creative judgement.
- Type: SCOPED DRAFT QC. Not a LOCK and not an approval, and not a permission for any generation or video.
- The label "Mohammed Omar" is an asset label only. I did not identify any person and did not verify identity or ethnic origin. The judgement here is on the visible match to the reference and the consistency of rendering across images.
- I did not read any other review of this sheet (the creative director's review or others).

## Status

| Item | Status |
|---|---|
| Draft verdict | **REVISE** |
| Production status | **PENDING**: There is no casting/look approval, no human visual approval (2V) and no quality benchmark, and none of them was examined |
| QC for the full pack | **NOT LOCKED / PENDING**: This is a single character only, and there are no props, no locations, no style guide and no R12 |
| Video | Not permitted |

## 1. Scope and files actually opened with Read

Original sources (all opened):
- `knowledge/library/assets/2026-11-09/mohammed-omar-character-v1/01-6UnyBbimn0I-t018.png` (full body, front)
- `.../02-6UnyBbimn0I-t004.png` (front gesture)
- `.../03-6UnyBbimn0I-t010.png` (open palm)
- `.../04-6UnyBbimn0I-t026.png` (close face)
- `.../05-6UnyBbimn0I-t055.png` (smile)
- `.../06-6UnyBbimn0I-t036.png` (body angle/gesture)
- `knowledge/library/assets/2026-11-09/mohammed-omar-character-v1.jpg` (source board, carries the phrase "NOT A PRODUCTION LOCK")

Generated (all opened):
- `work/production/casting/CHAR-MO-v01/CHAR-MO-v01-sheet.jpg`
- The nine images in `.../views/`: `CHAR-MO-v01-01-front.png` to `CHAR-MO-v01-09-face-surprise.png`
- `work/production/casting/CHAR-MO-v01/manifest.json`

Not opened: `prompt.txt`, `request.md`, `generation-record.json`, `manifest.md`, `source/face-source.jpg`, `CHAR-MO-v01-sheet.png` and `CHAR-MO-v01-contact-sheet.png`.

## 2. Dimensions and limits of verification

- **Sheet JPG:** The read tool reported that the original is 2700×1910 (displayed at 2000×1415), which matches `sheet_dimensions` in the manifest. Actually verified.
- **The nine images:** The tool did not state their dimensions explicitly. The visible display size (about 1024×1536 for the body and 1254×1254 for the faces) agrees with the manifest, but **I did not verify them with an independent tool** (no Bash/identify in this session). Dimensions = manifest claim + visual consistency only.
- **The six sources:** Displayed at about 720×1280; they are compressed video frames. The tool did not report explicit dimensions.
- **Pixels ≠ detail:** The 1024×1536 full images show the face at only about 110–130 pixels wide (see 01). They are not suitable for judging the face; shots 06–09 are relied on. I did not inspect 100% crops of each area; the inspection was on the full downscaled display from the tool.
- The manifest says the nine images were "Individually generated; not cropped from initial grid". I have no independent evidence of this; what I saw is that the sheet is a layout of the same images.

## 3. Reference source table (for comparison)

| Source | What actually appears | Note |
|---|---|---|
| 01 (full body) | Loose white thobe, standing collar, round black microphone (a chest piece, not a thobe button) on the upper placket, pocket on the wearer's left chest (image right), black thick-soled sandals with straps | The face is very small (about 60 pixels) and cannot be relied on |
| 02 | Front face, medium-density curved moustache, short-sided cut with density on top, round microphone on the placket | Good source for the collar and pocket |
| 03 | Open-mouthed expression, microphone visible, open palm | The right side of the hair and details are less clear |
| 04 | Closest face: thick eyebrows angled slightly upward, relatively broad nose, curved moustache, very light beard on the cheeks, thick wavy hair styled upward | Best reference for the face and hair |
| 05 | Smile, side sleeve, round microphone | Motion blur |
| 06 | Body angle, index-finger pointing, pocket visible | The pocket is on the same side (wearer's left) |
| JPG board | Compilation of the six sources | States "Missing views are not invented", i.e. there is no reference for the back, the sides or the footwear from behind |

**Front aspects of the sources:** The pocket is on the wearer's left chest (viewer's right), and the microphone is on the placket. The back, the two sides and the details below the knee are not confirmed in the sources (the sandals are visible only in 01).

## 4. Table of the nine images

Priorities: **CRITICAL** blocks lock/use, **MAJOR** noticeable continuity break, **MINOR** secondary.

| # | File | What was seen | Findings (precise area) | Priority |
|---|---|---|---|---|
| 01 | `views/CHAR-MO-v01-01-front.png` | Standing front, standing collar with tab, placket ending in a point, pocket on image right, round black piece (the microphone) drawn as a button, sleeves with cuffs, wide bottom hem, navy sandals with straps and buckle | (a) The round microphone appeared as a button with an engraved symbol/icon not clearly present in the source, upper chest area (about x=487, y=337 in the tool's display). (b) The sandals are navy with a buckle/velcro and straps over the foot, not black and thick-soled as in source 01, lower foot area. (c) The thobe cut is narrower and more elegant than the loose source. (d) The face is small (about 110 pixels) | (a) MAJOR (b) MAJOR (c) MINOR (d) MINOR |
| 02 | `views/CHAR-MO-v01-02-left.png` | Left side (facing image left), pocket visible on the chest, the microphone as a protruding black slice, sandals with crossed straps | (a) Left side with the pocket showing: **pocket side is correct**. (b) The sandals here have crossed straps without a buckle, a **different design** from 01/05 (buckle). (c) The hair has less volume on top of the head, and the sides are thinner than in 03. (d) A long vertical line/seam on the side not documented in the source | (b) MAJOR (c) MINOR (d) MINOR |
| 03 | `views/CHAR-MO-v01-03-right.png` | Right side (facing image right), no pocket (correct), the microphone at the edge of the chest | (a) A visible horizontal seam/patch on the side at the hip (about y=880–900, x=480–560) and a rectangular line on the upper arm (about x=410–480, y=410–440) that did not appear in 02 or in 01: invented details. (b) Crossed-strap sandals without a buckle, consistent with 02 and different from 01/05. (c) The hairstyle in 03 is higher at the front with a stronger fade than in 02. (d) The hem of the skirt is folded asymmetrically at the lower right | (a) MAJOR (b) MAJOR (c) MINOR (d) MINOR |
| 04 | `views/CHAR-MO-v01-04-back.png` | Back, collar, shoulder line, no button or pocket, sandals with heel strap | (a) The back is a **synthesized proposal**, not a documented reference (the source does not cover it). (b) The sandals here have a heel strap/front clasp, a third design that does not match 02/03. (c) The hands are in reasonable condition (fingers visible, no obvious deformity). (d) The back hair strands have no problems | (b) MAJOR (a) non-reference (proposal) |
| 05 | `views/CHAR-MO-v01-05-three-quarter.png` | Three-quarter, pocket on image right (wearer's left), moustache and eyebrows clear | (a) Pocket, placket and button consistent with 01. (b) Sandals with straps and buckle, consistent with 01 only. (c) The image-left hand (wearer's right) with a finger slightly raised: reasonable pose. (d) The face is relatively small | (b) MAJOR (compounded with 02/03) |
| 06 | `views/CHAR-MO-v01-06-face-neutral.png` | Neutral front face 1254×1254, thick angled eyebrows, thick-edged moustache, light beard on the chin and cheeks, shiny wavy hair, collar with tab and microphone drawn as a button with a symbol | (a) The moustache is thicker, with sharper and darker edges, than the lighter moustache in source 04. (b) The beard on the chin and cheeks is denser and more defined than in 04. (c) The hair is wavy and shiny with a wet look compared with the source. (d) The symbol on the microphone (about x=630, y=980) is an icon not clearly present in the source | (a)(b) MAJOR (c) MINOR (d) MAJOR |
| 07 | `views/CHAR-MO-v01-07-face-three-quarter.png` | Three-quarter face, collar with tab, microphone with a slightly different symbol, pocket | (a) The microphone symbol here (about x=548, y=972) differs in shape from 06: inconsistent microphone design. (b) The moustache is slightly thinner and shorter than in 06 (about x=510–700, y=545–590). (c) Ear and jaw consistent with 06 | (a) MAJOR (b) MINOR |
| 08 | `views/CHAR-MO-v01-08-face-smile.png` | Smile showing upper teeth | (a) The moustache curves and stretches with the smile, acceptable. (b) The symbol on the microphone (about x=630, y=980) is closer to 06, with a small dot at the upper left of the piece. (c) The density of the light beard is higher than in the source | (b) MINOR (c) MINOR |
| 09 | `views/CHAR-MO-v01-09-face-surprise.png` | Surprise, open mouth, wide eyes | (a) Eyebrows and eyes within natural expression. (b) The moustache narrows and changes shape with the open mouth: reasonable. (c) Microphone symbol as in 06/08 with the small dot | (c) MINOR |

## 5. Shared continuity anchors (expected to be constant)

| Anchor | Status across the nine images |
|---|---|
| Chest pocket on the wearer's left | Constant: visible in 01/02/05/06–09, absent in 03 and 04 (correct) |
| Standing collar with tab and pointed front placket | Constant |
| Thobe colour (white/off-white) | Constant |
| Moustache | Overall shape constant, but thickness and sharpness vary between 06 and 07 (MINOR) |
| Hairstyle (short sides, wavy top mass) | Generally constant, with a height difference between 02 and 03 (MINOR) |
| Microphone/button | **Not constant**: the microphone appeared as an integrated button with an engraved icon in varying shapes, instead of a simple black microphone disc with a constant design (MAJOR) |
| Sandals | **Not constant**: three designs (buckle in 01/05, crossed straps in 02/03, heel strap in 04) and navy colour instead of the black in the source (MAJOR) |
| Wide bottom hem | Present in all full-body images, and not established in the source (proposed) |

## 6. Comparison with the source (match notes)

- **Face:** The thick eyebrows, relatively broad nose and curved moustache appeared in images 06–09 as in source 04. Variance: the moustache is thicker and sharper, and the light beard is denser than in the source.
- **Hair:** Direction and overall volume are close to the source, but the texture is wavier and shinier.
- **Microphone:** In the sources it is a small round black disc on the upper placket. In the generated images the microphone was drawn as an integrated button with an engraved symbol, and without a clear microphone feature. I counted the symbol as an unintended mark (R10) until the CD/client approves it.
- **Sandals:** The source shows black thick-soled sandals in 01 only. The generated ones are navy and in multiple designs.
- **Thobe:** The generated cut is slimmer and neater than the loose source. Whether this is an acceptable deviation depends on the CD's decision; I make no taste judgement.
- **Right/left side:** The naming is correct (02 left side, 03 right side) and consistent with the pocket position.
- **Anatomy:** The hands in 01/02/03/04/05 are sound, with no visible extra fingers on the full display. I did not inspect 100% crops of the hands.

## 7. Corrections in priority order

1. **MAJOR — Sandals:** Unify a single design across the five full-body images (style, straps and colour), and match the black thick-soled sandals visible in `01-6UnyBbimn0I-t018.png`, or ask the CD to fix an alternative design. Any design outside the source counts as a proposal.
2. **MAJOR — Microphone:** Fix a single black microphone disc in a single position on the placket, without an engraved symbol (or with an approved symbol), in the same shape in images 01, 05 and 06–09 and at the side in 02/03.
3. **MAJOR — 03 right side:** Remove the horizontal seam on the side and the rectangle on the arm (areas noted in the table), or document them in the thobe design and add them in all angles.
4. **MAJOR — 06 neutral face:** Reduce the moustache's thickness and sharpness and the density of the cheek and chin beard to bring it closer to `04-6UnyBbimn0I-t026.png`, and fix the same moustache in 07–09.
5. **MINOR:** Unify the hair height between 02 and 03 and reduce the shine/waviness.
6. **MINOR:** Settle whether the wide skirt hem and the side seam are part of the approved design.
7. **MINOR:** The CD decides whether the narrower cut is acceptable; this is not counted as a judgement of mine.

## 8. Evidence, limitations and confidence

- **Actual evidence:** I opened with Read all the required images (6 sources + the board + the sheet + 9 views) and read manifest.json.
- **Limitations:**
  - I did not verify the dimensions of the nine images with an independent tool (see section 2).
  - I did not inspect 100% crops of the hands, feet or microphone, and the judgement on small symbols and sandal details is from relatively downscaled views.
  - The back, the two sides, the details below the knee and the sandals from behind are **synthesized proposals**, not a documented reference (the source does not cover them), so their match to the source cannot be judged.
  - The sources are low-resolution, compressed video frames carrying text, products and third-party commercial sites, so they are not suitable as a precise detailed reference.
  - I do not judge identity or ethnic origin, and this is not a numerical assessment of resemblance.
- **Assumptions [ASSUMPTION]:** That the colour of the sandals in the source is black (based on source 01 alone).
- **Confidence:** Medium-high for the sandal, microphone and visible-seam findings, medium for the hair, moustache and beard (visual judgement across differing lighting and angle), and low for what the source does not cover.
- **Not done:** No casting approval, no locked spec, no script, no R12 or V1–V6, no review of the pack as a whole.

## 9. Final verdicts

- **Draft verdict: REVISE** (at least 3 MAJOR continuity issues: the sandals, the microphone, invented details in 03, in addition to the moustache and beard differences in 06). No CRITICAL is visible on these images, but this is a draft verdict and does not count as a permission.
- **Production status: PENDING.**
- **QC of the pack as a whole: NOT LOCKED / PENDING.** No video or shot generation is permitted from these images.

## 10. Documentation addendum (2026-11-09): verification of the written evidence

Its scope is documentation only. The images were not re-reviewed and no visual verdict changed.

**A. What the round black piece is.** `library-kyu-visual-character-place-audio.md` (character section, outfit line) states "a round black microphone piece on the chest", and the description is repeated in the appearance summary. So it is a microphone, not a thobe button. The wording in the body was corrected (tables 3–4, the continuity item, correction item 2 and the limitations), and the [ASSUMPTION] about what it is was removed. The duplicate question about it was also removed from the HANDOFF.
- **The visual verdict has not changed:** The generated images draw the microphone as a button with an engraved symbol, in shapes that are not constant between 01 and 06–09. This is still MAJOR, and the symbol is still an unintended mark (R10) until the CD decides.
- I did not reopen the images in this round; the verdict rests on the earlier inspection.
- Note: The library describes the sandals only as "dark". The sandal note (navy versus black, and three designs) stands, and the question about it remains open.

**B. Permission for the work/review (established in writing).**
- `request.md` and the DL-011 line: an explicit question about generating new images of his character and uploading the references to Higgsfield; the user's answer «نعم، لهذا الشيت فقط» ("Yes, for this sheet only") (2026-11-09). The permission is reported by the user, not an independent consent document, and it excludes voice, video and publication.
- Permission for Claude to review these assets: stated explicitly in this round's assignment. I found no trace of it in the files I read, so it rests on the assignment alone.
- Notable discrepancy: The recorded permission mentions Higgsfield, while `request.md` records that the images were generated with the built-in image tool after Higgsfield refused. I do not judge here whether the permission covers this; I leave it to the coordinator/CD to document.
- This permission authorizes the work and the review only.

**C. Production approvals: not examined.** In this round I did not examine the casting/look files (`09-casting-approval.md`), the quality benchmark or the 2V visual approval (`visual-approval.md`). Permission to generate the sheet and send it to Claude does not count as any of them. I am not saying they do not exist; I am saying they were not examined and nothing in the sources read establishes them (`request.md` itself describes the output as a draft that does not replace the approval stages). **Production status remains PENDING**.

**D. Status after the addendum.**

| Item | Status |
|---|---|
| Visual verdict | **REVISE** (unchanged) |
| Production | **PENDING** |
| Full pack | **NOT LOCKED / PENDING** |
| Video and generation from these images | Not permitted |
| Wording of the body | Amended for the microphone naming only |

### HANDOFF
- Stage completed: Limited draft QC review of CHAR-MO-v01 (not a formal stage 8 and not a LOCK) + documentation addendum in section 10.
- Output file(s) written: `work/reviews/CHAR-MO-v01/qc-supervisor.md` (the only file modified; no images or shared logs were modified).
- Next agent and what they need from this output: DoP to fix items 1–4 in section 7 and regenerate under a new version name; then a new QC review. The CD decides on the narrower cut, the microphone design and its symbol, and the alternative sandals, and documents whether the recorded permission covers the built-in image tool.
- Open questions for the human (max 3, each with a recommended answer):
  1. Should the black thick-soled sandals from source 01 be adopted? Recommendation: yes, because it is the only visible reference.
  2. Should the slimmer thobe and the wide hem be adopted as the design? Recommendation: the CD's decision after a visual comparison, recorded as a proposed design.
  3. Does the DL-011 permission (which mentioned Higgsfield) cover generation with the built-in tool? Recommendation: the coordinator documents it in request.md or the decision log.
- Decision log lines added: none.
- Limitations: no visual re-review; casting/2V/benchmark approvals not examined; no LOCK and no video permission.
