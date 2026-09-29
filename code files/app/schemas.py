from pydantic import BaseModel, Field


class ComicRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=1200)
    character_name: str = Field(default="Alex", min_length=1, max_length=60)
    setting: str = Field(default="an enchanted forest", max_length=100)
    tone: str = Field(default="adventurous", max_length=40)
    art_style: str = Field(default="colorful comic book", max_length=60)
    panel_count: int = Field(default=5, ge=3, le=6)


class ComicPanel(BaseModel):
    number: int
    title: str
    scene_description: str
    image_prompt: str
    narration: str
    dialogue: str


class Comic(BaseModel):
    id: str
    title: str
    prompt: str
    character_name: str
    setting: str
    tone: str
    art_style: str
    panels: list[ComicPanel]
    pdf_url: str | None = None
    demo_mode: bool = False
