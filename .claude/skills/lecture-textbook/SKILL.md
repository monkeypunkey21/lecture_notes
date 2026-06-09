---
name: lecture-textbook
description: Turn lecture materials (transcript, board screenshots, related textbook chapter) into a single self-contained interactive HTML study page rendered in a fixed light-mode design system. Trigger this skill whenever the user attaches or pastes a lecture transcript with intent to learn the content (especially for an exam), when they ask to "turn this lecture into an interactive page," "make me a study guide," "help me learn this lecture," or similar — even if they don't explicitly say "skill" or "interactive textbook." Trigger even when only a transcript or only board screenshots are provided. Primary use case is computer science (CS) coursework, but the same approach works for any discipline. Use this skill instead of frontend-design whenever the goal is learning lecture material — frontend-design is for novel, varied visual work; this skill produces consistent study pages with a fixed component vocabulary.
---

# Lecture Textbook

A skill for converting raw lecture materials into a single interactive HTML
study page styled with a fixed design system. The student wants to *learn the
content* — not skim a summary. Every page should teach from scratch, build up
gradually, and answer "why am I learning this?" at every turn.

## Inputs to expect

The user will provide some combination of:

- **Lecture transcript** — primary spine. The exam will test what the
  professor actually said, so this is the source of truth for what gets
  covered. May be raw (timestamps, filler words, false starts) — clean as
  you read.
- **Board screenshots** — what the professor wrote on the board, slide
  contents, or projected code. Use these as anchors: anything written on the
  board is something the professor flagged as worth writing down, so it
  should usually appear in the page (often as a code block, diagram, or
  flow-step trace).
- **Textbook chapter** — the related chapter from the course textbook. Treat
  this as a *secondary explainer*. The lecture is canonical; reach for the
  textbook when a concept needs more careful unpacking than the lecture
  gave, when an analogy or alternative framing would help, or when the
  textbook covers something the lecture only gestured at.

If the user provides only a transcript, that's fine — produce the page from
what's there. Don't refuse or stall on missing materials.

## Pedagogical principles (non-negotiable)

These are the rules the student explicitly asked for. Honour them literally.

1. **Teach from scratch.** Assume zero prior knowledge. If the lecture uses a
   term, define the term, even if it feels obvious. No "as you know" or "you
   should already be familiar with" — instead, briefly catch the reader up.
2. **Build up before applying.** For any topic that requires layered
   understanding (especially CS topics like coding syntax, recursion, data
   structures, algorithms, type systems): introduce the foundational idea
   first, then a worked example, then add complexity, then another example.
   Never drop the advanced version on the reader before the simple version.
3. **Always answer "why are we learning this?"** Every major section should
   open with motivation. What problem does this solve? What goes wrong
   without it? Where does it lead?
4. **Connect to the bigger picture.** Use *connection callouts* (tip class)
   to flag "this builds on X from earlier" and "this sets up Y coming
   later." The student wants to see the course as a graph, not a list.
5. **Examples are not optional.** Every concept gets at least one concrete
   example. For procedural concepts (algorithms, code execution), use a
   `flow-step` trace that walks through it. For structural concepts (parse
   trees, list cons, recursion call trees), use an inline SVG figure.
6. **Synthesise, don't transcribe.** The transcript is raw material. Rewrite
   it as clear prose. Reorder for pedagogical flow. Cut filler. Add the
   connective tissue the professor skipped because they were speaking out
   loud.

## Output

Produce **one self-contained `.html` file** that opens directly in a browser
(no build step, no external assets beyond the Google Fonts CDN). The file
must include the full `<style>` block from `assets/styles.css` and the full
`<script>` block shown in `references/component-library.html`.

Save it to a sensible filename like `lecture-{N}-{slug}.html`
(e.g. `lecture-3-patterns-recursion-syntax.html`). On claude.ai with code
execution enabled, write to `/mnt/user-data/outputs/` and present it. In
Claude Code, write to the current working directory unless the user said
otherwise.

### Required head

```html
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=JetBrains+Mono:wght@400;500;600&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
  /* paste the entire contents of assets/styles.css here */
</style>
```

### Page structure (in order)

1. **Progress bar** (`<div class="progress-bar">`) — top of body
2. **Nav toggle button** + **sidebar nav** with TOC (every part, every
   sub-section, every quiz)
3. **Hero** — eyebrow (`Course Code · Course Name`), `<h1>` lecture title,
   `hero-sub` one-line description
4. **Parts** — one `<section>` per major topic. Each part has a
   `part-header` with `part-number` ("Part I", "Part II", ...) and an `<h2>`
   title. Within a part, use `<h3>` for sub-topics and `<h4>` for finer
   subdivisions.
5. **Putting It All Together** — final synthesis section. Connect the parts
   to each other and to the bigger picture of the course. End with a `tip`
   callout titled "What's Next" previewing the next lecture or where these
   ideas reappear.
6. **Scripts** — the full `<script>` block at the bottom of `<body>` (nav
   toggle, progress bar, scroll reveal, quiz logic).

Aim for **3–7 parts** for a typical lecture. Fewer feels thin; more
fragments the material.

## Component vocabulary

`references/component-library.html` is the canonical reference — read it
before writing the page. Every component used in a generated page must come
from this vocabulary. Do not invent new component classes or restyle
existing ones.

### Callouts (`<div class="callout {variant}">`)

Use them deliberately, not decoratively. A page with a callout every
paragraph dilutes their signal value.

- **concept** (blue) — formal definitions of key terms. The thing you'd
  want flagged on a flashcard.
- **warning** (red) — common mistakes, compiler errors, footguns, "don't
  do this and here's why."
- **tip** (green) — practical advice, study strategy, *connection callouts*
  ("this builds on X" / "this sets up Y"). Also used for the "What's
  Next" closer.
- **insight** (purple) — deeper realizations, "aha" moments, surprising
  consequences. Less formal than `concept`, more substantive than `tip`.
- **big-idea** (orange/accent) — reserve for the 3–5 most important
  takeaways of the entire lecture. If you're using more than five per
  page, you're diluting them.

### Quizzes (`<div class="quiz">`)

End every part with one check-yourself quiz. 3–4 options, exactly one
correct. The explanation block should be substantive — at minimum 2
sentences explaining *why* the right answer is right, ideally also noting
why a plausible wrong answer is wrong. Quiz IDs must be unique (`q1`, `q2`,
...). The onclick must encode the correct letter: `checkQuiz('q2','b')`.

### Flow-steps (`<div class="flow-step">`)

Use for any numbered walkthrough: code execution traces, algorithm steps,
derivation chains, multi-step proofs. The vertical connector line between
steps is automatic — don't add your own.

### Figures (`<div class="figure">` + `<div class="figure-box">`)

The figure-box contains inline SVG. Use figures for spatial / structural
concepts where prose alone is insufficient: parse trees, list cons
diagrams, recursion call trees, memory layouts, finite-state machines,
type derivation trees, control-flow graphs. Always add a `figure-caption`
underneath.

For SVG colors, use the design system: `#c0510a` (accent), `#2a2520`
(text), `#d9d0c4` (border / connector lines). For monospace text in
figures, use `font-family="JetBrains Mono, monospace"`.

### Collapsible details (`<details>` / `<summary>`)

Use for genuinely optional deep-dives: desugared / expanded forms of
syntax, formal proofs, edge cases, "here's the long version." Don't bury
core content inside `<details>` — if the student needs to read it, it
should be in the main flow.

### Code blocks (`<pre><code>`)

Manually colorize with span classes from the CSS: `kw` (keywords), `str`
(strings), `cm` (comments), `tp` (types), `fn` (function names), `op`
(operators), `nb` (numbers/special). Add a `<span class="label">` in the
top-right for language tag when the language isn't obvious from context
(e.g. `<span class="label">C</span>` in an otherwise-OCaml page).

Inline code (`<code>` inside `<p>`) is auto-styled with accent color on a
warm background — no manual colorizing.

### Comparison tables (`<table class="compare-table">`)

For genuinely comparative content (this vs that, before vs after, syntax
vs semantics, naive vs optimized). Use sparingly.

## Process

1. **Read all inputs in full.** Don't skim. The transcript especially —
   the professor's emphases, asides, and worked examples are signal.
2. **Identify the parts.** What are the 3–7 major topics? They usually
   correspond to topic transitions in the lecture or board.
3. **For each part, plan the flow:** motivation → foundational concept →
   worked example → complexity / variant → another example → quiz.
4. **Decide the connections.** Which parts depend on earlier parts? Which
   set up later parts? These become tip callouts at transitions.
5. **Identify big-ideas.** What are the 3–5 things the student absolutely
   must take away? These become big-idea callouts, scattered through the
   page (not all at the end).
6. **Identify figures.** Where is the concept spatial or structural? Plan
   inline SVG diagrams for those spots.
7. **Write the page.** Mirror `references/component-library.html`
   exactly for structure and class names. Paste `assets/styles.css`
   verbatim into the `<style>` block.
8. **Write the closing synthesis.** "Putting It All Together" should
   actively connect the parts, not just summarise them.

## Quality bar / what NOT to do

- **No prior knowledge assumed.** If you find yourself writing "recall
  from last lecture..." or "you'll remember that...", stop and define
  the term in-place.
- **No telegraphic explanations.** "X is when Y" is not enough. Spell out
  the motivation, the mechanism, and the consequence.
- **No deviation from the design system.** Don't restyle components,
  don't add new colors, don't change fonts, don't introduce dark mode.
  Every page must look like a sibling of every other page.
- **No glossary tooltips, no runnable code playgrounds.** The student
  opted out of these explicitly.
- **No fake interactivity.** If a button or control exists in the HTML,
  it must work. Don't add decorative `<input>` or `<select>` elements
  with no script behind them.
- **No filler.** "This is an important topic that we'll explore in
  depth" is filler. Just start exploring it.
- **No surface-level transcribing.** If the lecture said "and then we
  call cons on it," that's transcription. The page should explain *what
  cons is*, *why we're calling it*, and *what happens as a result*.

## CS-specific guidance

CS is the primary use case. A few extra patterns to reach for:

- **Code execution traces** — use flow-steps to walk through what a
  program does line by line, showing variable state at each step.
- **Big-O / complexity analysis** — show the cost per call and the
  number of calls explicitly. Use a flow-step or callout to derive the
  total. Don't just assert "this is O(n²)."
- **Data structure diagrams** — linked lists, trees, hash tables, stack
  frames, heap layouts — all candidates for inline SVG figures.
- **Type derivations** — for typed languages, show the inferred type and
  reason about *why* OCaml/Haskell/Rust inferred it that way.
- **Naive vs optimized comparisons** — `compare-table` is great for this.
  Show both versions, then explain the gap.
- **Compiler / language theory** — parse trees, ASTs, token streams,
  grammar rules. Use figures and code blocks generously.

## Non-CS subjects

The same skill works for any subject. Adjust the patterns:

- For math: code blocks become equation blocks (use `<pre>` with KaTeX-free
  ASCII math, or `<code>` for inline). Figures show diagrams, graphs.
- For history / theory: flow-steps walk through causal chains or
  arguments. Comparison tables compare theories, periods, schools.
- For science: figures show experimental setups, molecular structures,
  process diagrams.

The pedagogical principles are universal — only the figure content changes.
