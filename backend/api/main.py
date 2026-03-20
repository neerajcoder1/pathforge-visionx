from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.upload import router as upload_router
from backend.api.analyze import router as analyze_router
from backend.api.quiz import router as quiz_router
from backend.api.demo import router as demo_router

app = FastAPI(title="NEXUS API")  # ✅ FIRST create app

# Allow frontend (Next.js)
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ THEN include router
app.include_router(upload_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "NEXUS API is running 🚀"}


app.include_router(analyze_router, prefix="/api")

app.include_router(quiz_router, prefix="/api")

app.include_router(demo_router, prefix="/api")
