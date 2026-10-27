# Re-verify low-confidence entries

Upgrade `confidence: low` entries with primary-source citations. Batch size:
$ARGUMENTS entries if given, otherwise 5.

## Procedure

1. `python3 scripts/reverify_worklist.py --limit <N>` — take the entries in
   the order given (the script already prioritizes categories where
   datasheets likely exist, and skips entries whose `reverify` record is not
   yet due).
2. For each entry, hunt the primary source (WebSearch/WebFetch):
   - manufacturer datasheet / spec table / official mechanical drawing, or
   - the design's official repo/docs for community hardware.
   Check EVERY spec field against it, not just the ones flagged in notes.
3. Apply corrections following AGENTS.md rules strictly:
   - a value you cannot source stays as-is (or becomes `null` if it was a
     guess), flagged in `notes` — never invent, never average conflicts
     (tier-1 wins; note the conflict).
   - record old value → new value → source (URL, revision/date) in `notes`.
   - upgrade `confidence` only to what the new citations support:
     `high` needs a working URL to a primary source; verify it yourself
     (the validator only checks for a URL-like citation);
     retailer-only corroboration is `medium`.
   - an entry that stays `low` gets a `reverify` record — the only thing
     that stops it being re-hunted every batch:
     `reverify: {checked: 'YYYY-MM-DD', outcome: source_unreachable | unpublished}`
     (quoted date). `source_unreachable` = a primary source exists but could
     not be loaded from this environment; `unpublished` = sources were read
     and the values (or the product) are not published — a legitimate
     outcome for community designs (toolhead weights/CFMs). Replace any
     existing `reverify` record; do not append a dated "re-verified, no
     change" paragraph to `notes` — notes carry the places checked and what
     they showed, the date and outcome live in `reverify`. Recheck intervals
     are `REVERIFY_RECHECK_DAYS` in scripts/validate.py.
   - an entry upgraded off `low` drops its `reverify` record (validated).
4. Regenerate affected board/PSU aggregates per AGENTS.md, then run all
   gates before committing: `python3 scripts/validate.py`,
   `python3 scripts/check_docs.py`, `python3 scripts/gen_schema.py --validate`.
5. Branch `reverify-YYYY-MM-DD`, one commit
   (`fix(<category>): re-verify <n> low-confidence entries`, body lists each
   old→new+source), push, open a PR with `gh pr create` summarizing per-entry
   findings. Do NOT push to main — data changes get human review.
6. If a datasheet contradicts a plausibility band in validate.py, do not
   weaken the band to make it pass — flag it in the PR body for human review.
