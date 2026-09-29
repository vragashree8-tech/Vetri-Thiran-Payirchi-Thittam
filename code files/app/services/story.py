import json
from google import genai
from google.genai import types
from app.config import settings
from app.schemas import ComicRequest, ComicPanel


def _client():
    if not settings.gemini_api_key:
        return None
    return genai.Client(api_key=settings.gemini_api_key)


def generate_outline(request: ComicRequest) -> list[dict]:
    """Create structured panel beats with Gemini; deterministic fallback keeps local setup usable."""
    client = _client()
    if not client:
        return _demo_outline(request)
    prompt = f"""Create exactly {request.panel_count} sequential comic panel beats.
Premise: {request.prompt}
Hero: {request.character_name}. Setting: {request.setting}. Tone: {request.tone}. Art direction: {request.art_style}.
Use a clear beginning, escalation, and satisfying ending. Image prompts must describe a single coherent panel, avoid lettering/text, and repeat the hero's visual traits for consistency."""
    response = client.models.generate_content(
        model=settings.gemini_outline_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[ComicPanel],
            temperature=0.8,
        ),
    )
    parsed = json.loads(response.text or "[]")
    return [item.model_dump() if isinstance(item, ComicPanel) else item for item in parsed]


def _demo_outline(request: ComicRequest) -> list[dict]:
    beats = [
        ("A Curious Beginning", f"{request.character_name} discovers a strange clue that points toward adventure."),
        ("Into the Unknown", f"Following the clue, {request.character_name} ventures deeper into {request.setting}."),
        ("A Surprising Challenge", f"An unexpected obstacle tests {request.character_name}'s courage and cleverness."),
        ("The Turning Point", f"A small act of kindness reveals a clever way to solve the problem."),
        ("A New Beginning", f"{request.character_name} brings the adventure to a joyful, hopeful close."),
        ("One More Mystery", f"Just as everything settles, a final little mystery appears."),
    ]
    return [{"number": i + 1, "title": beats[i][0], "scene_description": beats[i][1],
             "image_prompt": f"{request.art_style} illustration, {beats[i][1]} Main character {request.character_name}, consistent design, expressive composition, no words, no lettering",
             "narration": "", "dialogue": ""} for i in range(request.panel_count)]


def generate_story(outline: list[dict], request: ComicRequest) -> list[dict]:
    """Expand panel beats into narration and dialogue while preserving panel order."""
    client = _client()
    if not client:
        for panel in outline:
            panel["narration"] = panel["scene_description"]
            panel["dialogue"] = f'{request.character_name}: "Let’s see where this leads!"' if panel["number"] == 1 else f'{request.character_name}: "We can do this together!"'
        return outline
    prompt = f"Write concise comic narration and one natural dialogue line for each beat. Keep the exact number, title, scene_description, and image_prompt unchanged. Tone: {request.tone}. Hero: {request.character_name}. Beats: {json.dumps(outline)}"
    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=list[ComicPanel], temperature=0.9),
    )
    return [item.model_dump() for item in json.loads(response.text or "[]")]
