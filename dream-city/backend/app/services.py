from .analyzer import analyze, build_vector, city_score, load_cities
from .models import AnalyzeResponse, CityResult
from .scene_config import build_scene_config

CATEGORY_LABELS = {
    "emotion": {"ar": "المشاعر", "en": "emotion"}, "color": {"ar": "الألوان", "en": "color"},
    "weather": {"ar": "الطقس", "en": "weather"}, "time": {"ar": "الوقت", "en": "time"},
    "environment": {"ar": "البيئة", "en": "environment"}, "place": {"ar": "المكان", "en": "place"},
    "dream_type": {"ar": "نوع الحلم", "en": "dream type"}, "motion": {"ar": "الحركة", "en": "motion"},
    "entity": {"ar": "العناصر", "en": "entities"}, "light": {"ar": "الإضاءة", "en": "light"},
    "mood": {"ar": "الأجواء", "en": "mood"}, "keyword": {"ar": "الكلمة المفتاحية", "en": "keyword"},
}

def city_result(city, score, signals, language, metrics=None):
    reasons = []
    for signal in signals:
        profile_weight = city.profile.get(f"{signal.category}:{signal.value}", 0)
        if profile_weight >= 0.48 and signal.score >= 0.18:
            label = CATEGORY_LABELS.get(signal.category, {}).get(language, signal.category)
            reasons.append(f"{label}: {signal.value}")
        if len(reasons) >= 5:
            break
    if not reasons:
        reasons = ["توافق مركب بين عدة أبعاد من الحلم وتكوين المدينة" if language == "ar" else "Composite compatibility across multiple dream dimensions"]
    return CityResult(
        id=city.id, name=city.name, name_ar=city.name_ar, tagline=city.tagline, tagline_ar=city.tagline_ar,
        score=round(score, 3), match_reasons=reasons, palette=city.palette, terrain=city.terrain,
        architecture=city.architecture, road_style=city.road_style, atmosphere=city.atmosphere,
        landmark=city.landmark, water=city.water, vegetation=city.vegetation, density=city.density,
        height=city.height, weather_effect=city.weather_effect,
        scene_config=build_scene_config(city, metrics) if metrics is not None else None,
    )

def analyze_dream(text: str, requested_language: str) -> AnalyzeResponse:
    language, signals, keywords, metrics = analyze(text, requested_language)
    vector = build_vector(signals, metrics)
    scored = sorted(((city, city_score(city, vector)) for city in load_cities()), key=lambda item: item[1], reverse=True)
    best_city, best_score = scored[0]
    alternatives = [city_result(city, score, signals, language, metrics) for city, score in scored[1:6]]
    signal_strength = sum(s.score for s in signals[:12])
    confidence = min(0.98, max(0.16, best_score * 0.92 + min(0.26, signal_strength * 0.025) + min(0.08, metrics.narrative_depth * 0.08)))
    return AnalyzeResponse(
        language=language, confidence=round(confidence, 3), signals=signals, keywords=keywords,
        metrics=metrics, city=city_result(best_city, best_score, signals, language, metrics), alternatives=alternatives,
    )
