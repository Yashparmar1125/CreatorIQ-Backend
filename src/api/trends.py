from fastapi import APIRouter, HTTPException, Query

from src.services.trending_topics_service import get_top_trending_topics

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

@router.get("/{trend_id}")
async def get_trend_detail(trend_id: str):
    return {"message": f"Trends: Detail for {trend_id}"}
