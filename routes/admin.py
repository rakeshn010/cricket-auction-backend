from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()

@router.post("/create")
def create_admin():
    if db.admin.find_one({"username": "admin"}):
        return {"message": "Admin already exists"}

    db.admin.insert_one({
        "username": "admin",
        "password": "admin123"
    })
    return {"message": "Admin created"}

@router.post("/login")
def admin_login(username: str, password: str):
    admin = db.admin.find_one({
        "username": username,
        "password": password
    })
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

    return {"message": "Admin login success"}
