# Application Tracker — the standing ledger of where every role stands

The scanner remembers what it has *shown* you (`seen_postings.json`); the tracker
remembers what you've *done* — applied, reached out, interviewed, heard back — and what
you owe next. It's a single plain-JSON file the agent maintains:
**`user-library/applications.json`**. No script renders it; you read and update it
directly, the same way you maintain the rest of the library, and under the same
**`library_enrichment.mode`** (confirm vs. silent) and never-fabricate rules — only ever
record what actually happened.

This is what lets the user ask "what's still open?", "who do I owe a follow-up?", or
"what did I apply to last week?" and get a real answer instead of a shrug.

## When to touch it (across modes)

- **RUN (apply):** when an application is built — and especially after a browser
  fill/upload — append or update the role's record: `status: "applied"` (or
  `"prepared"` if the docs are made but not submitted), the deliverable paths, the JD
  link, the ATS, and the tier.
- **OUTREACH:** when a note is drafted/sent, set `outreach` (method, who, date,
  email-confidence) and, if outreach is the only action so far, `status: "outreach_sent"`.
- **PREP:** when the user says they have an interview, add an entry to `interviews`
  (round, date) and set `status: "interviewing"`.
- **Debrief:** mark that interview `debriefed: true` with a one-line outcome read.
- **Scan / discovery:** optional — a strong shortlisted role the user wants to pursue
  can be logged `status: "discovered"` so it doesn't get lost before they apply.
- **Status changes the user reports** ("got rejected", "they ghosted me", "got the
  offer"): update `status` and clear/keep `next_action` accordingly.

Always batch tracker writes into a mode's **close-out step**, never mid-task, and (in
`confirm` mode) show the user the record you're about to write.

## Record shape

`applications.json` is `{"applications": [ ... ]}`. Each record:

```json
{
  "company": "Acme",
  "role": "Senior Product Designer",
  "tier": 1,
  "source": "linkedin",
  "jd_url": "https://acme.com/jobs/123",
  "apply_url": "https://boards.greenhouse.io/acme/jobs/123",
  "ats": "greenhouse",
  "status": "interviewing",
  "applied_date": "2026-06-10",
  "deliverables": {
    "resume": "Resume_Jane_Acme.pdf",
    "cover_letter": "CoverLetter_Jane_Acme.pdf"
  },
  "outreach": {
    "sent": true, "method": "email", "to": "Dana Lee (Head of Design)",
    "email_confidence": "deduced", "date": "2026-06-10"
  },
  "interviews": [
    { "round": "recruiter screen", "date": "2026-06-14", "debriefed": true, "outcome": "advanced" },
    { "round": "hiring manager", "date": "2026-06-20", "debriefed": false, "outcome": null }
  ],
  "next_action": "Prep for the hiring-manager round",
  "next_action_date": "2026-06-19",
  "notes": "Real hook: long-time user of their product.",
  "updated_at": "2026-06-14"
}
```

Keep fields honest and omit what you don't know (don't invent a date or an outcome).
`status` is one of: `discovered` · `prepared` · `applied` · `outreach_sent` ·
`interviewing` · `offer` · `rejected` · `withdrawn` · `ghosted`.

## Answering "what's outstanding?"

When the user asks for their pipeline, read `applications.json` and report a tight,
grouped view — active roles first, then by `next_action_date`:

- **Needs action now** — anything whose `next_action_date` is past/today, or
  `status: applied` with no response in ~7–10 days (a polite status-check nudge is the
  natural follow-up — see `references/followup-and-negotiation.md`).
- **In flight** — `interviewing` / `offer`, with the next round or decision date.
- **Applied, waiting** — recent applications inside the normal response window.
- **Closed** — `rejected` / `withdrawn` / `ghosted`, collapsed to a count unless asked.

Offer to take the obvious next step (draft the follow-up, prep the next round, log a
new outcome). The tracker exists to drive action, not just to store rows.

## First-run

If `applications.json` doesn't exist when a mode first needs it, create it as
`{"applications": []}` (same as the empty `seen_postings.json` seed). Mention to the
user once that you're now keeping a pipeline ledger they can query anytime.
