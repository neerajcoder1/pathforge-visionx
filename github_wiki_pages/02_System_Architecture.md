# System Architecture

## High-Level View

NEXUS follows a client, API, engine, and data-layer architecture with explicit separation of concerns.

## Layers

### 1) Client Layer

Technology in PRD:

- Next.js 15
- Tailwind
- shadcn/ui
- Recharts
- Framer Motion
- react-flow-renderer

Responsibilities:

- Skill Radar visualization.
- Three-path Pareto exploration.
- Reasoning trace views (technical and HR modes).
- HR dashboard with CVS and compliance views.

### 2) API Gateway Layer

Technology in PRD:

- FastAPI 0.115
- Pydantic v2

Responsibilities:

- Request validation.
- Streaming responses via SSE.
- Session orchestration.
- Circuit-breaker style behavior for model outages.

### 3) Service Layer

#### Extraction Service

- Resume/JD parsing.
- LLM-assisted structured extraction.
- OCR fallback path.

#### PACE Engine

- Mastery initialization.
- Eligibility masking.
- Multi-objective module scoring.
- Topological ordering.
- Z3 verification.

#### Trace Service

- Decision ledger creation.
- Provenance structure generation.

#### Justification Service

- Natural-language rendering from structured trace.

### 4) Data Layer

- In-memory NetworkX graph loaded at startup.
- PostgreSQL + pgvector for session and retrieval state.
- Redis for demo cache, response cache, and session state.

## External Inference Layer

- Primary inference on Groq API.
- Local Ollama fallback for resilience.

## Reliability Boundaries

- LLMs are isolated from formal planning and verification.
- Path validity depends on deterministic engine and Z3 checks.
- Cache-first demo mode reduces network dependence.
