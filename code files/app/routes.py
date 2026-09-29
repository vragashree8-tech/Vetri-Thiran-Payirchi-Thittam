from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.schemas import ComicRequest
from app.config import settings
from app.services.story import generate_outline, generate_story
from app.services.images import generate_image, ROOT
from app.services.pdf_export import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory=str(ROOT / "templates"))
COMICS: dict[str, dict] = {}


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


def create_comic(data: ComicRequest) -> dict:
    comic_id = uuid4().hex[:12]
    outline = generate_outline(data)
    story = generate_story(outline, data)
    panels = []
    for panel in story:
        panel = dict(panel)
        panel["image_url"] = generate_image(panel["image_prompt"], comic_id, int(panel["number"]))
        panels.append(panel)
    comic = {"id": comic_id, "title": f"{data.character_name}: {data.prompt[:52].strip()}",
             "prompt": data.prompt, "character_name": data.character_name, "setting": data.setting,
             "tone": data.tone, "art_style": data.art_style, "panels": panels,
             "demo_mode": not bool(settings.gemini_api_key and settings.hf_token)}
    pdf_path = save_pdf(comic)
    comic["pdf_url"] = f"/export/{comic_id}"
    comic["pdf_path"] = str(pdf_path)
    COMICS[comic_id] = comic
    return comic


def generation_error(request: Request, exc: Exception):
    return templates.TemplateResponse(request=request, name="index.html",
        context={"error": f"Comic generation failed: {exc}. Check your API keys or select demo mode."}, status_code=502)


@router.post("/generate", response_class=HTMLResponse)
def generate_form(request: Request, prompt: str = Form(...), character_name: str = Form("Alex"),
                  setting: str = Form("an enchanted forest"), tone: str = Form("adventurous"),
                  art_style: str = Form("colorful comic book"), panel_count: int = Form(5)):
    try:
        comic = create_comic(ComicRequest(prompt=prompt, character_name=character_name, setting=setting, tone=tone, art_style=art_style, panel_count=panel_count))
        return templates.TemplateResponse(request=request, name="comic_preview.html", context={"comic": comic})
    except Exception as exc:
        return generation_error(request, exc)


@router.post("/generate-comic/json")
def generate_json(data: ComicRequest):
    try:
        comic = create_comic(data)
        return {key: value for key, value in comic.items() if key != "pdf_path"}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Comic generation failed: {exc}") from exc


@router.get("/export/{comic_id}")
def export_pdf(comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found. Generate it again to export.")
    path = Path(comic["pdf_path"])
    return FileResponse(path, media_type="application/pdf", filename=f"comiccraft-{comic_id}.pdf")


@router.get("/export-success/{comic_id}", response_class=HTMLResponse)
def export_success(request: Request, comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found")
    return templates.TemplateResponse(request=request, name="export_success.html", context={"comic": comic})


@router.post("/test-image")
def test_image(prompt: str = Form(...)):
    return {"image_url": generate_image(prompt, uuid4().hex[:12], 1)}


