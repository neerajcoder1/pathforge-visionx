# Z3 Formal Verification Rules

## Why Verification Exists

Path generation alone is not enough; NEXUS must guarantee structural validity before delivery.

## Rule Set

### Rule 1: CATALOG_MEMBERSHIP

All selected module IDs must exist in the loaded catalog.

Impact:

- Prevents invented learning assets.

### Rule 2: PREREQUISITE_SATISFIED

For every selected module, each prerequisite skill must satisfy mastery threshold (e.g., > 0.85).

Impact:

- Prevents pedagogically invalid sequencing.

### Rule 3: NO_CYCLES

The induced prerequisite graph over selected modules must be acyclic.

Impact:

- Guarantees executable order.

### Rule 4: COMPLIANCE_MANDATORY

All mandatory compliance modules must be included.

Impact:

- Enforces policy and governance requirements.

## Replanning Behavior

On UNSAT or failing checks:

1. Identify violating component.
2. Remove or replace violating module.
3. Rescore and regenerate candidate path.
4. Re-verify before release.

## Verification Artifacts in Product

- Variant-level verified status badge.
- Module-level rule outcomes in trace.
- Ledger entries preserving rejection reasons.

## Reliability Argument

Together, these rules provide strong guarantees against:

- Extrinsic hallucination.
- Invalid progression ordering.
- Compliance bypass.
