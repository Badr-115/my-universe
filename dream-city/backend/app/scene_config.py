from __future__ import annotations

from typing import Any

from .models import AnalysisMetrics, CityTemplate


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _profile(city: CityTemplate, key: str) -> float:
    return float(city.profile.get(key, 0.0))


def build_scene_config(city: CityTemplate, metrics: AnalysisMetrics) -> dict[str, Any]:
    """Convert a semantic city profile into renderer-friendly procedural parameters."""
    terrain = city.terrain.lower()
    architecture = city.architecture.lower()
    road_style = city.road_style.lower()
    weather = city.weather_effect.lower()
    atmosphere = city.atmosphere.lower()

    night = max(_profile(city, "time:night"), 0.25 if "night" in atmosphere else 0.0)
    sunset = _profile(city, "time:sunset")
    dawn = _profile(city, "time:dawn")
    rain = max(_profile(city, "weather:rain"), 1.0 if weather == "rain" else 0.0)
    mist = max(_profile(city, "weather:mist"), 1.0 if weather in {"mist", "fog"} else 0.0)
    snow = max(_profile(city, "weather:snow"), 1.0 if weather == "snow" else 0.0)
    storm = _profile(city, "weather:storm")
    fantasy = _clamp(
        0.28
        + _profile(city, "dream_type:fantasy") * 0.55
        + _profile(city, "dream_type:space") * 0.45
        + metrics.wonder * 0.20
        + metrics.mystery * 0.12
    )

    is_space = terrain == "space" or _profile(city, "environment:space") > 0.65
    is_water = city.water or terrain in {"water", "wet", "coast", "island"}
    is_desert = terrain == "desert" or _profile(city, "environment:desert") > 0.65
    is_forest = terrain in {"forest", "jungle"} or _profile(city, "environment:forest") > 0.65
    is_mountain = terrain in {"mountain", "mountains"} or _profile(city, "environment:mountain") > 0.65

    street_width = 0.72 + (1.0 - city.density) * 1.65
    block_radius = 6.5 + city.density * 4.0
    city_scale = 0.88 + city.height * 0.32 + city.density * 0.18
    building_count = int(32 + city.density * 46)
    average_height = 1.7 + city.height * 5.0
    height_variance = 0.30 + city.height * 0.75

    architecture_kind = "tower"
    if any(word in architecture for word in ("arcad", "courtyard", "low")):
        architecture_kind = "arcade"
    elif any(word in architecture for word in ("organic", "biomorphic", "tree")):
        architecture_kind = "organic"
    elif any(word in architecture for word in ("crystal", "glass", "luminous")):
        architecture_kind = "crystal"
    elif any(word in architecture for word in ("dome", "vault", "desert")):
        architecture_kind = "dome"
    elif any(word in architecture for word in ("spire", "gothic")):
        architecture_kind = "spire"
    elif any(word in architecture for word in ("floating", "orbital")):
        architecture_kind = "floating"

    road_kind = "grid"
    if any(word in road_style for word in ("winding", "organic", "trail")):
        road_kind = "radial"
    elif any(word in road_style for word in ("bridge", "canal")):
        road_kind = "canal"
    elif any(word in road_style for word in ("stone", "cobble")):
        road_kind = "grid_stone"

    vegetation_density = _clamp(
        0.10
        + (0.60 if is_forest else 0.0)
        + (0.35 if not is_desert and city.vegetation not in {"none", "bare"} else 0.0)
        + _profile(city, "environment:forest") * 0.25
    )

    fog_density = _clamp(
        0.002
        + mist * 0.012
        + rain * 0.004
        + metrics.mystery * 0.004
        + (0.003 if not is_space else 0.001)
    )

    if is_space:
        sky_top, sky_bottom = city.palette[0], city.palette[min(2, len(city.palette) - 1)]
    elif night > 0.55:
        sky_top, sky_bottom = city.palette[0], city.palette[min(1, len(city.palette) - 1)]
    elif sunset > 0.45:
        sky_top, sky_bottom = city.palette[min(2, len(city.palette) - 1)], city.palette[0]
    elif dawn > 0.45:
        sky_top, sky_bottom = city.palette[min(3, len(city.palette) - 1)], city.palette[1]
    else:
        sky_top, sky_bottom = city.palette[0], city.palette[min(2, len(city.palette) - 1)]

    return {
        "terrain": {"type": terrain, "water": is_water, "desert": is_desert, "forest": is_forest, "mountain": is_mountain, "space": is_space},
        "city": {
            "scale": round(city_scale, 3), "radius": round(block_radius, 3),
            "density": round(city.density, 3), "building_count": building_count,
            "average_height": round(average_height, 3), "height_variance": round(height_variance, 3),
            "street_width": round(street_width, 3),
        },
        "architecture": {"style": architecture_kind, "source": city.architecture},
        "roads": {"layout": road_kind, "style": city.road_style, "width": round(street_width, 3), "wetness": round(_clamp(rain + (0.25 if "wet" in road_style else 0.0)), 3)},
        "water": {"enabled": is_water, "coverage": round(_clamp(0.12 + city.density * 0.18 + _profile(city, "environment:water") * 0.35), 3), "bridges": int(1 + (2 if is_water else 0) + fantasy * 2)},
        "vegetation": {"type": city.vegetation, "density": round(vegetation_density, 3)},
        "sky": {"top": sky_top, "bottom": sky_bottom, "stars": round(_clamp((0.25 if night > 0.45 else 0.0) + (0.65 if is_space else 0.0) + metrics.mystery * 0.25), 3), "moon": round(_clamp(night * 0.8 + metrics.calmness * 0.15), 3)},
        "weather": {"type": weather, "rain": round(_clamp(rain), 3), "mist": round(_clamp(mist), 3), "snow": round(_clamp(snow), 3), "storm": round(_clamp(storm), 3), "particles": int(80 + metrics.sensory_density * 170 + metrics.mystery * 100)},
        "lighting": {"night": round(_clamp(night), 3), "sunset": round(_clamp(sunset), 3), "dawn": round(_clamp(dawn), 3), "warmth": round(_clamp(0.35 + sunset * 0.55 + metrics.calmness * 0.15), 3), "intensity": round(1.0 + metrics.wonder * 1.1 + metrics.tension * 0.45, 3)},
        "landmark": {"name": city.landmark, "fantasy": round(fantasy, 3), "scale": round(1.2 + fantasy * 2.0, 3)},
        "colors": city.palette,
        "fantasy": round(fantasy, 3),
        "atmosphere": atmosphere,
        "source_profile": city.profile,
    }
