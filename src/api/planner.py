from fastapi import APIRouter

router = APIRouter()

@router.get("/slots")
async def get_slots():
    return {"message": "Planner: Get schedule slots"}
