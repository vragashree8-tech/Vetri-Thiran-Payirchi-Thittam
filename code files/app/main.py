from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="ComicCraft API", description="Create illustrated five-panel stories with Gemini and Hugging Face.", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
app.include_router(router)


@app.get("/health")
def health():
    from app.config import settings
    return {"status": "ok", "gemini_configured": bool(settings.gemini_api_key), "huggingface_configured": bool(settings.hf_token)}
