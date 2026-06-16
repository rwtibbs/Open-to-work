# Onboarding Interview — Quick & Thorough question sets

This is the question bank the onboarding step (Step A in SKILL.md) draws on to
build the user's library. Two depths; the user picks at runtime. Whatever the
depth, **parse any uploaded resume / pasted LinkedIn or portfolio first** and only
ask for what's genuinely missing — don't re-ask for things you can already read.
Confirm everything back before writing the files.

The goal of every question is to fill a specific library file:
`profile.json`, `base_resume.md`, `fact-pack.md`, `voice.md`, `format.json`, and
(optionally) `scanner_config.json`.

---

## QUICK path (~5 minutes)

Best when the user uploads a resume. Parse it, then ask only the gaps.

**Identity & profile (profile.json)**
1. Confirm name, email, phone, location, and the personal website/portfolio URL
   I parsed — fix anything wrong, add what's missing.
2. LinkedIn URL? Any other links (GitHub, portfolio) to keep on file?
3. Are you authorized to work in [country], and do you now or will you in future
   need visa sponsorship?
4. Comp target and floor (a number or a range — used only when a form demands one;
   "open" is fine).
5. Anything you want pre-filled for the standard form questions (how you heard
   about roles, earliest start date, relocation/remote preference)? The EEO
   demographic questions are always optional — skip any you'd rather leave blank.

**Resume content (base_resume.md)**
6. I've drafted your master resume from what you uploaded — does the summary,
   the role list, and the skills look right? Anything understated or missing?

**Stories & differentiators (fact-pack.md)**
7. One real story where you **deviated from the standard process** — compressed
   deadline, mid-flight scope change, a constraint that broke the normal playbook.
   What was standard, what you did instead, the outcome. (Almost every application
   asks a version of this.)
8. Any **genuine personal connections** to companies/products/domains you're
   targeting — something you actually use, a cause you actually care about, a field
   you came from? Only real ones.
9. The 2–3 metrics or wins you're proudest of (real numbers).
10. An honest list of gaps — domains/tools/scales you genuinely can't claim. (This
    keeps the rest of your application confident and truthful.)

**Voice (voice.md)**
11. Can you paste something you've written that sounds like you (an old cover
    letter you liked, a post, a detailed email)? If not, I'll capture your voice
    from how you write to me.

**Format (format.json)**
12. Any preference on the resume's look — a display font for your name, an accent
    color for links? Otherwise I'll use a clean default.

---

## THOROUGH path (~20 minutes)

Best when there's no resume, or the user wants a richer fact pack and voice. Covers
everything in QUICK, plus the following — ask conversationally, in batches, not as
a rigid quiz.

**Career history (base_resume.md + fact-pack.md)** — for each role, most recent
first:
- Company, what it does, your title, dates, team size, who you reported to.
- What you actually owned and how you operated (the hats you wore).
- The 3–6 concrete things you did, each with a real outcome or number.
- The recurring hard problems you were solving (fuel for "tell me about a time…").

**Strength areas (fact-pack.md)**
- What are the 3–4 things you're genuinely best at? Two pieces of real evidence
  each.

**Signature stories (fact-pack.md)** — get real, specific versions of:
- The 0→1 / built-from-nothing story.
- The deviated-from-process story (deadline / scope change / ambiguity).
- The practitioner / "I use what I build" story, if you have one.
- Any other story you find yourself telling.

**Personal hooks & motivation (fact-pack.md)**
- Products/categories you genuinely use and love; causes you actually care about;
  the field you came from. What kind of company would each be a real connection to?
- Your reusable elevator pitch — 1–2 sentences about you, the same person every
  time, for when there's no specific hook to open with.

**Voice (voice.md)** — capture from a sample if possible; otherwise dig in:
- How would you describe the way you write? Show me a sentence you're proud of.
- What kind of writing makes you cringe? (Their "never" list.)
- Formal or casual? Humor or straight? Do you use dashes, short punchy lines, long
  flowing ones?

**Format (format.json)**
- Display font for your name, body font, accent color, or a vibe ("understated and
  serif" / "modern and clean"). I'll translate it into tokens.

**Automation & browser apply (Step A3 — prompt for these, don't just mention them)**

These are the high-leverage features; walk the user into setting them up.

- *Scanner config (`scanner_config.json`).* Set up automated scanning?
  - Target roles and seniority levels (e.g. "Senior/Staff Product Designer").
  - Locations — remote, specific cities/states, US-only?
  - Comp floor (the number below which it's not worth surfacing).
  - The role *shape* you most want (founding / first-hire / 0→1 / generalist) and
    your priority vs. hard-no domains.
  - **Translate the config examples to THEIR field.** The `scanner_config.template.json`
    ships with role-neutral defaults plus example values phrased for one role (e.g.
    design: "first design hire", "founding designer", role-title regex around "product
    design"). Do NOT leave the design examples as-is for a non-design user. Rewrite every
    example slot to the user's actual profession before saving their `scanner_config.json`:
    - `role_keywords` / `role_title_regex` → their job titles (e.g. "growth marketing
      manager", "backend engineer", "staff nurse").
    - `shape_signals` → the equivalent shape language for THEIR role: add "founding
      engineer / first backend hire", "first PM / founding product manager", "first sales
      hire", "charge nurse / unit lead", etc., while keeping the role-neutral ones that
      already generalize ("founding", "first hire", "0 to 1", "generalist", "broad scope",
      "end-to-end ownership", "wear many hats", "build the X function").
    - `tier1/tier2/exclude` keywords → their domains and hard-nos.
    - For a non-US / non-USD search, set `accept_currencies` and `comp_band` to their
      currency (see the template's `_currency_note`).
    Confirm the rewritten lists back to the user before writing the file.
  - Any companies for the watchlist? (I'll find + verify their Greenhouse/Lever/Ashby
    slugs.)
  - Recency window and how many results per digest.
- *Schedule.* I'll run it twice a day (~8am/4pm your time) and send a ranked
  shortlist — or pick your own cadence. (Confirm timezone.)
- *Claude for Chrome extension.* This unlocks two things, so let's get it installed:
  (1) the logged-in **LinkedIn + Wellfound** browser pass in your scans — the only
  way to include those two — and (2) **browser fill & upload** of applications at the
  end of a run. Are you able to install it and stay signed in to those sites? If you
  skip it, scanning runs on the API sources only and applications hand back to you to
  submit.

---

## After either path

1. Write the filled files into `user-library/` and **delete `NOT_ONBOARDED.md`**.
2. Read back a concise confirmation: identity, the roles captured, the hooks and
   the deviated-from-process story, the gap list, and a 2–3 sentence pastiche in
   the captured voice ("does this sound like you?").
3. Tell them they're set up and can now say e.g. "tailor my resume for this job"
   (paste a JD) or, if scanning was configured, "scan for jobs."
