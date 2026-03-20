from pydantic import BaseModel
from typing import List, Optional


class SkillMastery(BaseModel):
    esco_uri: str
    label: str
    p_m: float  # current mastery (0-1)
    p_l0: float  # initial mastery
    ci_lower: float
    ci_upper: float
    ci_color: str  # 'green' | 'amber' | 'red'
    evidence: str


class CourseModule(BaseModel):
    course_id: str
    title: str
    hours: float
    teaches: List[str]  # list of esco_uris
    is_mandatory: bool
    bkt_delta: float
    reward_score: float
    justification_en: str
    z3_result: str  # 'PASS' | 'FAIL'
    rejection_reason: Optional[str] = None


class PathVariant(BaseModel):
    label: str  # 'Speed' | 'Balance' | 'Depth'
    lambda_val: float  # 2.0 | 1.0 | 0.2
    modules: List[CourseModule]
    total_hours: float
    cvs: float
    skill_coverage_pct: float
    z3_verified: bool


class PaceResult(BaseModel):
    session_id: str
    current_mastery: List[SkillMastery]
    target_skills: List[SkillMastery]
    path_variants: List[PathVariant]
    cvs_nexus: float
    cvs_legacy: float
    decision_ledger: dict
    diagnostic_required: bool


class QuizResultRequest(BaseModel):
    session_id: str
    module_id: str
    answers: List[bool]


class AnalyzeRequest(BaseModel):
    session_id: str
    jd_text: str
