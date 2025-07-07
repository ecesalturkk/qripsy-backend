# This file defines a FastAPI backend that: Accepts a POST request at /plan_trip. Expects a JSON body with destination, days, and interests. Responds with a generated itinerary using basic formatting


from fastapi import FastAPI, HTTPException
# FastAPI: The main web framework we are using to build the backend API
from pydantic import BaseModel
# Used to define and validate the shape of incoming JSON data.
from typing import List
# Used to define the type of the interests field — a list of strings.
from pydantic import BaseModel

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

class ESIMRequest(BaseModel):
    country: str
    device: str

@app.post("/get_esim_options")
async def get_esim_options(req: ESIMRequest):
    if not req.country or not req.device:
        raise HTTPException(status_code=400, detail="Country and device are required.")

    esim_data = {
        "country": req.country,
        "device": req.device,
        "plans": [
            {"name": "Basic Plan", "data": "1GB", "price": "$5"},
            {"name": "Standard Plan", "data": "3GB", "price": "$10"},
            {"name": "Unlimited Plan", "data": "∞", "price": "$20"}
        ]
    }
    return esim_data

class SafetyRequest(BaseModel):
    country: str

@app.post("/get_safety_info")
async def get_safety_info(req: SafetyRequest):
    return {
        "country": req.country,
        "emergency_numbers": {
            "police": "112",
            "ambulance": "113",
            "fire": "114"
        },
        "tips": f"Be aware of local customs and keep emergency contacts saved while traveling in {req.country}."
    }
class TranslationRequest(BaseModel):
    phrase: str
    target_language: str

@app.post("/get_translation")
async def get_translation(req: TranslationRequest):
    return {
        "original": req.phrase,
        "language": req.target_language,
        "translation": f"Translated '{req.phrase}' to {req.target_language}."
    }

class LocalEventsRequest(BaseModel):
    city: str

@app.post("/get_local_events")
async def get_local_events(req: LocalEventsRequest):
    return {
        "city": req.city,
        "events": [
            f"Food Festival in {req.city}",
            f"Live music concert in central {req.city}",
            f"Open-air art market this weekend in {req.city}"
        ]
    }

import re

app = FastAPI()

class ConversationRequest(BaseModel):
    message: str

COMPETITOR_KEYWORDS = [
    "Airalo", "Airhub", "BetterRoaming", "BNESIM", "ByteSim", "DENT", "Digital Republic",
    "easySim", "EscapeSIM", "eSIM.sm", "eSIM2Fly", "eSIM4Travel", "Esimatic", "esim-man",
    "eSIMple", "eSIMplus", "eSIMX", "ETravelSim", "Ezsim", "Flexiroam", "GIGAGO", "GigSky",
    "GLOBAL YO", "GlobaleSIM", "GoMoWorld", "iFREE Mogo", "Instabridge eSIM", "Jetpac",
    "Keepgo", "KnowRoaming", "Kolet", "Manet Travel", "Maya Mobile", "MicroEsim", "MobiMatter",
    "Monty eSIM", "MTX Connect", "Nomad", "NorthSIM", "RapideSIM", "RedteaGO", "Roamify",
    "Saily", "SimOptions", "Soracom Mobile", "Stork Mobile", "Taro Mobile", "Textr eSIM",
    "TravelKon", "trifa", "Truphone", "Ubigi", "UPeSIM", "Webbing", "WiFi Map", "Yesim",
    "Yoho Mobile", "Roamless", "Honest"
]

@app.post("/conversation")
async def conversation(req: ConversationRequest):
    for keyword in COMPETITOR_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", req.message, re.IGNORECASE):
            return {
                "allowed": False,
                "reason": "competitor_detected",
                "response": "Sorry, I can't help with questions about competitors. Let me know how I can assist with your travel plans instead!"
            }

    return {
        "allowed": True,
        "reply": "Your message is allowed. How can I help you further?"
    }
