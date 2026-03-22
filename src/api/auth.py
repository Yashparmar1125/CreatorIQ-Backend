from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
async def register():
    return {"message": "Auth: Register endpoint"}

@router.post("/login")
async def login():
    return {"message": "Auth: Login endpoint"}
