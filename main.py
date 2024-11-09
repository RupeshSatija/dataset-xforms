from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import audio_files, image_files, model_files, text_files

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(text_files.router, prefix="/api/text")
app.include_router(image_files.router, prefix="/api/image")
app.include_router(audio_files.router, prefix="/api/audio")
app.include_router(model_files.router, prefix="/api/model")
