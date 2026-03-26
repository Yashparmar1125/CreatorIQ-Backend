from __future__ import annotations

import json
from typing import Any

from src.core.config import settings


def _extract_json_payload(raw_text: str) -> dict[str, Any]:
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Gemini response did not contain a valid JSON object")

    return json.loads(raw_text[start : end + 1])


def _fallback_cards_from_topics(topics: list[str]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, topic in enumerate(topics[:5]):
        cards.append(
            {
                "title": topic,
                "volume": "N/A",
                "velocity": f"+{20 + (index * 7)}%",
                "tags": ["Trend", "YouTube"],
            }
        )
    return cards


def _fallback_payload(genre: str, top_topics: list[str], llm_error: str | None = None) -> dict[str, Any]:
    cards = _fallback_cards_from_topics(top_topics)
    recommendations = []
    for index, card in enumerate(cards):
        recommendations.append(
            {
                "title": card["title"],
                "predicted_virality_score": max(40, 82 - (index * 6)),
                "time_to_trend_days": min(10, 3 + index),
                "confidence_level": "Medium",
                "explanation": {
                    "trends_weight_percent": 60,
                    "genre_weight_percent": 40,
                    "hidden_layer_influence": ["momentum", "creator interest"],
                    "trigger_factors": ["curiosity", "opportunity"],
                },
            }
        )

    return {
        "cards": cards,
        "final_recommended_topics": recommendations,
        "hidden_layer_insights": [
            f"{genre} audience reacts strongly to novelty + utility combinations"
        ],
        "rejected_candidates": [],
        "strategic_insights": {
            "emerging_pattern": "Short-cycle topics with clear practical payoff are accelerating.",
            "focus_next_7_days": "Publish early explainers and one tactical implementation video.",
        },
        "llm_error": llm_error,
    }


def _advanced_prompt(genre: str, top_topics: list[str], audience: str, region: str, content_format: str) -> str:
    return f"""
You are an advanced trend forecasting and content strategy AI.

## INPUT DATA

1. Current Trending Topics (Top N):
   {top_topics}

2. My YouTube Channel Genre:
   {genre}

3. Optional Context:

* Audience type: {audience}
* Region focus: {region}
* Content format: {content_format}

---

## TASK OBJECTIVE

Your goal is to predict future high-potential YouTube video topics that are:

* Indirectly connected to current trends (not obvious copies)
* Strongly aligned with my channel genre
* Likely to trend within the next 3-10 days
* Suitable for early content creation (before saturation)

---

## THINKING PROCESS (MANDATORY)

### Step 1: Semantic Expansion

For each trending topic:

* Extract underlying themes
* Identify secondary effects

### Step 2: Hidden Layer Mapping (Markov-style reasoning)

* Build connections between Trend -> Intermediate Concepts -> My Genre
* These intermediate concepts act as hidden states

### Step 3: Topic Generation

Generate 5-6 predicted video topics that:

* Combine multiple signals
* Are early-stage
* Have high curiosity or urgency factor

---

## IMPORTANT RULES

* Do NOT give generic topics
* Avoid direct repetition of trending topics
* Prioritize indirect, high-leverage ideas
* Think like a hedge fund analyst + viral content strategist
* Be predictive, not reactive

---

Return ONLY valid JSON in this exact schema:
{{
  "cards": [
    {{
      "title": "string",
      "volume": "string like 120K",
      "velocity": "string like +85%",
      "tags": ["string", "string"]
    }}
  ],
  "final_recommended_topics": [
    {{
      "title": "string",
      "predicted_virality_score": 0,
      "time_to_trend_days": 0,
      "confidence_level": "Low|Medium|High",
      "explanation": {{
        "trends_weight_percent": 0,
        "genre_weight_percent": 0,
        "hidden_layer_influence": ["string"],
        "trigger_factors": ["string"]
      }}
    }}
  ],
  "hidden_layer_insights": ["string"],
  "rejected_candidates": [
    {{
      "title": "string",
      "reason": "string"
    }}
  ],
  "strategic_insights": {{
    "emerging_pattern": "string",
    "focus_next_7_days": "string"
  }}
}}
""".strip()


def _generate_with_model(prompt: str, model_name: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return (getattr(response, "text", None) or "").strip()


def build_genre_trend_cards(
    genre: str,
    top_topics: list[str],
    audience: str = "General creators",
    region: str = "IN",
    content_format: str = "Short + Long form",
) -> dict[str, Any]:
    if not settings.GEMINI_API_KEY:
        return _fallback_payload(genre, top_topics, llm_error="GEMINI_API_KEY is not configured")

    try:
        import google.generativeai as genai  # noqa: F401
    except ImportError as exc:
        return _fallback_payload(genre, top_topics, llm_error=str(exc))

    prompt = _advanced_prompt(genre, top_topics, audience, region, content_format)
    configured_model = (settings.GEMINI_MODEL or "").strip() or "gemini-1.5-flash"
    model_candidates = [configured_model, "gemini-1.5-flash", "gemini-1.5-pro"]

    raw_text = ""
    last_error: str | None = None
    for model_name in model_candidates:
        try:
            raw_text = _generate_with_model(prompt, model_name)
            if raw_text:
                break
        except Exception as exc:
            last_error = f"{model_name}: {exc}"

    if not raw_text:
        return _fallback_payload(genre, top_topics, llm_error=last_error or "Empty Gemini response")

    try:
        payload = _extract_json_payload(raw_text)
    except Exception as exc:
        return _fallback_payload(genre, top_topics, llm_error=f"Invalid JSON from Gemini: {exc}")

    raw_cards = payload.get("cards")
    if not isinstance(raw_cards, list):
        payload["cards"] = []

    cleaned_cards: list[dict[str, Any]] = []
    for card in payload.get("cards", [])[:6]:
        if not isinstance(card, dict):
            continue

        title = str(card.get("title", "")).strip()
        if not title:
            continue

        cleaned_cards.append(
            {
                "title": title,
                "volume": str(card.get("volume", "N/A")).strip() or "N/A",
                "velocity": str(card.get("velocity", "+0%")).strip() or "+0%",
                "tags": [
                    str(tag).strip()
                    for tag in card.get("tags", [])
                    if str(tag).strip()
                ][:3]
                or ["Trend"],
            }
        )

    if len(cleaned_cards) < 5:
        for fallback in _fallback_cards_from_topics(top_topics):
            if len(cleaned_cards) >= 5:
                break
            if all(existing["title"].lower() != fallback["title"].lower() for existing in cleaned_cards):
                cleaned_cards.append(fallback)

    payload["cards"] = cleaned_cards[:6]
    payload["llm_error"] = None
    return payload
