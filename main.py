from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List

app = FastAPI()

class TripRequest(BaseModel):
    destination: str
    days: int
    interests: List[str]

@app.post("/plan_trip")
async def plan_trip(req: TripRequest):
    itinerary = {}
    for day in range(1, req.days + 1):
        itinerary[f"Day {day}"] = {
            "morning": f"Explore {req.destination} in the morning, focusing on {req.interests[0]}.",
            "afternoon": f"Visit local attractions related to {req.interests[1] if len(req.interests) > 1 else req.interests[0]}.",
            "evening": f"Dine at a recommended place or relax with a local activity tied to {req.interests[-1]}."
        }

    return {
        "destination": req.destination,
        "days": req.days,
        "itinerary": itinerary
    }
