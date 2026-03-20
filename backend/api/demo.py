from fastapi import APIRouter

router = APIRouter()


@router.get("/demo/{demo_id}")
def get_demo(demo_id: int):
    # Predefined demo responses

    demo_data = {
        1: {
            "session_id": "demo-1",
            "current_mastery": [{"skill": "Python", "level": 0.6}],
            "target_skills": [{"skill": "Backend Development", "level": 0.9}],
            "path_variants": [
                {
                    "label": "Speed",
                    "modules": ["FastAPI Basics", "API Deployment"],
                    "hours": 10,
                }
            ],
            "cvs_nexus": 0.85,
            "cvs_legacy": 0.5,
            "decision_ledger": {"reason": "Optimized for quick learning"},
            "diagnostic_required": False,
        }
    }

    return demo_data.get(demo_id, {"error": "Demo not found"})
