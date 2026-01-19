from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, trackers

app = FastAPI(
    title="AI Life Tracker",
    description="Voice-first AI-powered life tracking",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(trackers.router)


@app.get("/")
async def root():
    return {"message": "AI Life Tracker API", "env": settings.env}


@app.get("/health")
async def health():
    return {"status": "healthy"}
