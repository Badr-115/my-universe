from fastapi.testclient import TestClient

from app.analyzer import load_cities, load_lexicon
from app.main import app
from app.services import analyze_dream


def test_catalog_has_240_distinct_city_profiles():
    cities = load_cities()
    assert len(cities) == 240
    assert len({item.id for item in cities}) == 240
    assert all(item.palette and item.profile for item in cities)


def test_english_and_arabic_inputs_have_structured_results():
    assert len(load_lexicon()) >= 30
    for text, language in [
        ("I flew over a blue ocean in the rain", "en"),
        ("رأيت مدينة زرقاء ومطر في الليل", "ar"),
    ]:
        result = analyze_dream(text, language)
        assert result.language == language
        assert result.city.id.startswith("dream-city-")
        assert len(result.alternatives) == 5
        assert len(result.city.palette) >= 3


def test_api_readiness_and_validation():
    with TestClient(app) as client:
        assert client.get("/api/ready").status_code == 200
        response = client.post("/api/analyze", json={"dream": "I saw blue water", "language": "en"})
        assert response.status_code == 200
        assert response.json()["city"]["id"].startswith("dream-city-")
        invalid = client.post("/api/analyze", json={"dream": "a", "language": "en"})
        assert invalid.status_code == 422
