# Reasoning Trace and Reliability

## Trace Objectives

- Make every module decision inspectable.
- Support both engineering audit and HR readability.

## Contrastive Decision Ledger

For each key decision, ledger captures:

- Target skill and requirement context.
- Baseline mastery and evidence.
- Eligible set with selected and rejected modules.
- Rejection reasons.
- BKT deltas.
- Z3 result snapshots.
- Human-readable justification.

## Dual-Mode Explainability

### Technical Mode

- Structured trace details.
- Verification outcomes.
- Provenance graph semantics.

### HR Mode

- Concise natural-language rationale.
- Business-readable intent and impact.

## Hallucination Prevention Strategy

PRD defines triple-lock behavior:

1. LLM isolation from planner and verifier.
2. Catalog membership formal check.
3. Prompt grounding constraints for uncovered skills.

## Reliability Position

NEXUS does not claim uncertainty elimination; it claims uncertainty management through explicit confidence signals, formal constraints, and transparent ledgering.
