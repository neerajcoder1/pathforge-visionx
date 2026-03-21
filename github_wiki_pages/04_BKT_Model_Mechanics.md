# BKT Model Mechanics

## Purpose

BKT represents uncertainty in user skill mastery and updates beliefs as evidence arrives.

## Per-Skill Parameters

- P(L0): prior mastery.
- P(T): transition probability after relevant learning action.
- P(S): slip probability.
- P(G): guess probability.

## Update Equations

Correct response posterior:

P(L|correct) = P(L)*(1-P(S)) / [P(L)*(1-P(S)) + (1-P(L))*P(G)]

Incorrect response posterior:

P(L|incorrect) = P(L)*P(S) / [P(L)*P(S) + (1-P(L))*(1-P(G))]

Learning transition:

P(M) = P(L) + (1-P(L))*P(T)

## Initialization Signals in PRD

- Proficiency cues from extraction language.
- Recency decay using exponential form.
- Skill complexity-informed transition defaults.

## Worked Example from PRD Narrative

Given skill Docker:

- Baseline mastery = 0.32
- Evidence update leads to latent mastery = 0.554
- Transition probability = 0.35

Projected mastery:

P(M) = 0.554 + (1-0.554)*0.35 = 0.7101

Rounded = 0.71

## Operational Role in NEXUS

- Drives eligibility gating.
- Drives expected reward deltas.
- Supports confidence interval communication.
- Supports live adaptation after diagnostic probes.

## Practical Constraints

- BKT calibration quality affects recommendation quality.
- Sparse evidence can widen uncertainty.
- Human overrides and probes are essential in low-confidence states.
