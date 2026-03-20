from fastapi import APIRouter
from backend.api.schemas import QuizResultRequest

router = APIRouter()


@router.post("/quiz-result")
async def quiz_result(data: QuizResultRequest):
    # Dummy logic (we'll upgrade later)

    correct_answers = sum(data.answers)
    total = len(data.answers)

    score = correct_answers / total if total > 0 else 0

    return {
        "session_id": data.session_id,
        "module_id": data.module_id,
        "score": score,
        "message": "Quiz processed successfully",
    }
