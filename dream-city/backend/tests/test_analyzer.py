from app.analyzer import analyze, build_vector, city_score, load_cities


def values(signals, category):
    return {s.value for s in signals if s.category == category}


def test_arabic_composition_extracts_multiple_dimensions():
    language, signals, keywords, metrics = analyze(
        "كنت أمشي في مدينة هادئة ليلاً، والمطر ينزل والأنوار تنعكس على الشوارع وشعرت بالراحة.", "auto"
    )
    assert language == "ar"
    assert "city" in values(signals, "environment")
    assert "rain" in values(signals, "weather")
    assert "night" in values(signals, "time")
    assert "calm" in values(signals, "emotion")
    assert "glow" in values(signals, "light")
    assert metrics.calmness > metrics.tension


def test_contradictory_environment_is_preserved():
    _, signals, _, metrics = analyze("كنت في صحراء لكن السماء مليئة بالنجوم وكان هناك بحر قريب.", "ar")
    env = values(signals, "environment")
    assert "desert" in env
    assert "water" in env
    assert metrics.contradiction_count >= 1


def test_negation_reduces_false_positive():
    _, signals, _, _ = analyze("لم أشعر بالخوف، كنت هادئاً في مدينة مضيئة.", "ar")
    fear = next((s.score for s in signals if s.category == "emotion" and s.value == "fear"), 0)
    calm = next((s.score for s in signals if s.category == "emotion" and s.value == "calm"), 0)
    assert calm > fear


def test_city_catalog_is_large_and_scores_compositionally():
    cities = load_cities()
    assert len(cities) >= 200
    _, signals, _, metrics = analyze("rainy quiet city at night with blue lights", "en")
    vector = build_vector(signals, metrics)
    scores = sorted(city_score(city, vector) for city in cities)
    assert scores[-1] > scores[0]


def test_scene_config_reflects_city_profile_and_metrics():
    from app.models import AnalysisMetrics
    from app.scene_config import build_scene_config
    city = load_cities()[0]
    metrics = AnalysisMetrics(calmness=0.9, tension=0.1, mystery=0.7, wonder=0.8, motion=0.4, sensory_density=0.6, narrative_depth=0.8)
    config = build_scene_config(city, metrics)
    assert config["city"]["building_count"] >= 24
    assert config["architecture"]["source"] == city.architecture
    assert config["landmark"]["name"] == city.landmark
    assert config["colors"] == city.palette
    assert "weather" in config and "lighting" in config and "water" in config


def test_all_city_profiles_are_renderable_and_not_identical():
    from app.scene_config import build_scene_config
    cities = load_cities()
    fingerprints = set()
    for city in cities:
        cfg = build_scene_config(city, metrics=__import__("app.models", fromlist=["AnalysisMetrics"]).AnalysisMetrics(
            calmness=0.5, tension=0.2, mystery=0.4, wonder=0.3, motion=0.2, sensory_density=0.5, narrative_depth=0.5
        ))
        fingerprints.add((cfg["terrain"]["type"], cfg["architecture"]["style"], cfg["roads"]["layout"], tuple(cfg["colors"]), cfg["landmark"]["name"], cfg["vegetation"]["type"]))
    assert len(fingerprints) >= 100

