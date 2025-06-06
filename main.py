# This file defines a FastAPI backend that: Accepts a POST request at /plan_trip. Expects a JSON body with destination, days, and interests. Responds with a generated itinerary using basic formatting


from fastapi import FastAPI, Request
# FastAPI: The main web framework we are using to build the backend API
# request: (not used here yet, but imported) useful for accessing the raw request if needed
from pydantic import BaseModel
# Used to define and validate the shape of incoming JSON data.
from typing import List
# Used to define the type of the interests field — a list of strings.

app = FastAPI()
# Creates an instance of the FastAPI app => this is the core of our backend that routes requests

class TripRequest(BaseModel):
    destination: str
    days: int
    interests: List[str]
# Defines the expected input format for your /plan_trip endpoint

@app.post("/plan_trip")
async def plan_trip(req: TripRequest):
    # Defines a POST endpoint at /plan_trip. FastAPI will automatically parse and validate incoming JSON against TripRequest. req will be an instance of TripRequest, already validated.

    itinerary = {}
    #Initializes an empty dictionary to hold the day-by-day trip plan.

    for day in range(1, req.days + 1):
        itinerary[f"Day {day}"] = {
            "morning": f"Explore {req.destination} in the morning, focusing on {req.interests[0]}.",
            "afternoon": f"Visit local attractions related to {req.interests[1] if len(req.interests) > 1 else req.interests[0]}.",
            "evening": f"Dine at a recommended place or relax with a local activity tied to {req.interests[-1]}."
        }
    # Loops through each day from 1 to the number of days specified. Creates a basic itinerary for morning, afternoon, and evening using the first, second, and last elements of the interests list respectively. It's dynamic depending on how many interests are provided.

    return {
        "destination": req.destination,
        "days": req.days,
        "itinerary": itinerary
    }
    # Responds with a JSON object containing: The destination, the number of days, and the generated itinerary dictionary
