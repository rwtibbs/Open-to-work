# Browser Auto-Fill & Upload (Claude-in-Chrome)

How to fill an application form and attach the tailored PDFs in a browser, using
the Claude-in-Chrome tools. This is the apply step at the end of the RUN pipeline.
The method below is the *only* one that reliably works for file uploads — the
obvious alternatives don't, for the reasons noted. None of this is person-specific.

**Prerequisite: the Claude for Chrome extension.** This whole step depends on it,
plus the browser being open and the user logged in to the ATS / job site. If the
extension isn't connected, you can't fill or upload — say so and point the user to
Step A3c (extension setup) rather than failing silently. (The same extension powers
the scheduled LinkedIn/Wellfound browser pass, so a user who set up scanning likely
already has it.)

## The one irreversible rule

**Always STOP at the final Submit.** Fill everything, attach the files, verify, and
then hand control back so the user reviews and submits themselves. Submitting is
the one step you never take for them — unless the user has explicitly authorized you
to submit.

## Apply on the canonical ATS, not a profile-only aggregator

Before filling anything, check **where** you're applying. Some sources — notably
**Wellfound and LinkedIn Easy Apply** — only transmit the user's *profile* and offer
**no file upload at all**, so the tailored résumé and cover letter can never be
attached. When the role was found on one of those, first search for the same posting
on the company's **real ATS** (Greenhouse / Ashby / Lever) or careers page and apply
**there**, where the documents can actually be uploaded. Profile-only is the fallback
only when no canonical posting exists. (At the shortlist stage, that canonical "Apply
at" link should already be surfaced — see `scheduling.md`.)

## Stage the PDFs to the OUTPUTS folder first

The Chrome `file_upload` tool can only attach a file that lives in a **writable
outputs/working folder** (it's writable and the tool drops the file straight into the
form's own file input) — **not** a read-only skill/bundle dir, and **not** a
Drive/Dropbox location. So before applying, copy the final PDFs into the outputs
folder with their exact deliverable names:

```bash
cp "Resume_<Name>_<Company>.pdf" "CoverLetter_<Name>_<Company>.pdf" "<outputs folder>/"
```

Keep the filenames exactly as the deliverables — they're what the recruiter sees,
and you'll verify them by name after upload.

## Upload procedure

1. **One tab per application.** Open EACH application in its OWN browser tab and
   never reuse a tab — navigating away wipes a filled form. Applying to several
   roles in a batch means several parallel tabs.
2. **Fill standard fields from `profile.json`** — name, email, phone, location,
   links, work authorization / sponsorship answer, and the `standard_form_answers`
   (how-you-heard, start date, EEO fields the user chose to pre-fill). Leave blank
   anything the user left blank.
3. **Upload the résumé.** `find` the specific résumé file input (type=file), then
   `file_upload` with the outputs path. **Re-find the input ref immediately before
   the upload** — refs shift, and a mid-task extension reconnect can land a file in
   the wrong slot.
4. **Upload the cover letter** the same way — re-find its input first, then upload.
5. **Verify the filenames landed in the right slots.** Read back the attached
   filenames and confirm the résumé is in the Résumé/CV field and the cover letter
   is in the Cover Letter field. If they're mis-slotted (the reconnect slot-shuffle
   bug), remove and redo. This check is not optional — a swapped pair looks fine to
   the upload tool but wrong to the recruiter.
6. **Fill remaining fields and STOP at Submit** for the user to review.

## Some forms have no cover-letter slot and/or no essay questions

Not every ATS form accepts a cover letter, and some have no open-ended essay
questions at all (certain Ashby forms, for instance, offer neither). That's fine and
expected — it doesn't mean skip the cover letter. The cover letter is **always a
standalone deliverable**: produce and render it regardless, so the user can email it
or hand it to a recruiter even when the form won't take an upload. If there's no
essay box, there's simply nothing to paste — note it and move on.

## Leave genuine user-judgment fields for the human

Fill only what you can verify from `profile.json`. **Never auto-answer or auto-agree**
to fields that are the user's call to make:

- **Relocation-willingness** questions ("are you willing to relocate to X?").
- **"Have you used <product> before?"** / familiarity questions.
- **Terms / consent / acknowledgment checkboxes.**
- The final **Submit**.

Leave these for the user. Surface them clearly when you hand control back, fill
everything you legitimately can, and stop — unless the user has explicitly told you
to answer or submit on their behalf.

## What NOT to do (these genuinely don't work)

- **Don't use the board's Google Drive / Dropbox "import" buttons.** They open a
  third-party, cross-origin file chooser the agent cannot operate — clicks and
  keystrokes don't reach inside it.
- **Don't rely on the native OS file dialog.** It's invisible to the agent.
- The outputs-folder → `file_upload` path is the only working upload method.

## Open-ended questions live behind the Apply button

Most application forms hide their essay-style questions ("Why this company?",
"Walk us through a project") behind the Apply button, so they often don't appear in
the JD text at all. When you have the application page open, **pull those questions
straight from the form** and answer them (in the user's voice, per the
cover-letter playbook's coordinated-set rule) before stopping at Submit. If you
only ever had the JD and never opened the form, tell the user plainly that
form-gated questions may exist that you couldn't see, and offer to answer any they
paste back.
