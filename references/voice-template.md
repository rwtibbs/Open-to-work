# Writing Voice — [Your Name]

This file teaches the assistant to write cover letters and application answers
that sound like **you**, not like generic "AI cover-letter voice." Onboarding
writes a filled copy to `user-library/voice.md` and the writing pass loads it
before drafting a single sentence. A letter in your real voice helps you; a
templated one actively hurts you.

---

## How this file gets built (for the assistant, during onboarding)

Capture the user's voice from the strongest evidence available, in this order:

1. **A real writing sample** — the best source by far. Ask for 1–3 things they've
   written that sound like them: a past cover letter they liked, a blog post, a
   detailed email, a LinkedIn "about," anything in their natural register. Read it
   and extract the *patterns* below — sentence length and rhythm, how they open,
   whether they use humor, dry understatement, em dashes, how formal they are,
   words they reach for and words they'd never use.
2. **Targeted Q&A** — if there's no sample, ask a few questions and listen to *how*
   they answer, not just what: "How would you describe the way you write?" "Show me
   a sentence you're proud of." "What kind of writing makes you cringe?" Their
   phrasing in chat is itself a sample.
3. **Fill the template below** with what you found, quoting real fragments where you
   can. Concrete captured patterns beat adjectives — "opens with a short personal
   anecdote, then the work" is more useful than "engaging."

Then confirm it back: read a 2–3 sentence pastiche in the captured voice and ask
"does this sound like you?" Adjust from their reaction.

---

## Captured voice profile

### Core character
[How they come across on the page. e.g. "Writes like someone who did the thing and
is telling you about it directly — confident, personal, grounded; professional but
never stiff. No performing expertise, no hedging."]

### Structure
[How they organize a piece. e.g. "Narrative when the format allows — what was
broken, what changed, what resulted; lets numbers land as payoff rather than
headlines. But not a rule — some pieces are short and direct."]

### Voice & person
- [First person, active? Passive avoided? e.g. "First person, active — 'I led,'
  'I built,' never passive constructions."]
- [How much emotion/personal stakes show, and whether it's understated or open]
- [Humor? Dry? Warm? e.g. "Dry understatement used sparingly for memorable
  moments; warm but never gushing."]

### Rhythm
[Sentence-length pattern. e.g. "Varies length naturally — short sentences land key
moments, longer ones carry context. Clean, often time-based transitions. Avoids
stacking three clauses back to back." Capture whether genuinely short sentences are
rare-and-earned or a frequent device for them.]

### Word choice
- [Concrete vs. abstract tendencies]
- [Real numbers over vague quantifiers — "70% faster" not "significant"]
- [Em dashes, semicolons, other punctuation they actually use]
- [Words/phrases they reach for]

### Things to avoid (their personal "never" list)
[Words, phrases, and tics that don't sound like them. e.g. corporate jargon
("leverage," "synergy," "cross-functional alignment"), passive voice, padding
before the point, adjective stacking, and AI tells ("not only… but also," "it's
worth noting," "in today's world," "seamlessly," "delve").]

### Sample fragments (in their real words)
[2–4 short quotes from their writing sample that capture the voice, so the
assistant can pattern-match against the genuine article rather than a description
of it.]

---

## Universal guard rails (apply on top of the captured voice for every user)

These hold regardless of whose voice it is — they're what keeps the writing
human:

- **Write like a person, not like ad copy.** The most common failure is
  artificially short, clipped sentences and fragments-for-effect, which reads as
  machine-generated. Favor fuller sentences whose clauses connect — joined with
  conjunctions, em dashes, semicolons, commas. A genuinely short sentence should be
  rare and earned, used for real emphasis, never as the default cadence. Read each
  paragraph back and ask whether a person would say it that way out loud.
- **No AI tells.** "Not only… but also," "it's worth noting," "in today's world,"
  "seamlessly," "delve," "tapestry," "testament to" — cut on sight.
- **Concrete over professional-vague.** Real specifics and real numbers, never
  filler abstractions.
- **Truth only.** Voice never licenses fabrication — see the never-fabricate rule
  in SKILL.md.
