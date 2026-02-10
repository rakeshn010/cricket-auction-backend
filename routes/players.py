from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from database import db
import os, shutil

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# PLAYER SELF REGISTRATION
@router.post("/register")
def register_player(
    name: str = Form(...),
    role: str = Form(...),
    category: str = Form(...),
    base_price: int = Form(...),
    photo: UploadFile = File(...)
):
    if db.players.find_one({"name": name}):
        raise HTTPException(status_code=400, detail="Player already exists")

    path = f"{UPLOAD_DIR}/{photo.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    db.players.insert_one({
        "name": name,
        "role": role,
        "category": category,
        "base_price": base_price,
        "photo": path,
        "status": "pending"
    })

    return {"message": "Player registered, waiting for admin approval"}

# ADMIN APPROVE PLAYER
@router.post("/approve")
def approve_player(name: str):
    result = db.players.update_one(
        {"name": name, "status": "pending"},
        {"$set": {"status": "unsold"}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Player not found or already approved")

    return {"message": "Player approved"}

# GET ALL PLAYERS
@router.get("/all")
def get_players():
    return list(db.players.find({}, {"_id": 0}))
