from typing import Literal
from pydantic import BaseModel, Field

Category = Literal[
    "emotion", "color", "weather", "time", "environment", "place",
    "dream_type", "motion", "entity", "light", "mood", "keyword"
]

class DreamRequest(BaseModel):
    dream: str = Field(min_length=3, max_length=12000)
    language: Literal["ar", "en", "auto"] = "auto"

class Signal(BaseModel):
    category: Category
    value: str
    score: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)

class AnalysisMetrics(BaseModel):
    calmness: float = Field(ge=0, le=1)
    tension: float = Field(ge=0, le=1)
    mystery: float = Field(ge=0, le=1)
    wonder: float = Field(ge=0, le=1)
    motion: float = Field(ge=0, le=1)
    sensory_density: float = Field(ge=0, le=1)
    narrative_depth: float = Field(ge=0, le=1)
    contradiction_count: int = 0

class CityTemplate(BaseModel):
    id: str
    name: str
    name_ar: str
    tagline: str
    tagline_ar: str
    profile: dict[str, float]
    palette: list[str]
    terrain: str
    architecture: str
    road_style: str
    atmosphere: str
    landmark: str
    water: bool
    vegetation: str
    density: float
    height: float
    weather_effect: str

class SceneConfig(BaseModel):
    terrain: dict
    city: dict
    architecture: dict
    roads: dict
    water: dict
    vegetation: dict
    sky: dict
    weather: dict
    lighting: dict
    landmark: dict
    colors: list[str]
    fantasy: float
    atmosphere: str
    source_profile: dict[str, float]

class CityResult(BaseModel):
    id: str
    name: str
    name_ar: str
    tagline: str
    tagline_ar: str
    score: float
    match_reasons: list[str]
    palette: list[str]
    terrain: str
    architecture: str
    road_style: str
    atmosphere: str
    landmark: str
    water: bool
    vegetation: str
    density: float
    height: float
    weather_effect: str
    scene_config: SceneConfig | None = None

class AnalyzeResponse(BaseModel):
    language: Literal["ar", "en"]
    confidence: float
    signals: list[Signal]
    keywords: list[str]
    metrics: AnalysisMetrics
    city: CityResult
    alternatives: list[CityResult]
