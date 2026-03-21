from __future__ import annotations

import json

from fastapi import APIRouter

from backend.api.store import get_redis_client

router = APIRouter()


@router.get("/demo/{demo_id}")
def get_demo(demo_id: int):
    cache_key = f"demo:{demo_id}"
    cached = get_redis_client().get(cache_key)
    if cached:
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            pass

    # Golden, schema-compliant demo response for frontend stability.
    demo_1 = {
        "session_id": "demo-1",
        "current_mastery": [
            {
                "esco_uri": "esco:python",
                "label": "Python",
                "p_m": 0.62,
                "p_l0": 0.55,
                "ci_lower": 0.54,
                "ci_upper": 0.70,
                "ci_color": "amber",
                "evidence": "Built internal automation scripts.",
            },
            {
                "esco_uri": "esco:api-design",
                "label": "API Design",
                "p_m": 0.48,
                "p_l0": 0.42,
                "ci_lower": 0.40,
                "ci_upper": 0.56,
                "ci_color": "amber",
                "evidence": "Documented REST endpoints.",
            },
            {
                "esco_uri": "esco:warehouse-ops",
                "label": "Warehouse Operations",
                "p_m": 0.35,
                "p_l0": 0.30,
                "ci_lower": 0.25,
                "ci_upper": 0.45,
                "ci_color": "red",
                "evidence": "No direct resume evidence.",
            },
        ],
        "target_skills": [
            {
                "esco_uri": "esco:python",
                "label": "Python",
                "p_m": 0.90,
                "p_l0": 0.90,
                "ci_lower": 0.88,
                "ci_upper": 0.92,
                "ci_color": "green",
                "evidence": "Target role requirement.",
            },
            {
                "esco_uri": "esco:api-design",
                "label": "API Design",
                "p_m": 0.85,
                "p_l0": 0.85,
                "ci_lower": 0.83,
                "ci_upper": 0.87,
                "ci_color": "green",
                "evidence": "Target role requirement.",
            },
            {
                "esco_uri": "esco:warehouse-ops",
                "label": "Warehouse Operations",
                "p_m": 0.80,
                "p_l0": 0.80,
                "ci_lower": 0.78,
                "ci_upper": 0.82,
                "ci_color": "green",
                "evidence": "Target role requirement.",
            },
        ],
        "path_variants": [
            {
                "label": "Speed",
                "lambda_val": 2.0,
                "modules": [
                    {
                        "course_id": "MOD-FASTAPI-101",
                        "title": "FastAPI for Internal Logistics APIs",
                        "hours": 6.0,
                        "teaches": ["esco:python", "esco:api-design"],
                        "is_mandatory": True,
                        "bkt_delta": 0.18,
                        "reward_score": 0.82,
                        "justification_en": "High impact on API readiness with minimal time.",
                        "z3_result": "PASS",
                        "rejection_reason": None,
                    }
                ],
                "total_hours": 6.0,
                "cvs": 0.92,
                "skill_coverage_pct": 68.0,
                "z3_verified": True,
            },
            {
                "label": "Balance",
                "lambda_val": 1.0,
                "modules": [
                    {
                        "course_id": "MOD-FASTAPI-101",
                        "title": "FastAPI for Internal Logistics APIs",
                        "hours": 6.0,
                        "teaches": ["esco:python", "esco:api-design"],
                        "is_mandatory": True,
                        "bkt_delta": 0.18,
                        "reward_score": 0.82,
                        "justification_en": "Builds backend foundation for system integration.",
                        "z3_result": "PASS",
                        "rejection_reason": None,
                    },
                    {
                        "course_id": "MOD-LOGISTICS-201",
                        "title": "Logistics Domain Primer for SWE",
                        "hours": 8.0,
                        "teaches": ["esco:warehouse-ops"],
                        "is_mandatory": False,
                        "bkt_delta": 0.24,
                        "reward_score": 0.76,
                        "justification_en": "Bridges product context for faster production onboarding.",
                        "z3_result": "PASS",
                        "rejection_reason": None,
                    },
                ],
                "total_hours": 14.0,
                "cvs": 0.88,
                "skill_coverage_pct": 86.0,
                "z3_verified": True,
            },
            {
                "label": "Depth",
                "lambda_val": 0.2,
                "modules": [
                    {
                        "course_id": "MOD-FASTAPI-101",
                        "title": "FastAPI for Internal Logistics APIs",
                        "hours": 6.0,
                        "teaches": ["esco:python", "esco:api-design"],
                        "is_mandatory": True,
                        "bkt_delta": 0.18,
                        "reward_score": 0.82,
                        "justification_en": "Core technical baseline.",
                        "z3_result": "PASS",
                        "rejection_reason": None,
                    },
                    {
                        "course_id": "MOD-LOGISTICS-201",
                        "title": "Logistics Domain Primer for SWE",
                        "hours": 8.0,
                        "teaches": ["esco:warehouse-ops"],
                        "is_mandatory": False,
                        "bkt_delta": 0.24,
                        "reward_score": 0.76,
                        "justification_en": "Context transfer into operations workflows.",
                        "z3_result": "PASS",
                        "rejection_reason": None,
                    },
                    {
                        "course_id": "MOD-SYSTEM-DESIGN-301",
                        "title": "Scalable Event-Driven Logistics Systems",
                        "hours": 10.0,
                        "teaches": ["esco:api-design", "esco:warehouse-ops"],
                        "is_mandatory": False,
                        "bkt_delta": 0.20,
                        "reward_score": 0.69,
                        "justification_en": "Raises long-term architecture readiness.",
                        "z3_result": "PASS",
                        "rejection_reason": None,
                    },
                ],
                "total_hours": 24.0,
                "cvs": 0.79,
                "skill_coverage_pct": 100.0,
                "z3_verified": True,
            },
        ],
        "cvs_nexus": 0.88,
        "cvs_legacy": 0.57,
        "decision_ledger": {
            "z3_rules_checked": [
                "CATALOG_MEMBERSHIP",
                "PREREQUISITE_SATISFIED",
                "NO_CYCLES",
                "COMPLIANCE_MANDATORY",
            ],
            "options_considered": [
                {
                    "course_id": "MOD-BATCH-LEGACY",
                    "title": "Legacy Batch Processing",
                    "rejection_reason": "Lower reward score than top candidates",
                }
            ],
            "bkt_parameters": {"p_t": 0.35, "p_s": 0.1, "p_g": 0.2},
            "masked_actions_blocked": ["MOD-ADV-DB-401"],
            "justification_model": "qwen-2.5-7b",
            "extraction_model": "phi-4-mini",
        },
        "diagnostic_required": False,
    }

    # Compatibility aliases requested by integration checks.
    demo_1["paths"] = demo_1["path_variants"]
    demo_1["audit_trail"] = demo_1["decision_ledger"]

    demo_data = {1: demo_1}
    payload = demo_data.get(demo_id, {"error": "Demo not found"})

    if "error" not in payload:
        get_redis_client().setex(cache_key, 3600, json.dumps(payload))
    return payload
