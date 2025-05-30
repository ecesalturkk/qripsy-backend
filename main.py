from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Qrispy API! Visit /docs to test the endpoints."}

class TripRequest(BaseModel):
    destination: str
    days: int
    interests: List[str]

@app.post("/plan_trip")
def plan_trip(data: TripRequest):
    itinerary = {}
    for day in range(1, data.days + 1):
        itinerary[f"Day {day}"] = {
            "morning": f"Explore {data.destination} in the morning, focusing on {data.interests[0]}.",
            "afternoon": f"Visit local attractions related to {data.interests[1] if len(data.interests) > 1 else data.interests[0]}.",
            "evening": f"Dine at a recommended place or relax with a local activity tied to {data.interests[-1]}."
        }
    return {
        "destination": data.destination,
        "days": data.days,
        "itinerary": itinerary
    }

from fastapi import Query
import random

@app.post("/translate_phrase")
def translate_phrase(text: str = Query(...), language: str = Query(...)):
    fake_translations = {
        "es": f"Traducción simulada de '{text}' al español.",
        "fr": f"Traduction simulée de '{text}' en français.",
        "de": f"Simulierte Übersetzung von '{text}' ins Deutsche.",
        "tr": f"'{text}' ifadesi Türkçeye şöyle çevrilebilir:",
        "jp": f"「{text}」の日本語への偽の翻訳。"
    }

    translated = fake_translations.get(language.lower(), f"(Simulated translation of '{text}' in {language})")

    return {
        "original": text,
        "language": language,
        "translated": translated
    }

@app.get("/esim_options")
def get_esim_options(country: str):
    sample_packages = {
        "turkey": [
            {"name": "Qrispy Basic TR", "data": "5GB", "validity": "7 days", "price": "$5"},
            {"name": "Qrispy Pro TR", "data": "10GB", "validity": "15 days", "price": "$9"},
        ],
        "italy": [
            {"name": "Qrispy Travel IT", "data": "8GB", "validity": "10 days", "price": "$7"},
            {"name": "Qrispy Unlimited IT", "data": "Unlimited", "validity": "30 days", "price": "$15"},
        ],
        "usa": [
            {"name": "Qrispy Starter US", "data": "3GB", "validity": "5 days", "price": "$4"},
            {"name": "Qrispy Flex US", "data": "15GB", "validity": "30 days", "price": "$12"},
        ],
        "france": [
            {"name": "Qrispy Bonjour", "data": "6GB", "validity": "7 days", "price": "$6"},
            {"name": "Qrispy Liberté", "data": "12GB", "validity": "20 days", "price": "$11"},
        ],
        "spain": [
            {"name": "Qrispy España", "data": "7GB", "validity": "10 days", "price": "$6"},
            {"name": "Qrispy Fiesta", "data": "20GB", "validity": "30 days", "price": "$14"},
        ],
        "japan": [
            {"name": "Qrispy Sakura", "data": "5GB", "validity": "7 days", "price": "$6"},
            {"name": "Qrispy Zen", "data": "10GB", "validity": "14 days", "price": "$10"},
        ],
        "germany": [
            {"name": "Qrispy Berlin", "data": "8GB", "validity": "10 days", "price": "$7"},
            {"name": "Qrispy Autobahn", "data": "16GB", "validity": "30 days", "price": "$13"},
        ],
        "uk": [
            {"name": "Qrispy UK Lite", "data": "4GB", "validity": "7 days", "price": "$5"},
            {"name": "Qrispy UK Pro", "data": "10GB", "validity": "20 days", "price": "$10"},
        ],
        "australia": [
            {"name": "Qrispy Down Under", "data": "6GB", "validity": "10 days", "price": "$7"},
            {"name": "Qrispy Oz Max", "data": "Unlimited", "validity": "30 days", "price": "$18"},
        ],
        "canada": [
            {"name": "Qrispy Maple", "data": "5GB", "validity": "7 days", "price": "$6"},
            {"name": "Qrispy Great North", "data": "12GB", "validity": "30 days", "price": "$11"},
        ],
    }

    country_key = country.lower()
    packages = sample_packages.get(country_key)

    if not packages:
        return {
            "country": country,
            "message": "Sorry, we don't currently offer packages for this country. Here are popular options:",
            "packages": sample_packages["usa"]
        }

    return {
        "country": country,
        "packages": packages
    }


@app.get("/events")
def get_local_events(city: str):
    example_events = {
        "paris": [
            {"name": "Louvre Late Nights", "type": "Exhibition", "date": "2025-06-01"},
            {"name": "Seine River Jazz Cruise", "type": "Concert", "date": "2025-06-03"}
        ],
        "barcelona": [
            {"name": "Gaudí Art Fest", "type": "Festival", "date": "2025-06-05"},
            {"name": "Sagrada Família Light Show", "type": "Exhibition", "date": "2025-06-07"}
        ],
        "tokyo": [
            {"name": "Shibuya Anime Expo", "type": "Convention", "date": "2025-06-02"},
            {"name": "Cherry Blossom Night Market", "type": "Festival", "date": "2025-06-04"}
        ],
        "new york": [
            {"name": "Central Park Summer Concert", "type": "Concert", "date": "2025-06-06"},
            {"name": "MoMA After Dark", "type": "Exhibition", "date": "2025-06-08"}
        ],
        "istanbul": [
            {"name": "Bosphorus Music Festival", "type": "Festival", "date": "2025-06-09"},
            {"name": "Historical Peninsula Tour", "type": "Exhibition", "date": "2025-06-10"}
        ]
    }

    city_key = city.lower()
    events = example_events.get(city_key)

    if not events:
        return {
            "city": city,
            "message": "Sorry, no events found for this city. Try one of our most popular destinations:",
            "suggested_events": example_events["paris"]
        }

    return {
        "city": city,
        "events": events
    }

@app.get("/safety_info")
def get_safety_info(city: str):
    safety_data = {
        "tokyo": {
            "emergency_numbers": {
                "police": "110",
                "ambulance": "119",
                "fire": "119"
            },
            "tips": "Tokyo is very safe. Carry cash as some shops don’t accept cards.",
            "nearest_embassy": "U.S. Embassy Tokyo"
        },
        "paris": {
            "emergency_numbers": {
                "police": "17",
                "ambulance": "15",
                "fire": "18"
            },
            "tips": "Beware of pickpockets in tourist areas.",
            "nearest_embassy": "U.S. Embassy Paris"
        },
        "istanbul": {
            "emergency_numbers": {
                "police": "155",
                "ambulance": "112",
                "fire": "110"
            },
            "tips": "Avoid unlicensed taxis; use registered ones via mobile apps.",
            "nearest_embassy": "U.S. Consulate Istanbul"
        },
        "new york": {
            "emergency_numbers": {
                "police": "911",
                "ambulance": "911",
                "fire": "911"
            },
            "tips": "Be cautious in less crowded areas after dark.",
            "nearest_embassy": "Your home country's consulate in NYC"
        },
        "barcelona": {
            "emergency_numbers": {
                "police": "112",
                "ambulance": "112",
                "fire": "112"
            },
            "tips": "Petty theft is common in tourist zones. Secure your belongings.",
            "nearest_embassy": "U.S. Consulate Barcelona"
        }
    }

    city_key = city.lower()
    info = safety_data.get(city_key)

    if not info:
        return {
            "city": city,
            "message": "We don’t have safety info for this city yet. Here are general travel safety tips:",
            "general_tips": "Stay in well-lit areas, keep emergency contacts saved, and carry a copy of your passport."
        }

    return {
        "city": city,
        "safety_info": info
    }
