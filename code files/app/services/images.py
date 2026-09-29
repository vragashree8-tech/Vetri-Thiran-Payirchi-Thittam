from pathlib import Path
from uuid import uuid4
from PIL import Image, ImageDraw
from huggingface_hub import InferenceClient
from app.config import settings

ROOT = Path(__file__).resolve().parents[2]
PANEL_DIR = ROOT / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)


def generate_image(prompt: str, comic_id: str, panel_number: int) -> str:
    """Generate via Hugging Face when configured; otherwise create an attractive local demo illustration."""
    filename = f"{comic_id}-{panel_number}.png"
    destination = PANEL_DIR / filename
    use_hf = settings.hf_token and settings.image_provider != "demo"
    if use_hf:
        try:
            client = InferenceClient(model=settings.hf_image_model, token=settings.hf_token, timeout=120)
            image = client.text_to_image(prompt, width=768, height=512)
            image.save(destination)
            return f"/static/panels/{filename}"
        except Exception:
            if settings.image_provider == "huggingface":
                raise
    _make_demo_image(destination, prompt, panel_number)
    return f"/static/panels/{filename}"


def _make_demo_image(path: Path, prompt: str, number: int) -> None:
    w, h = 768, 512
    image = Image.new("RGB", (w, h), "#f8c86b")
    draw = ImageDraw.Draw(image)
    for y in range(h):
        t = y / h
        draw.line((0, y, w, y), fill=(int(83 + 105*t), int(135 + 56*t), int(194 - 65*t)))
    draw.ellipse((545, 56, 655, 166), fill="#ffe6a1")
    draw.polygon([(0,350),(170,190),(335,355),(490,205),(768,380),(768,512),(0,512)], fill="#315c61")
    draw.polygon([(0,420),(210,290),(410,430),(610,275),(768,410),(768,512),(0,512)], fill="#47765e")
    cx = 380 + (number % 2) * 45
    draw.ellipse((cx-48, 285, cx+48, 381), fill="#f3a15f", outline="#fff1cf", width=5)
    draw.rounded_rectangle((cx-42, 365, cx+42, 485), radius=28, fill="#e15c55", outline="#fff1cf", width=5)
    draw.ellipse((cx-20, 317, cx-9, 330), fill="#25384b")
    draw.ellipse((cx+9, 317, cx+20, 330), fill="#25384b")
    draw.arc((cx-19, 328, cx+19, 357), 5, 175, fill="#25384b", width=4)
    draw.rounded_rectangle((24, 24, 744, 100), radius=18, fill=(255, 255, 255))
    label = prompt[:92]
    draw.text((44, 48), label, fill="#25384b")
    image.save(path, "PNG")
