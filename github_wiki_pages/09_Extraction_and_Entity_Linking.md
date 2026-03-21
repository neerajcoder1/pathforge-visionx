# Extraction and Entity Linking

## Extraction Goals

- Convert unstructured resume and JD text into structured skill entities.
- Preserve evidence signals for mastery initialization.

## Resume Parsing Path

1. Parse text from PDF.
2. OCR fallback for image-heavy documents.
3. LLM structured extraction for skills and proficiency cues.

## Entity Linking Path

1. Normalize mention text.
2. Resolve direct alias matches.
3. Use fuzzy alias mapping when exact match fails.
4. Optionally use ANN fallback path.

## Reliability Practices from PRD

- Category-aware matching to reduce lookalike confusion.
- Alias dictionaries for abbreviations and legacy terms.
- Confidence-aware unresolved handling.

## Output Contracts

Each linked item should preserve:

- Skill identifier.
- Human-readable label.
- Initial mastery priors.
- Confidence interval fields.
- Evidence phrase.

## Failure Behavior

When extraction quality is weak:

- Mark low-confidence state.
- Trigger diagnostic probing path.
- Avoid fabricating certainty.
