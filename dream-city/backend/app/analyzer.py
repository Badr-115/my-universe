import json
import math
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

from .config import get_settings
from .models import AnalysisMetrics, Signal, CityTemplate

ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F]+")
TOKEN_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F]+|[A-Za-z]+(?:'[A-Za-z]+)?")

# Words that intensify nearby evidence. The engine uses them as modifiers rather than
# treating them as standalone dream concepts.
INTENSIFIERS = {
    "ar": {"جداً": 1.35, "جدًا": 1.35, "شديد": 1.25, "شديداً": 1.25, "شديدًا": 1.25, "تماماً": 1.2, "تمامًا": 1.2, "ببطء": 0.82, "بهدوء": 0.78},
    "en": {"very": 1.35, "extremely": 1.5, "deeply": 1.3, "intensely": 1.4, "quietly": 0.8, "gently": 0.82, "slowly": 0.82},
}

NEGATIONS = {"ar": {"ليس", "ليست", "لم", "لن", "لا", "دون", "بدون", "بلا", "لم يكن", "لم تكن"},
             "en": {"not", "never", "no", "without", "didn't", "wasn't", "weren't", "hardly"}}

CONTRAST_MARKERS = {"ar": {"لكن", "ولكن", "رغم", "رغم أن", "مع ذلك", "بينما"},
                    "en": {"but", "however", "although", "though", "while", "despite"}}

@lru_cache
def load_lexicon() -> dict:
    return json.loads(Path(get_settings().lexicon_path).read_text(encoding="utf-8"))

@lru_cache
def load_cities() -> list[CityTemplate]:
    raw = json.loads(Path(get_settings().catalog_path).read_text(encoding="utf-8"))
    return [CityTemplate.model_validate(item) for item in raw]

def normalize_arabic(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه")
    text = re.sub(r"[ًٌٍَُِّْـ]", "", text)
    return text

def normalize_token(token: str) -> str:
    token = token.lower().strip(".,!?؟،:;()[]{}\"'“”‘’")
    if ARABIC_RE.fullmatch(token):
        return normalize_arabic(token)
    return token

def detect_language(text: str, requested: str) -> str:
    if requested in {"ar", "en"}:
        return requested
    ar = len(ARABIC_RE.findall(text))
    en = len(re.findall(r"[A-Za-z]+", text))
    return "ar" if ar >= en else "en"

def tokenize(text: str) -> list[str]:
    return [normalize_token(m.group(0)) for m in TOKEN_RE.finditer(text)]

def _nearby_modifier(tokens: list[str], index: int, language: str) -> float:
    table = INTENSIFIERS[language]
    score = 1.0
    for token in tokens[max(0, index - 3): index]:
        score *= table.get(token, 1.0)
    return max(0.65, min(1.65, score))

def _is_negated(tokens: list[str], index: int, language: str) -> bool:
    """Return True when a nearby negation governs the matched concept.

    Keep the window deliberately small so a negation in a separate clause does not
    erase an otherwise valid dream element.
    """
    previous = tokens[max(0, index - 3): index]
    joined = " ".join(previous)
    return any(token in previous or token in joined for token in NEGATIONS[language])

def _phrase_matches(text: str, lexicon: dict, language: str):
    phrases = lexicon.get("_phrases", {}).get(language, {})
    # Longest-first avoids double counting a phrase and one of its shorter substrings.
    seen_normalized: set[str] = set()
    for phrase, entries in sorted(phrases.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = normalize_arabic(phrase) if language == "ar" else phrase.lower()
        if normalized in seen_normalized:
            continue
        seen_normalized.add(normalized)
        match = re.search(r"(?:^|[\s،,:;.!؟!?]|[وفبكل])" + re.escape(normalized) + r"(?![\w])", text)
        if not match:
            continue
        before = tokenize(text[:match.start()])
        if any(token in NEGATIONS[language] for token in before[-3:]):
            continue
        yield phrase, entries

def analyze(text: str, requested_language: str) -> tuple[str, list[Signal], list[str], AnalysisMetrics]:
    language = detect_language(text, requested_language)
    normalized_text = normalize_arabic(text) if language == "ar" else text.lower()
    tokens = tokenize(text)
    lexicon = load_lexicon()
    categories: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    evidence: dict[tuple[str, str], list[str]] = defaultdict(list)
    evidence_count: dict[tuple[str, str], int] = defaultdict(int)

    # Lexical evidence is only one layer. Scores are later adjusted by modifiers,
    # phrase context, repetition, narrative density and contradictions.
    for index, token in enumerate(tokens):
        entries = lexicon.get(token, [])
        if not entries and language == "ar":
            # A small light-stemming fallback helps common Arabic inflections without
            # introducing a heavyweight NLP dependency.
            candidates = []
            if len(token) > 3:
                candidates.extend([token[1:], token[:-1], token[1:-1]])
                stems = {token}
                for _ in range(3):
                    stems |= {stem[1:] for stem in list(stems) if len(stem) > 3 and stem[0] in "والفبكل"}
                candidates.extend(stems)
                if token.startswith("بال") and len(token) > 5:
                    candidates.append(token[3:])
            entries = next((lexicon.get(candidate, []) for candidate in candidates if lexicon.get(candidate)), [])
        modifier = _nearby_modifier(tokens, index, language)
        negated = _is_negated(tokens, index, language)
        for entry in entries:
            weight = float(entry.get("weight", 1.0)) * modifier
            if negated:
                weight *= 0.12
            category, value = entry["category"], entry["value"]
            categories[category][value] += weight
            evidence_count[(category, value)] += 1
            if token not in evidence[(category, value)]:
                evidence[(category, value)].append(token)

    for phrase, entries in _phrase_matches(normalized_text, lexicon, language):
        for entry in entries:
            category, value = entry["category"], entry["value"]
            categories[category][value] += float(entry.get("weight", 1.0)) * 1.55
            evidence_count[(category, value)] += 1
            evidence[(category, value)].append(phrase)

    # Repetition is meaningful in dreams: repeated concepts receive a diminishing bonus.
    for category, values in categories.items():
        for value in list(values):
            repeats = evidence_count[(category, value)]
            values[value] *= 1.0 + min(0.28, max(0, repeats - 1) * 0.07)

    signals: list[Signal] = []
    for category, values in categories.items():
        total = sum(values.values()) or 1.0
        ranked = sorted(values.items(), key=lambda item: item[1], reverse=True)
        for value, raw_score in ranked[:5]:
            # Preserve relative strength inside each category, while preventing a single
            # long list of weak matches from drowning out a strong concept.
            score = min(1.0, raw_score / max(1.8, total * 0.82))
            signals.append(Signal(category=category, value=value, score=round(score, 3), evidence=evidence[(category, value)][:6]))

    signals.sort(key=lambda signal: (signal.score, signal.category), reverse=True)
    stopwords = set(lexicon.get("_stopwords", []))
    keywords = []
    for token in tokens:
        if token not in stopwords and token not in keywords and len(token) > 2:
            keywords.append(token)
    keywords = keywords[:16]

    metrics = _derive_metrics(signals, text, language)
    return language, signals, keywords, metrics

def _score(signals: list[Signal], category: str, values: set[str]) -> float:
    return min(1.0, sum(s.score for s in signals if s.category == category and s.value in values))

def _derive_metrics(signals: list[Signal], text: str, language: str) -> AnalysisMetrics:
    calm = _score(signals, "emotion", {"calm", "peace", "relief", "joy", "love", "serenity", "هدوء", "راحة", "فرح", "حب", "طمأنينة"})
    tension = _score(signals, "emotion", {"fear", "anxiety", "tension", "sadness", "panic", "خوف", "قلق", "توتر", "حزن", "ذعر"})
    mystery = _score(signals, "dream_type", {"mysterious", "surreal", "cosmic", "غامض", "سريالي", "كوني"})
    wonder = _score(signals, "dream_type", {"wonder", "cosmic", "magical", "دهشة", "سحر", "كوني"})
    motion = min(1.0, sum(s.score for s in signals if s.category == "motion"))
    sensory = min(1.0, (len(signals) / 20) + min(0.35, len(set(x.value for x in signals)) / 45))
    narrative = min(1.0, 0.2 + len(TOKEN_RE.findall(text)) / 65)
    contradiction_count = _count_contradictions(signals)
    # Contradictions increase mystery rather than being discarded: a dream can be both
    # desert and ocean, night and radiant daylight, calm and stormy.
    mystery = min(1.0, mystery + contradiction_count * 0.12)
    return AnalysisMetrics(
        calmness=round(calm, 3), tension=round(tension, 3), mystery=round(mystery, 3),
        wonder=round(wonder, 3), motion=round(motion, 3), sensory_density=round(sensory, 3),
        narrative_depth=round(narrative, 3), contradiction_count=contradiction_count,
    )

def _count_contradictions(signals: list[Signal]) -> int:
    groups = [
        ({"water", "desert", "forest", "snow", "space"}, "environment"),
        ({"day", "night", "dawn", "sunset"}, "time"),
        ({"rain", "sun", "storm", "snow", "fog"}, "weather"),
        ({"calm", "peace", "serenity"}, "emotion"),
        ({"fear", "anxiety", "tension", "panic"}, "emotion"),
    ]
    count = 0
    for values, category in groups:
        active = {s.value for s in signals if s.category == category and s.value in values and s.score >= 0.18}
        if category == "emotion":
            if any(v in active for v in {"calm", "peace", "serenity"}) and any(v in active for v in {"fear", "anxiety", "tension", "panic"}):
                count += 1
        elif len(active) >= 2:
            count += 1
    return count

def build_vector(signals: list[Signal], metrics: AnalysisMetrics) -> dict[str, float]:
    vector = defaultdict(float)
    for signal in signals:
        # Category confidence acts as a second dimension: several strong signals can
        # coexist and contribute to the same city profile.
        vector[f"{signal.category}:{signal.value}"] += signal.score
    vector["meta:calmness"] = metrics.calmness
    vector["meta:tension"] = metrics.tension
    vector["meta:mystery"] = metrics.mystery
    vector["meta:wonder"] = metrics.wonder
    vector["meta:motion"] = metrics.motion
    return vector

def city_score(city: CityTemplate, vector: dict[str, float]) -> float:
    """Score a city from the complete dream vector.

    Profile weights are normalized per city so profiles with more attributes do not
    receive an artificial advantage. Coverage rewards coherent multi-signal matches.
    """
    observed = {key: max(0.0, value) for key, value in vector.items() if value > 0}
    if not observed:
        return 0.0
    dot = city_norm = dream_norm = 0.0
    for key, dream_value in observed.items():
        city_weight = max(0.0, float(city.profile.get(key, 0.0)))
        dot += city_weight * dream_value
        city_norm += city_weight * city_weight
        dream_norm += dream_value * dream_value
    if not city_norm or not dream_norm:
        return 0.0
    cosine = dot / (math.sqrt(city_norm) * math.sqrt(dream_norm))
    matched = sum(1 for key in observed if city.profile.get(key, 0) > 0)
    coverage = min(1.0, matched / min(8.0, max(3.0, len(observed))))
    return round(max(0.0, min(1.0, cosine * 0.78 + coverage * 0.22)), 6)
