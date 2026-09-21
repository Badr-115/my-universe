import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "backend" / "data" / "city_templates.json"

ARCHETYPES = [
    ("Tideglass", "مدينة زجاج المد", "Coastal glass terraces", "coast", "water", "blue", "peace", "night", "coastal"),
    ("Sunscar", "مدينة أثر الشمس", "Amber dunes and wind towers", "dunes", "desert", "gold", "journey", "sunset", "desert"),
    ("Mossveil", "مدينة حجاب الطحلب", "Canopy bridges above a living forest", "forest", "forest", "green", "peace", "dawn", "forest"),
    ("Frostmere", "مدينة بحيرة الصقيع", "Frozen canals beneath pale towers", "snow", "snow", "white", "loneliness", "night", "frozen"),
    ("Astralith", "مدينة الحجر النجمي", "Orbital plazas and luminous spires", "space", "space", "violet", "cosmic", "night", "orbital"),
    ("Rainhaven", "مدينة ملجأ المطر", "Rain roofs and reflective alleys", "wet", "water", "blue", "sadness", "night", "rain"),
    ("Stormreach", "مدينة حافة العاصفة", "Wind-cut towers around a storm harbor", "coast", "water", "red", "fear", "storm", "storm"),
    ("Auroray", "مدينة الشفق", "Layered streets under a luminous sky", "sky", "sky", "violet", "joy", "dawn", "aurora"),
    ("Emberfall", "مدينة سقوط الجمر", "Dark stone districts glowing from below", "city", "desert", "red", "anger", "night", "ember"),
    ("Mooncourt", "مدينة فناء القمر", "Quiet courtyards and silver arcades", "palace", "city", "white", "peace", "night", "lunar"),
    ("Verdigris", "مدينة النحاس الأخضر", "Patinated domes wrapped in gardens", "city", "forest", "green", "love", "day", "garden"),
    ("Mirage Crown", "مدينة تاج السراب", "Floating market roofs above shifting sand", "dunes", "desert", "violet", "anxiety", "sunset", "mirage"),
    ("Blue Hour", "مدينة الساعة الزرقاء", "Long promenades frozen at twilight", "coast", "water", "blue", "loneliness", "sunset", "twilight"),
    ("Cloudstep", "مدينة درج السحاب", "Hanging platforms connected by sky bridges", "tower", "sky", "white", "flight", "day", "cloud"),
    ("Deepwake", "مدينة اليقظة العميقة", "Submerged plazas beneath translucent roofs", "coast", "water", "violet", "submersion", "night", "submerged"),
    ("Hollow Lantern", "مدينة الفانوس المجوف", "Lantern streets around an ancient sanctuary", "sanctuary", "city", "gold", "fear", "night", "lantern"),
    ("Velvet Spring", "مدينة الربيع المخملي", "Soft plazas threaded through flowering trees", "garden", "forest", "green", "joy", "dawn", "spring"),
    ("Iron Orchard", "مدينة البستان الحديدي", "Industrial towers pierced by orchards", "tower", "city", "red", "transformation", "day", "industrial"),
    ("Prism Gate", "مدينة بوابة المنشور", "A portal district built from radiant geometry", "portal", "sky", "violet", "portal", "dawn", "prismatic"),
    ("Golden Echo", "مدينة الصدى الذهبي", "Grand avenues that catch every sunset", "palace", "desert", "gold", "love", "sunset", "royal"),
]

PALETTES = {
    "blue": ["#091B3A", "#1C4E80", "#63B3ED", "#D7F5FF"],
    "gold": ["#2D1B08", "#8C5A18", "#D7A94B", "#FFF0BD"],
    "green": ["#10271B", "#2F6B45", "#7BBF7A", "#D9F0C2"],
    "white": ["#17202A", "#536270", "#DDE8EF", "#FFFFFF"],
    "violet": ["#170C2F", "#4E2A7A", "#A47BE3", "#E8D9FF"],
    "red": ["#2A0E12", "#6E2430", "#C55A4B", "#FFD1B8"],
}

ARCH = ["arcaded", "needle towers", "stepped terraces", "courtyard blocks", "domed halls", "cantilevered platforms"]
ROADS = ["wet stone", "sand ribbons", "moss paths", "ice canals", "glass causeways", "red basalt avenues"]
VEG = ["salt grass", "date palms", "ferns", "silver pines", "floating gardens", "no vegetation"]
WEATHER = ["mist", "clear", "dust", "snow", "starlight", "rain", "wind"]

def profile(environment, place, color, emotion, time, dream_type, weather):
    values = {
        f"environment:{environment}": 0.95,
        f"place:{place}": 0.72,
        f"color:{color}": 0.60,
        f"emotion:{emotion}": 0.58,
        f"time:{time}": 0.52,
        f"dream_type:{dream_type}": 0.62,
        f"weather:{weather}": 0.50,
    }
    return values

def main():
    cities = []
    for archetype_index, (slug, name_ar, tagline, place, environment, color, emotion, time, style) in enumerate(ARCHETYPES):
        for variant in range(12):
            idx = archetype_index * 12 + variant + 1
            palette_key = [color, "blue", "gold", "green", "violet", "white", "red"][(variant + archetype_index) % 7]
            weather = WEATHER[(variant + archetype_index * 2) % len(WEATHER)]
            architecture = ARCH[(variant * 2 + archetype_index) % len(ARCH)]
            road = ROADS[(variant + archetype_index) % len(ROADS)]
            vegetation = VEG[(variant + archetype_index * 2) % len(VEG)]
            density = round(0.28 + ((variant * 7 + archetype_index * 5) % 60) / 100, 2)
            height = round(0.55 + ((variant * 11 + archetype_index * 3) % 80) / 100, 2)
            water = environment == "water" or style in {"submerged", "coastal"} or variant in {3, 9} and environment == "forest"
            city_name = f"{slug} {variant + 1:02d}"
            city_ar = f"{name_ar} {variant + 1:02d}"
            palette = PALETTES[palette_key]
            weather_effect = weather
            city = {
                "id": f"dream-city-{idx:03d}",
                "name": city_name,
                "name_ar": city_ar,
                "tagline": tagline,
                "tagline_ar": name_ar,
                "profile": profile(environment, place, palette_key, emotion, time, style if style in {"cosmic","journey","flight","fall","chase","transformation","portal","submersion"} else "journey", weather),
                "palette": palette,
                "terrain": environment,
                "architecture": architecture,
                "road_style": road,
                "atmosphere": style,
                "landmark": f"{architecture} {['observatory', 'market', 'garden', 'tower', 'archive', 'harbor'][variant % 6]}",
                "water": water,
                "vegetation": vegetation,
                "density": density,
                "height": height,
                "weather_effect": weather_effect,
            }
            cities.append(city)
    OUT.write_text(json.dumps(cities, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated {len(cities)} city templates at {OUT}")

if __name__ == "__main__":
    main()
