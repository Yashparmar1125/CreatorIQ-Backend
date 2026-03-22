from fastapi import APIRouter

router = APIRouter()

@router.post("/sessions")
async def create_session():
    return {"message": "Strategy: Create session"}

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    return {"message": f"Strategy: Get session {session_id}"}
