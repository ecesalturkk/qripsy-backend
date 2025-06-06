# this script is designed to simulate how GPT would call our FastAPI backend (local test). This script: Loads your API key from .env. Defines tool (function) schemas that GPT-4o can use. Sends a message to GPT-4o asking for an itinerary. GPT decides to use a tool (like plan_trip). The tool call is forwarded to your FastAPI backend. The backend's result is printed.

# to run this make sure main.py (our FastAPI) is running and in a separate terminal run this script.

import os
import requests
import openai
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

#Loads necessary libraries: requests: to call our FastAPI backend.dotenv: loads our .env file containing our OpenAI API key. OpenAI: OpenAI Python SDK (latest-style client).

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
print(" API Key Loaded:", openai_api_key)

client = OpenAI(api_key=openai_api_key)

# Reads the .env file from the same directory. Loads OPENAI_API_KEY.Initializes the OpenAI client.

functions = [
    # Defines function schemas for GPT to choose from. Must exactly match the input our FastAPI expects.
    {
        "name": "plan_trip",
        "description": "Creates a travel itinerary based on city, number of days, and interests.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "days": {"type": "integer"},
                "interests": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["destination", "days", "interests"]
        }
    },
    {
        "name": "get_esim_options",
        "description": "Returns eSIM plan options based on country and device type.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "device": {"type": "string"}
            },
            "required": ["country", "device"]
        }
    },
    {
        "name": "get_safety_info",
        "description": "Provides emergency numbers and local safety tips for a given country.",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {"type": "string"}
            },
            "required": ["country"]
        }
    },
    {
        "name": "get_translation",
        "description": "Translates a phrase into the selected target language.",
        "parameters": {
            "type": "object",
            "properties": {
                "phrase": {"type": "string"},
                "target_language": {"type": "string"}
            },
            "required": ["phrase", "target_language"]
        }
    },
    {
        "name": "get_local_events",
        "description": "Returns popular local events happening in a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
]
 


def call_backend_function(name, arguments):
    print(f" Calling backend with: {arguments}")
    response = requests.post(f"http://127.0.0.1:8000/{name}", json=arguments)
    return response.json()

# Sends a POST request to our local FastAPI server (running at http://127.0.0.1:8000). The name is ,for instance, "plan_trip" so this becomes: http://127.0.0.1:8000/plan_trip. We must make sure our FastAPI is running when this script executes.

# Main test logic
if __name__ == "__main__":
    print(" Starting assistant test...")

# Send message to GPT. Simulates a user asking GPT to do something.
    messages = [
        {
            "role": "user",
            "content": "Can you create a 2-day Istanbul itinerary with culture and food?"
        }
    ]

# GPT chooses what to do (whether to reply directly or call one of your functions).
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": f} for f in functions],
        tool_choice="auto"
    )
# This extracts what GPT decided to call. If GPT chooses a tool, json.loads() is used here to convert string arguments to a Python dictionary.
    choice = response.choices[0].message

    if choice.tool_calls:
        tool_call = choice.tool_calls[0]
        name = tool_call.function.name
        import json
        args = json.loads(tool_call.function.arguments)
        print(f" GPT wants to call `{name}`")
        print(" With arguments:", args)

        # Calls our FastAPI endpoint and prints the result.
        result = call_backend_function(name, args)
        print(" Backend result:")
        print(result)
    else:
        print("✉️ GPT replied normally:")
        print(choice.content)
