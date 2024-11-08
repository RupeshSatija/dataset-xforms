from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers import audio_files, model_files, text_files

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(text_files.router, prefix="/api/text")
app.include_router(audio_files.router, prefix="/api/audio")
app.include_router(model_files.router, prefix="/api/3d")

# Mount static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
