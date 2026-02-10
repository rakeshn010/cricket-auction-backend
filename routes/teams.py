from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()

# ADMIN CREATES TEAM
@router.post("/create")
def create_team(
    name: str,
    username: str,
    password: str,
    budget: int
):
    if db.teams.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="Team already exists")

    db.teams.insert_one({
        "name": name,
        "username": username,
        "password": password,
        "budget": budget,
        "remaining_budget": budget,
        "players": []
    })

    return {"message": "Team created"}

# TEAM LOGIN
@router.post("/login")
def team_login(username: str, password: str):
    team = db.teams.find_one({"username": username, "password": password})
    if not team:
        raise HTTPException(status_code=401, detail="Invalid team credentials")

    return {
        "team_name": team["name"],
        "remaining_budget": team["remaining_budget"]
    }

# TEAM DASHBOARD
@router.get("/dashboard")
def team_dashboard(team_name: str):
    team = db.teams.find_one({"name": team_name}, {"_id": 0, "password": 0})
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team
