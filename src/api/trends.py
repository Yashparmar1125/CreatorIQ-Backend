from fastapi import APIRouter, HTTPException, Query

from src.services.gemini_trend_insights_service import build_genre_trend_cards
from src.services.trending_topics_service import get_top_trending_topics
from src.services.youtube_genre_service import resolve_youtube_channel_genre

router = APIRouter()

@router.get("/")
async def get_trends():
    return {"message": "Trends: Get trend feed"}


@router.get("/top-5")
async def get_top_5_trending_topics(
    keyword: list[str] = Query(
        ...,
        min_length=1,
        description="Use repeated query params or comma-separated values",
    )
):
    # Support both styles:
    # 1) ?keyword=Machine+Learning&keyword=AI
    # 2) ?keyword=Machine+Learning,AI
    parsed_keywords: list[str] = []
    for item in keyword:
        parts = [part.strip() for part in item.split(",")]
        parsed_keywords.extend([part for part in parts if part])

    if not parsed_keywords:
        raise HTTPException(status_code=422, detail="At least one non-empty keyword is required")

    results: dict[str, list[str]] = {}
    for kw in parsed_keywords:
        try:
            results[kw] = get_top_trending_topics(keyword=kw, top_n=5)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch trending topics for '{kw}': {exc}",
            ) from exc

    return {
        "keywords": parsed_keywords,
        "count": len(parsed_keywords),
        "results": results,
    }


@router.get("/genre-insights")
async def get_genre_insights(
    genre: str = Query(..., min_length=2, description="Genre from yt-data-api-v3")
):
    normalized_genre = genre.strip()
    if not normalized_genre:
        raise HTTPException(status_code=422, detail="Genre cannot be empty")

    try:
        seed_topics = get_top_trending_topics(keyword=normalized_genre, top_n=5)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch top topics for genre '{normalized_genre}': {exc}",
        ) from exc

    try:
        llm_payload = build_genre_trend_cards(genre=normalized_genre, top_topics=seed_topics)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini generation failed for genre '{normalized_genre}': {exc}",
        ) from exc

    return {
        "genre": normalized_genre,
        "seed_topics": seed_topics,
        "cards": llm_payload.get("cards", []),
        "llm": llm_payload,
    }


@router.get("/username-insights")
async def get_username_insights(
    username: str = Query(..., min_length=2, description="YouTube username or handle")
):
    try:
        channel_profile = resolve_youtube_channel_genre(username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to resolve channel for '{username}': {exc}",
        ) from exc

    genre = channel_profile["genre"]
    try:
        seed_topics = get_top_trending_topics(keyword=genre, top_n=5)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch top topics for genre '{genre}': {exc}",
        ) from exc

    try:
        llm_payload = build_genre_trend_cards(genre=genre, top_topics=seed_topics)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini generation failed for genre '{genre}': {exc}",
        ) from exc

    return {
        **channel_profile,
        "seed_topics": seed_topics,
        "cards": llm_payload.get("cards", []),
        "llm": llm_payload,
    }

@router.get("/{trend_id}")
async def get_trend_detail(trend_id: str):
    return {"message": f"Trends: Detail for {trend_id}"}
