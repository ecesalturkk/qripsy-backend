# This file defines a FastAPI backend that: Accepts a POST request at /plan_trip. Expects a JSON body with destination, days, and interests. Responds with a generated itinerary using basic formatting

from fastapi import FastAPI, HTTPException
# FastAPI: The main web framework we are using to build the backend API
from pydantic import BaseModel
# Used to define and validate the shape of incoming JSON data.
from typing import List
# Used to define the type of the interests field — a list of strings.
import re

app = FastAPI()
# Creates an instance of the FastAPI app, this is the core of our backend that routes requests

class SafetyRequest(BaseModel):
    country: str
# Safety info endpoint expects a country name, so the request model just needs 'country'

class TripRequest(BaseModel):
    destination: str
    days: int
    interests: List[str]
# Defines the expected input format for  /plan_trip endpoint

@app.post("/plan_trip")
async def plan_trip(req: TripRequest):
    # Defines a POST endpoint at /plan_trip. FastAPI will automatically parse and validate incoming JSON against TripRequest. req will be an instance of TripRequest, already validated.

    itinerary = {}
    # Initializes an empty dictionary to hold the day-by-day trip plan.

    for day in range(1, req.days + 1):
        # Safely pick interests even if the list is short/empty
        morning_interest = req.interests[0] if req.interests else "sightseeing"
        afternoon_interest = req.interests[1] if len(req.interests) > 1 else morning_interest
        evening_interest = req.interests[-1] if req.interests else morning_interest

        itinerary[f"Day {day}"] = {
            "morning": f"Explore {req.destination} in the morning, focusing on {morning_interest}.",
            "afternoon": f"Visit local attractions related to {afternoon_interest}.",
            "evening": f"Dine at a recommended place or relax with a local activity tied to {evening_interest}."
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

    # For now, mapping simplified to country categories, can later add country-specific logic
    country = req.country.lower()
    if country in ["usa", "canada", "mexico"]:
        region = "North America"
    elif country in ["france", "germany", "italy", "spain", "uk"]:
        region = "Europe"
    else:
        region = "Global"

    # Real packages from our PDF
    plans = [
        {
            "name": "Qrispy Go",
            "type": "Pay-as-you-go",
            "data": "Flexible (user top-up)",
            "price": "Based on usage",
            "coverage": "Global",
            "duration": "No expiry",
            "activation": "Whenever user activates",
            "segment": "Frequent travellers, flexibility, value"
        },
        {
            "name": "Qrispy Data Plan",
            "type": "Package",
            "data": "1-3-5-10-20GB",
            "price": "Varies by region",
            "coverage": "Country/Region",
            "duration": "Day, Week, 2 Weeks, Month",
            "activation": "When user arrives",
            "segment": "One-off, cost-conscious"
        },
        {
            "name": "Qrispy Unlimited Plan",
            "type": "Unlimited Package",
            "data": "1/2/3 GB per day, then throttled",
            "price": "Subscription or flat rate",
            "coverage": region,
            "duration": "Daily/Weekly/Monthly",
            "activation": "When user arrives",
            "segment": "Users who want no limits"
        },
        {
            "name": "Qrispy Multi Plan",
            "type": "Pack+",
            "data": "30-40-60GB (shared)",
            "price": "Varies",
            "coverage": region,
            "duration": "Day, Week, 2 Weeks, Month",
            "activation": "When user arrives",
            "segment": "Families, Friends, Nomads, Teams"
        },
        {
            "name": "Qrispy Global Membership",
            "type": "Subscription",
            "data": "Unlimited or fixed",
            "price": "Monthly/Yearly",
            "coverage": region,
            "duration": "Subscription-based",
            "activation": "When user arrives",
            "segment": "Expats, Students, Digital Nomads"
        }
    ]

    return {
        "country": req.country,
        "device": req.device,
        "plans": plans
    }

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
