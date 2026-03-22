from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_trends():
    return {"message": "Trends: Get trend feed"}

@router.get("/{trend_id}")
async def get_trend_detail(trend_id: str):
    return {"message": f"Trends: Detail for {trend_id}"}
