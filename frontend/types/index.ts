// types/index.ts — matches schemas.py EXACTLY

export interface SkillMastery {
  esco_uri: string;
  label: string;
  p_m: number;       // current mastery 0.0-1.0
  p_l0: number;      // initial mastery
  ci_lower: number;
  ci_upper: number;
  ci_color: 'green' | 'amber' | 'red';
  evidence: string;
}

export interface CourseModule {
  course_id: string;
  title: string;
  hours: number;
  teaches: string[];   // list of esco_uris
  is_mandatory: boolean;
  bkt_delta: number;   // expected mastery gain
  reward_score: number;
  justification_en: string;
  z3_result: 'PASS' | 'FAIL';
  rejection_reason?: string | null;
}

export interface PathVariant {
  label: 'Speed' | 'Balance' | 'Depth';
  lambda_val: number;  // 2.0 | 1.0 | 0.2
  modules: CourseModule[];
  total_hours: number;
  cvs: number;
  skill_coverage_pct: number;
  z3_verified: boolean;
}

export interface PaceResult {
  session_id: string;
  current_mastery: SkillMastery[];
  target_skills: SkillMastery[];
  path_variants: PathVariant[];  // always 3 items
  cvs_nexus: number;
  cvs_legacy: number;
  decision_ledger: Record<string, unknown>;
  diagnostic_required: boolean;
}

export interface QuizResultRequest {
  session_id: string;
  module_id: string;
  answers: boolean[];
}

export interface AnalyzeRequest {
  session_id: string;
  jd_text: string;
}

export interface SSEEvent {
  event_type: 'mastery_map' | 'paths' | 'complete' | 'error' | string;
  payload: unknown;
}

export interface UploadResumeResponse {
  session_id: string;
  resume_text: string;
}
