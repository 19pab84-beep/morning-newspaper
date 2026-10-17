# Document handoff check

This is a local document review gate, not an automation or a quality-scoring model.
Authoritative editorial instructions, reports and edition files remain on Drive.

After rendering, inspect every page and write an external JSON report with:
`pdf_sha256`, `pages_inspected` ([1,2,3,4]), `technical_errors` ([] on success),
`editorial_checks` (logic, specificity, repetition, visual, continuity, sources,
canon: each contains observed evidence), `defects` and `limitations`.
Each defect records severity, description, status and verification for a fixed item.
Critical and major defects must be fixed before handoff. Rerender and inspect again.
Never treat APPROVED_FOR_PILOT in a manuscript as proof of review completion.

Run from the repository:

    python -m v3.editorial.review_gate /path/to/review.json /path/to/final.pdf

An altered PDF invalidates the report. Tests cover stale reviews, missing pages,
missing editorial evidence, and unresolved serious defects despite technical PASS.
This verifies evidence completeness; prose quality and honesty of the observations
still require actual editorial judgment. It does not approve publication or printing.
The feature floor is 250 words, not a target to fill with repetition.
