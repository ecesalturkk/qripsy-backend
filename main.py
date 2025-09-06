from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, constr
from typing import List, Dict, Literal, Optional
import string

from routes_chat import router as chat_router
app.include_router(chat_router)


app = FastAPI(title="Qrispy TravelBuddy API", version="0.1.2")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: prod'da domainini ekle
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Types ---
CountryStr = constr(strip_whitespace=True, min_length=2, max_length=64)
DeviceStr  = constr(strip_whitespace=True, min_length=2, max_length=64)
LangStr    = constr(strip_whitespace=True, min_length=2, max_length=32)
CityStr    = constr(strip_whitespace=True, min_length=2, max_length=64)
MessageStr = constr(strip_whitespace=True, min_length=1, max_length=2000)

# --- Base response (success=true default) ---
class BaseOK(BaseModel):
    success: bool = True

# --- Request/Response Models ---
class TripRequest(BaseModel):
    destination: CountryStr
    days: int = Field(ge=1, le=30)
    interests: List[constr(strip_whitespace=True, min_length=1)] = Field(default_factory=list)

class DayPlan(BaseModel):
    morning: str
    afternoon: str
    evening: str

class TripResponse(BaseOK):
    destination: str
    days: int
    itinerary: Dict[str, DayPlan]

class ESIMRequest(BaseModel):
    country: CountryStr
    device: DeviceStr

class ESIMPlan(BaseModel):
    name: str
    type: str
    data: str
    price: str
    coverage: str
    duration: str
    activation: str
    segment: str

class ESIMResponse(BaseOK):
    country: str
    device: str
    region: str
    plans: List[ESIMPlan]

class SafetyRequest(BaseModel):
    country: CountryStr

class SafetyResponse(BaseOK):
    country: str
    emergency_numbers: Dict[str, str]
    tips: str
    source: Literal["mock"]

class TranslationRequest(BaseModel):
    phrase: constr(strip_whitespace=True, min_length=1)
    target_language: LangStr

class TranslationResponse(BaseOK):
    original: str
    language: str
    translation: str

class LocalEventsRequest(BaseModel):
    city: CityStr

class LocalEventsResponse(BaseOK):
    city: str
    events: List[str]

class ConversationRequest(BaseModel):
    message: MessageStr

class ConversationResponse(BaseOK):
    allowed: bool
    reason: Optional[str] = None
    response: Optional[str] = None
    reply: Optional[str] = None

# --- Utils ---
_COMPETITOR_KEYWORDS = {
    "airalo","airhub","betterroaming","bnesim","bytesim","dent","digital republic",
    "easysim","escapesim","esim.sm","esim2fly","esim4travel","esimatic","esim-man",
    "esimple","esimplus","esimx","etravelsim","ezsim","flexiroam","gigago","gigsky",
    "global yo","globalesim","gomoworld","ifree mogo","instabridge esim","jetpac",
    "keepgo","knowroaming","kolet","manet travel","maya mobile","microesim","mobimatter",
    "monty esim","mtx connect","nomad","northsim","rapidesim","redteago","roamify",
    "saily","simoptions","soracom mobile","stork mobile","taro mobile","textr esim",
    "travelkon","trifa","truphone","ubigi","upesim","webbing","wifi map","yesim",
    "yoho mobile","roamless","honest"
}
_PUNCT_TABLE = str.maketrans({c: " " for c in string.punctuation})

def contains_competitor(text: str) -> bool:
    norm = text.casefold().translate(_PUNCT_TABLE)
    tokens = {t for t in norm.split() if t}
    if any(" " in kw and kw in norm for kw in _COMPETITOR_KEYWORDS):
        return True
    return any(kw in tokens for kw in _COMPETITOR_KEYWORDS if " " not in kw)

def infer_region(country: str) -> str:
    c = country.casefold()
    if c in {"usa","united states","united states of america","canada","mexico"}:
        return "North America"
    if c in {"france","germany","italy","spain","uk","united kingdom","england","scotland"}:
        return "Europe"
    return "Global"

# --- Routes ---
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/plan_trip", response_model=TripResponse)
async def plan_trip(req: TripRequest):
    itinerary: Dict[str, DayPlan] = {}
    for day in range(1, req.days + 1):
        morning_interest   = req.interests[0] if req.interests else "sightseeing"
        afternoon_interest = req.interests[1] if len(req.interests) > 1 else morning_interest
        evening_interest   = req.interests[-1] if req.interests else morning_interest
        itinerary[f"Day {day}"] = DayPlan(
            morning=f"Explore {req.destination} in the morning, focusing on {morning_interest}.",
            afternoon=f"Visit local attractions related to {afternoon_interest}.",
            evening=f"Dine at a recommended place or relax with a local activity tied to {evening_interest}."
        )
    return TripResponse(destination=req.destination, days=req.days, itinerary=itinerary)

@app.post("/get_esim_options", response_model=ESIMResponse)
async def get_esim_options(req: ESIMRequest):
    if not req.country or not req.device:
        return ESIMResponse(success=False, country=req.country, device=req.device, region="Unknown", plans=[])
    region = infer_region(req.country)
    plans = [
        ESIMPlan(name="Qrispy Go", type="Pay-as-you-go", data="Flexible (user top-up)",
                 price="Based on usage", coverage="Global", duration="No expiry",
                 activation="Whenever user activates", segment="Frequent travellers, flexibility, value"),
        ESIMPlan(name="Qrispy Data Plan", type="Package", data="1-3-5-10-20GB",
                 price="Varies by region", coverage="Country/Region", duration="Day, Week, 2 Weeks, Month",
                 activation="When user arrives", segment="One-off, cost-conscious"),
        ESIMPlan(name="Qrispy Unlimited Plan", type="Unlimited Package",
                 data="1/2/3 GB per day, then throttled", price="Subscription or flat rate",
                 coverage=region, duration="Daily/Weekly/Monthly", activation="When user arrives",
                 segment="Users who want no limits"),
        ESIMPlan(name="Qrispy Multi Plan", type="Pack+", data="30-40-60GB (shared)",
                 price="Varies", coverage=region, duration="Day, Week, 2 Weeks, Month",
                 activation="When user arrives", segment="Families, Friends, Nomads, Teams"),
        ESIMPlan(name="Qrispy Global Membership", type="Subscription", data="Unlimited or fixed",
                 price="Monthly/Yearly", coverage=region, duration="Subscription-based",
                 activation="When user arrives", segment="Expats, Students, Digital Nomads"),
    ]
    return ESIMResponse(country=req.country, device=req.device, region=region, plans=plans)

@app.post("/get_safety_info", response_model=SafetyResponse)
async def get_safety_info(req: SafetyRequest):
    return SafetyResponse(
        country=req.country,
        emergency_numbers={"police": "112", "ambulance": "113", "fire": "114"},
        tips=f"Be aware of local customs and keep emergency contacts saved while traveling in {req.country}.",
        source="mock",
    )

@app.post("/get_translation", response_model=TranslationResponse)
async def get_translation(req: TranslationRequest):
    return TranslationResponse(
        original=req.phrase,
        language=req.target_language,
        translation=f"Translated '{req.phrase}' to {req.target_language}."
    )

@app.post("/get_local_events", response_model=LocalEventsResponse)
async def get_local_events(req: LocalEventsRequest):
    return LocalEventsResponse(
        city=req.city,
        events=[
            f"Food Festival in {req.city}",
            f"Live music concert in central {req.city}",
            f"Open-air art market this weekend in {req.city}"
        ]
    )

@app.post("/conversation", response_model=ConversationResponse)
async def conversation(req: ConversationRequest):
    if contains_competitor(req.message):
        return ConversationResponse(
            success=False,
            allowed=False,
            reason="competitor_detected",
            response="Sorry, I can't help with questions about competitors. Let me know how I can assist with your travel plans instead!",
        )
    return ConversationResponse(allowed=True, reply="Your message is allowed. How can I help you further?")


