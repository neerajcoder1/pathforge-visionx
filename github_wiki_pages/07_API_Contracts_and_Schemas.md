# API Contracts and Schemas

## API Style

- FastAPI with strict schema validation.
- SSE for progressive analyze responses.

## Core Endpoints

### Resume Upload

Purpose:

- Receive resume.
- Parse and stage session state.

Output:

- Session identifier.

### Analyze

Purpose:

- Execute full PACE orchestration for a session and JD.

Behavior:

- Streams intermediate events and final payload via SSE.

### Quiz Result / Diagnostic Update

Purpose:

- Accept probe or quiz outcomes.
- Update mastery posteriors.
- Trigger replanning if necessary.

## Payload Families

- Current mastery map entries.
- Target skill entries.
- Path variants with module arrays.
- Verification and decision ledger details.
- Comparative metrics like CVS.

## Schema Discipline

- Required fields for mastery include confidence interval and evidence metadata.
- Variant output always includes structural and verification status.
- Validation prevents partially formed records from leaking into UI.

## Contract Design Rationale

- Strong schemas make streaming UIs stable.
- Explicit fields support dual-audience trace rendering.
