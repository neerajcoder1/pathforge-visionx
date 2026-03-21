# Operations and Deployment Runbook

## Deployment Intent

Provide a fast, reproducible demo environment with minimal moving parts.

## Runtime Stack

- Application service.
- PostgreSQL + pgvector.
- Redis cache.

## Startup

Recommended from PRD:

- Single docker compose bootstrap command.
- Validate graph and database readiness.
- Confirm UI and API health endpoints.

## Operational Safeguards

- Circuit breaker from remote inference to local fallback.
- Cache-first strategy for demo stability.
- Session TTL strategy in Redis.

## Incident Playbook

### Extraction quality degradation

- Switch to known-good profile set.
- Surface confidence flags.
- Use diagnostic path.

### Inference outage

- Fail over to local fallback model.
- Continue demo from cached outputs.

### Verification failure

- Trigger local replanning.
- Return verified variant only.

## Governance and Transparency

- Label synthetic course catalog as training simulation.
- Preserve honest limitations in external docs.
- Keep dataset citations and license notes explicit.
