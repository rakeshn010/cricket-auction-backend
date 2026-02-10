from fastapi import APIRouter, HTTPException
from database import db

router = APIRouter()

# START AUCTION
@router.post("/start")
def start_auction():
    db.auction.delete_many({})
    db.auction.insert_one({
        "current_player": None,
        "highest_bid": 0,
        "highest_team": None,
        "status": "LIVE"
    })
    return {"message": "Auction started"}

# SET CURRENT PLAYER
@router.post("/set-player")
def set_player(player_name: str):
    player = db.players.find_one({"name": player_name, "status": "unsold"})
    if not player:
        raise HTTPException(status_code=404, detail="Player not approved or not found")

    db.auction.update_one({}, {
        "$set": {
            "current_player": player_name,
            "highest_bid": player["base_price"],
            "highest_team": None
        }
    })
    return {"message": "Player set for auction"}

# PLACE BID (TEAM ONLY)
@router.post("/bid")
def place_bid(team_name: str, bid_amount: int):
    auction = db.auction.find_one({})
    if not auction or auction["status"] != "LIVE":
        raise HTTPException(status_code=400, detail="Auction not live")

    team = db.teams.find_one({"name": team_name})
    if not team:
        raise HTTPException(status_code=403, detail="Invalid team")

    if auction["current_player"] is None:
        raise HTTPException(status_code=400, detail="No player set")

    if bid_amount <= auction["highest_bid"]:
        raise HTTPException(status_code=400, detail="Bid must be higher")

    if team["remaining_budget"] < bid_amount:
        raise HTTPException(status_code=400, detail="Not enough budget")

    db.auction.update_one(
        {},
        {"$set": {
            "highest_bid": bid_amount,
            "highest_team": team_name
        }}
    )

    return {"message": "Bid accepted"}

# SELL PLAYER
@router.post("/sell")
def sell_player():
    auction = db.auction.find_one({})
    if not auction or not auction["highest_team"]:
        raise HTTPException(status_code=400, detail="No bids")

    db.teams.update_one(
        {"name": auction["highest_team"]},
        {
            "$push": {
                "players": {
                    "name": auction["current_player"],
                    "price": auction["highest_bid"]
                }
            },
            "$inc": {"remaining_budget": -auction["highest_bid"]}
        }
    )

    db.players.update_one(
        {"name": auction["current_player"]},
        {"$set": {
            "status": "sold",
            "sold_to": auction["highest_team"],
            "price": auction["highest_bid"]
        }}
    )

    db.auction.update_one({}, {
        "$set": {
            "current_player": None,
            "highest_bid": 0,
            "highest_team": None
        }
    })

    return {"message": "Player sold"}

# MARK UNSOLD
@router.post("/unsold")
def mark_unsold():
    auction = db.auction.find_one({})
    if not auction or not auction["current_player"]:
        raise HTTPException(status_code=400, detail="No active player")

    db.players.update_one(
        {"name": auction["current_player"]},
        {"$set": {"status": "unsold"}}
    )

    db.auction.update_one({}, {
        "$set": {
            "current_player": None,
            "highest_bid": 0,
            "highest_team": None
        }
    })

    return {"message": "Marked unsold"}

# LIVE AUCTION
@router.get("/live")
def live():
    return db.auction.find_one({}, {"_id": 0})

# UNSOLD PLAYERS
@router.get("/unsold")
def unsold_players():
    return list(db.players.find({"status": "unsold"}, {"_id": 0}))
