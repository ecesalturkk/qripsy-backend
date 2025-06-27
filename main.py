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


class ConversationRequest(BaseModel):
    message: str

# about competitors
BLOCKED_KEYWORDS = [
    "competitor", "openai", "chatgpt", "claude", "gemini", "bard", "pi",
    "meta ai", "anthropic", "perplexity", "mistral", "llama", "groq", 
    "comparison", "vs", "compare", "better than", "alternative", "benchmark"
]

# language
PROFANITY_WORDS = [
    "fuck", "shit", "bitch", "asshole", "bastard", "damn", "crap", "dick", "piss",
    "fucker", "fucking", "retard", "douche", "slut", "whore"
]

# sexual stuff
SEXUAL_WORDS = [
    "sex", "porn", "nude", "naked", "boobs", "breasts", "vagina", "penis", "dildo",
    "cum", "orgasm", "anal", "blowjob", "masturbate"
]

@app.post("/conversation")
async def handle_conversation(req: ConversationRequest):
    user_message = req.message.lower()

    if any(word in user_message for word in BLOCKED_KEYWORDS):
        return {
            "allowed": False,
            "reason": "competitor_policy",
            "response": "I'm unable to answer questions about competitors. Let me know how I can help with your travel plans!"
        }

    if any(word in user_message for word in PROFANITY_WORDS):
        return {
            "allowed": False,
            "reason": "profanity_detected",
            "response": "Please avoid using offensive language so I can assist you better."
        }

    if any(word in user_message for word in SEXUAL_WORDS):
        return {
            "allowed": False,
            "reason": "inappropriate_content",
            "response": "I'm here to help with travel-related queries. Please keep the conversation respectful."
        }

    return {
        "allowed": True,
        "response": "Your message is accepted and being processed."
    }
