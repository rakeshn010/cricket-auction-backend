from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routes import admin, players, teams, auction

app = FastAPI(title="Cricket Auction System")

# static files (player photos)
app.mount("/static", StaticFiles(directory="static"), name="static")

# routes
app.include_router(admin.router, prefix="/admin")
app.include_router(players.router, prefix="/players")
app.include_router(teams.router, prefix="/teams")
app.include_router(auction.router, prefix="/auction")

@app.get("/")
def root():
    return {"message": "Cricket Auction Backend Running"}
