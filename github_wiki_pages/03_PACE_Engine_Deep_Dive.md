# PACE Engine Deep Dive

PACE stands for Probabilistic Adaptive Curriculum Engine.

## Input

- Resume text and extracted skill signals.
- Job description skill targets.
- ESCO-linked skill graph.
- Course catalog with prerequisites and coverage metadata.

## Output

- Three path variants: Speed, Balance, Depth.
- Module-level reasoning and verification status.
- Mastery and target skill structures for frontend views.

## Step-by-Step Pipeline

### Step 1: Mastery Matrix Initialization

- Convert extraction output to ESCO-linked skill entries.
- Initialize BKT state per skill.

### Step 2: JD Target Construction

- Extract JD skill intents.
- Map tokens to graph entities through alias and fuzzy logic.

### Step 3: Gap Discovery

- Identify target skills below mastery threshold.
- Expand upstream prerequisites through graph traversal.

### Step 4: Masked Action Space

- Build eligible module set only where prerequisites are satisfied.
- Remove modules that are pedagogically invalid for current mastery.

### Step 5: Multi-Objective Reward

For each eligible module m:

Reward(m) = sum over skills k of [Delta mastery(k) * criticality(k)] minus lambda * duration(m)

Lambda values:

- Speed: 2.0
- Balance: 1.0
- Depth: 0.2

### Step 6: Path Assembly

- Rank modules by reward for each lambda.
- Build candidate paths.
- Enforce ordering through topological constraints.

### Step 7: Formal Verification

- Validate each path via Z3 rules.
- Trigger local replanning on failure.

### Step 8: Trace and Justification

- Persist contrastive decision entries.
- Render human-readable reasoning from structured provenance.

## Why This Engine Is Practical in 24 Hours

- No long-horizon RL training.
- No dynamic policy instability.
- Fast, vectorized scoring and deterministic verification.
- Immediate explainability through explicit intermediate artifacts.
