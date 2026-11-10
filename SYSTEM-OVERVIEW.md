# Kyu Creative Studio — System Map

Status below reflects the current local project-file inventory.

A reference that explains the team, the libraries and each project's inputs. The roles below describe the agents' responsibilities and their required outputs; they do not mean these outputs have actually been produced. The status is updated when data is added or new stages are tested.

## 1. Agents table

The current team has **9 agents, spread across 8 roles**; idea generation has two agents working independently.

| Agent | Runs via | Responsibility | What does it deliver? |
|---|---|---|---|
| **Creative Director** | Claude Code | Understands the request, chooses the idea and the characters, approves the style and the quality sample | The brief, and the idea, casting and visual-approval decisions |
| **Researcher & Strategist** | Claude Code | Studies the brand, the market, the audience, the competitors and the trends | Documented research and a clear marketing message |
| **Idea Generator A** | Codex CLI | Generates ideas from specific creative angles | A varied set of ideas |
| **Idea Generator B** | Claude Code | Generates independent ideas from other angles | A second set to widen the options |
| **Critic** | Claude Code | Compares the ideas and reviews the script and the cut | Evaluation, notes, and acceptance or a request for changes |
| **Producer** | Claude Code | Checks feasibility, time, cost and constraints | An execution plan, risks and alternatives |
| **Writer** | Codex CLI | Develops the characters, the hook, the dialogue and the sequence of events | The script and the ad copy |
| **Director of Photography & Visual Planning** | Codex CLI | Defines the visual look and the specifications of the sheets and shots | A visual guide, sheet specifications, a shot list and prompts |
| **Quality & Continuity Reviewer** | Claude Code | Checks the sheets and the consistency of faces and wardrobe before video, then the shot frame and the motion | A video-readiness report and decisions to approve or re-correct |

The assignment of roles and providers is set in the [team settings](config/agents.yaml), and the sequence is explained in the [pipeline guide](PIPELINE.md).

## 2. Libraries table

The libraries are the knowledge the team refers to before making its decisions. The status recorded below is the actual status at the time of the last review.

| Library | What does it contain when complete? | Why does the team need it? | What exists now |
|---|---|---|---|
| **Hooks** | Hooks, classifications, reasons for success and documented numbers | Choosing a suitable opening | A taxonomy of 15 types, illustrative examples and measurement criteria; hook observations in the six video deconstructions, but no measured performance bank |
| **Trends** | Sounds, formats, hashtags and challenges, with the observation date and sources | Knowing what fits right now | An empty template; no automatic updates |
| **Idea DNA** | Breakdown of the premise, characters, escalation, joke, shareable shot and ending | Understanding the reusable creative structure | Six video deconstructions (five Kyu Shorts and the Ballon d'Or reference), plus a deeper character/comedy craft study; two additional Kyu 11/11 teasers analysed in the local research folder |
| **Audience Insights** | Needs, objections and phrases from comments and reviews | Building an idea that connects with the audience's life | Research instructions; no accumulated data bank |
| **Cultural Calendar** | Occasions, seasons, paydays and upcoming events, with documented dates and sources | Choosing the timing and context | The general 90-day calendar is empty; Kyu's 11/11 campaign context is documented in the brand file and teaser analysis |
| **Own Performance** | Results of our work linked to the idea, the hook and the execution | Improving decisions based on our experience | Not built yet |

Current references: [hook taxonomy](knowledge/hook-taxonomy.md), [trends template](knowledge/trends-snapshot.md), [work breakdown template](knowledge/deconstruction-template.md), [library folder](knowledge/library/README.md), [brand file](knowledge/kyu-brand.md), and [researcher instructions](agents/researcher-strategist.md).

Having a template does not mean having data. Every number, quote or trend needs a source and a date, and unconfirmed information is stated as an assumption or a gap.

### Supporting knowledge and project records

The six categories above are a planned knowledge taxonomy, not six independent databases. The project also has:

- **Brand knowledge:** `knowledge/kyu-brand.md` records confirmed/scoped information and open fields. It includes project consent and Kyu's teaser claims; the exact iPhone price, gift details, offer terms and many core brand fields remain unconfirmed.
- **Visual and character research:** `knowledge/library/library-kyu-visual-character-place-audio.md` and the asset manifest organise six original character frames, location/product boards and source provenance. Generated character-sheet candidates v01/v02 are in `work/production/casting/`; independent Claude reviews are in `work/reviews/`. These are separate from production approval.
- **Audio research:** `knowledge/library/library-mohammed-omar-voice-analysis.md` contains signal measurements and four excerpts, with no completed listening/tone review. The later client-request clip has a local automatic transcript and frame-based request analysis; it is not a voice-performance test.
- **Technical tests:** `knowledge/tech-test.md` still contains unfilled test tables. Creating stills and reviewing them does not establish Saudi lip-sync or motion quality.
- **Client request and working brief:** `work/00-client-notes.md`, `work/client-request-analysis.md` and draft `work/01-brief.md`. These are project inputs and proposals rather than general creative-library examples.
- **Detailed local evidence:** `work/research/` holds downloaded sources, extracted frames, transcripts and the two iPhone teaser analyses. Most media and this research folder are excluded from Git; not everything local is available in a GitHub clone.

## 3. Project inputs table

Inputs come from the client, then the team fills in what it needs through research. Work can start with the available information while recording the gaps; offers, prices and claims need confirmation before they are used.

| Input | What do we need in it? | What does it affect? |
|---|---|---|
| **Brand** | Its business, personality, values and visual identity | The ad's tone and look |
| **Product or service** | What we're advertising, its images and confirmed features | The story's focus and how the product is shown |
| **Objective** | Purchase, visit, download, awareness or recall | The message and the call to action |
| **Audience** | Who we're addressing, where they live, and what they need | The idea, the language and the hook |
| **Offer and message** | The price and terms if any, and the most important thing we want to get across | The advertising promise |
| **Taste and boundaries** | References the client likes, and what they want to avoid | The creative direction |
| **Execution conditions** | Platform, duration, deadline and budget | The size of the idea and the production plan |
| **Success criterion** | How will we judge the test? And what results will be available later? | The evaluation and feeding the performance log |

The client's words are recorded in [client notes](work/00-client-notes.md), and confirmed brand information is pinned in the [brand file](knowledge/kyu-brand.md).

## 4. How do the parts connect?

**Client request ← research ← ideas and review ← idea selection ← script ← choosing characters and the visual look ← sheets and their approval ← quality sample, client approval and consistency check ← storyboard and approved frame ← motion test ← production and review.**

- The client approves the brief and the idea, then the characters, the style and the quality sample at a 2V visual-approval point before video, then the cut that is shown.
- The director of photography plans the sheets for the characters, the product, the props, the location and the visual style. The images are produced with the tools and reviewed by an independent agent; writing the prompt alone does not mean the sheet is complete.
- The illustrated storyboard needs the full reference package to be approved. Before any video, the faces, hair, the cut, colors and fabrics of the clothes, and the accessories are checked across different angles and expressions, and an actual quality sample is approved. Then each shot's frame is checked before it is animated, and a motion test is reviewed before the rest of the videos.
- The review measures conformity to the approved references and the required contemporary look; it does not infer nationality or ethnicity from the face. The gates are operating instructions for the runner and the agents, not an automatic block inside the generation tools.
- When the performance log is built, publishing results are fed back into research and idea development; this loop is not currently implemented.

## 5. Current status and operating limits

The team's instructions and the runner exist, and the agents' isolated response tests passed. A full ad production cycle has not been tested yet. The libraries need filling, and running the image and video tools and reviewing the results are done as separate steps; full automatic linking between the production stages is not currently implemented.
