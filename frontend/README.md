# NEXUS Frontend — Member 4

## Quick Start

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

## What's built

| File | Description |
|------|-------------|
| `pages/index.tsx` | Main page: upload, JD input, SSE progress, 4-view tabs |
| `components/SkillRadar.tsx` | Animated Recharts radar — current vs target mastery |
| `components/ParetoPaths.tsx` | 3-tab Speed / Balance / Depth Pareto path selector |
| `components/ModuleCard.tsx` | Expandable card with Z3 badge + HR/Technical toggle |
| `components/TraceViewer.tsx` | DAG pipeline + decision ledger + HR mode |
| `components/HRDashboard.tsx` | CVS comparison charts, hours saved, compliance audit |
| `components/DiagnosticProbe.tsx` | 10-question modal, POST /api/quiz-result on submit |
| `lib/api.ts` | All API calls — never import fetch() in components |
| `hooks/useSSEStream.ts` | SSE stream handler, stage tracking, error handling |
| `lib/mockData.ts` | Realistic mock PaceResult for offline/demo mode |
| `types/index.ts` | TypeScript types matching schemas.py 1:1 |

## Integration with Member 3's API

The app connects to `http://localhost:8000` by default. Set `NEXT_PUBLIC_API_URL` in `.env.local` to override.

**All 4 endpoints consumed:**
- `POST /api/upload-resume` → multipart PDF upload
- `POST /api/analyze` → SSE stream, 4 progressive events
- `POST /api/quiz-result` → diagnostic probe submission
- `GET /api/demo/{profile_id}` → instant Redis-cached demo

## Offline / Demo Mode

If the backend is not running, the app automatically falls back to `lib/mockData.ts` (a full realistic `PaceResult`). Every UI view renders correctly.

Click **Demo 1–5** in the nav bar to load pre-cached profiles instantly.

## Done-When Checklist (from execution plan)

- [x] Upload PDF → session created
- [x] SSE progress shows 4 stages (Extracting → Mastery → Paths → Z3)
- [x] Skill Radar animates with Framer Motion
- [x] 3-Tab Pareto (Speed / Balance / Depth) renders
- [x] Click module card → trace expands
- [x] "Explain Like I'm HR" toggle works in both ModuleCard and TraceViewer
- [x] Z3 badge visible and green for verified paths
- [x] Diagnostic Probe modal (10 questions, POST on submit, re-render)
- [x] HR Dashboard: CVS bars show NEXUS > Standard
- [x] Load Demo button (nav + landing page)
- [x] TypeScript strict mode, no `any`
- [x] All API calls in `lib/api.ts`, never raw fetch in components
