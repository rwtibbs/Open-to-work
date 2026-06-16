# Cover-Letter Playbook (universal principles)

Load this in the writing pass, alongside the user's `voice.md` and `fact-pack.md`.
It governs *how* a strong cover letter is shaped; the user's files govern *what*
goes in it and *whose voice* it's in. None of this is person-specific — it applies
to anyone using the kit.

The goal every time: a specific, confident, human letter with zero generic filler,
in the applicant's real voice, that proves they read *this* posting.

---

## 1. Open with the strongest *authentic* entry point — strict hierarchy

Decide honestly which tier applies **before** writing. Scan the user's documented
personal hooks for a real connection to *this* company, product, or domain; if one
genuinely fits, lead with it; if not, use the elevator pitch. Don't force a
connection that isn't real.

- **PREFERRED — a genuine personal connection or passion**, drawn *only* from the
  user's documented hooks in `fact-pack.md` (or something they've said in the
  conversation). When real, this is the warmest, most memorable opener — a product
  they actually use every day, a cause they genuinely care about, the field they
  came from. The bar is **authenticity**: it must be traceable and must not be a
  stretch. **Never invent or inflate a connection.** A manufactured "I've always
  been passionate about [X]" is worse than having no connection at all — recruiters
  can smell it, and it's the opposite of a real voice.
- **FALLBACK — the elevator pitch**, lightly tailored (the user's canonical version
  is in `fact-pack.md`). Use when no genuine connection is strong enough to lead
  with. It's a clean, confident statement of who they are — the safe default, not a
  failure.
- **BANNED — the thesis cold open.** Never open with a pronouncement about the
  industry or what the role is "really" about. It reads as pretentious and
  overreaching — like explaining the company's own job back to them — and it
  recurs, so kill it on sight. Cautionary example of exactly what NOT to write:
  *"Most AI products look like a database that learned to talk — functional, and a
  little joyless. The interesting version of this role is refusing to let that
  happen…"* However clever it sounds, that pattern is banned.

"I am writing to apply for…" is also dead on arrival. After the opener, move
straight into evidence.

## 2. Prove it with real evidence

One or two paragraphs of concrete work, selected and framed for *this* role, drawn
from `fact-pack.md`. Use real numbers as payoff, not decoration. Tell the small,
specific story (the recovery flow, the research insight, the rescued deadline)
rather than listing responsibilities.

## 3. Be specific about *this* company

Name the actual product or problem and connect the applicant's experience to it.
This is the paragraph that proves they read the posting and aren't mass-blasting.
Generic praise ("I admire your innovative culture") is filler — cut it.

## 4. If there's an honest gap, name it plainly

When the role has a domain the applicant can't truthfully claim, the strongest play
is one plain sentence naming it, then a pivot to the transferable strength — e.g.
*"I don't have direct [domain] experience, and I'd rather say that plainly than let
you find it in the résumé."* Honesty reads as confidence. Never invent adjacent
experience to cover a gap.

## 5. Close short and confident

A line, not a paragraph — *"I'd love to talk."* / *"I'd love to work on this."*
Then the signature.

---

## Rhythm — write like a person, not like ad copy  *(the single most important craft rule)*

The most common way these letters go wrong is **artificially short, clipped
sentences and fragments deployed for effect**, which reads as machine-generated
rather than human. The tell is a sentence fragment standing in for a clause — e.g.
*"I started in advertising — a degree in it, then years at agencies."* ("a degree
in it" is a fragment-for-effect).

Favor fuller sentences whose clauses actually connect, joined with conjunctions, em
dashes, semicolons, or commas. Vary length, but a genuinely short sentence should
be **rare and earned** — used for real emphasis, never as the default cadence. Read
each paragraph back and ask whether a person would say it that way out loud; if it
feels staccato or punchy-for-the-sake-of-it, rewrite it to flow.

## Length & format

Keep it to one page, ~3–5 tight paragraphs. Render it with `build_cover_letter.py`
so the letterhead matches the resume — never hand-write the docx or re-style it.

Always produce the letter as a **standalone deliverable**, even when the application
form has no cover-letter upload slot (some ATS forms don't). A rendered letter the
user can email or hand to a recruiter is worth having regardless of whether a given
form will accept it.

---

## Coordinating the cover letter with application answers (distribute the evidence)

Cover letters and open-ended application answers should be planned **as one set**,
because the fastest way to look generic is to lead every piece with the same story.
Most applicants have a finite stock of proof points. Map each question (and the
letter) to a *distinct* primary example wherever the prompts allow: if the letter
leads on story A, let a "work you're proud of" answer lean on story B, a
"navigating ambiguity" answer pull from story C, and so on. Reuse a story across
two pieces only when it truly is the best fit for both — and even then, frame it
from a different angle. Someone reading the whole application should come away
seeing range, not the same anecdote on a loop.

For the answers specifically: match length to the ask (a "why this company" box
usually wants 80–120 words; "walk us through a project" might want 200–300), respect
any stated limits, answer the actual question with no throat-clearing preamble, and
hold to truth-only — every claim traces to `fact-pack.md` or something the user
said. Output answers inline in chat as copy-paste-ready text (they go into a web
form), never as a file: each as a markdown heading with the exact question text and
the answer beneath it.
