# Data Layer and ESCO Graph

## Knowledge Base Composition

### ESCO v1.2

- Primary ontology layer.
- Skills, occupations, labels, and relationship edges.

### O*NET Overlay

- Importance weighting inputs for scoring criticality.

### Crosswalk

- Official ESCO-O*NET mapping to bridge taxonomies.

## Graph Runtime Model

- NetworkX directed graph loaded at startup.
- Supports:
  - BFS prerequisite expansion.
  - Topological checks.
  - Similarity transfer behavior.

## Persistence Layer

### PostgreSQL + pgvector

Stores:

- Skill and course metadata.
- Session and path outputs.
- Decision ledger.
- Gap reporting signals.

### Redis

Stores:

- Demo profiles.
- LLM semantic cache.
- Session state with TTL.

## Retrieval Strategy

- Two-stage retrieval strategy in PRD:
  - Fast ANN shortlist.
  - Precision rerank.

## Data Integrity Priorities

- Catalog membership integrity for path safety.
- Alias normalization for robust entity mapping.
- Gap surfacing when no coverage exists.
