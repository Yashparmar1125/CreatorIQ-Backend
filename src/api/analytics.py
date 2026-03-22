from fastapi import APIRouter

router = APIRouter()

@router.get("/videos")
async def get_video_analytics():
    return {"message": "Analytics: Get video performance"}

@router.get("/summary")
async def get_summary():
    return {"message": "Analytics: Get AI summary"}
