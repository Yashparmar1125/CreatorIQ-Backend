from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_channels():
    return {"message": "Channels: Get all channels"}

@router.get("/{channel_id}/metrics")
async def get_channel_metrics(channel_id: str):
    return {"message": f"Channels: Metrics for {channel_id}"}
