# pathforge-visionx

AI-Adaptive Onboarding Engine - Team VisionX

## 🔧 Backend (Member 3 – API & Integration)

### 🚀 Tech Stack

- FastAPI
- Python
- Uvicorn
- Server-Sent Events (SSE)

---

### 📡 API Endpoints

#### 1. Upload Resume

`POST /api/upload-resume`

- Uploads user resume
- Generates session ID
- Stores data for further processing

---

#### 2. Analyze (Streaming)

`POST /api/analyze`

- Processes resume + job description
- Streams intermediate steps:
  - Mastery mapping
  - Path generation
  - Final result
- Uses SSE for real-time feedback

---

#### 3. Quiz Result

`POST /api/quiz-result`

- Evaluates user answers
- Returns score
- (Future: updates mastery model)

---

#### 4. Demo Endpoint (Fallback)

`GET /api/demo/{id}`

- Returns pre-defined results
- Ensures smooth demo even if AI fails

---

### ⚡ Key Features

- 🔄 Streaming API (low latency experience)
- 🧠 Session-based architecture
- 🔗 Modular integration with engine & frontend
- 🛟 Fault-tolerant demo system

---

### ▶️ How to Run Backend

```bash
pip install fastapi uvicorn python-multipart
uvicorn backend.api.main:app --reload
```
