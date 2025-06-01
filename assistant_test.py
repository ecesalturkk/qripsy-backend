import os
import requests
import openai
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

# Loading my API key
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
print(" API Key Loaded:", openai_api_key)

client = OpenAI(api_key=openai_api_key)

# Tool definitions (matching FastAPI endpoints)


functions = [
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


# Function to call FastAPI backend


def call_backend_function(name, arguments):
    print(f" Calling backend with: {arguments}")
    response = requests.post(f"http://127.0.0.1:8000/{name}", json=arguments)
    return response.json()


# Run GPT interaction


if __name__ == "__main__":
    print(" Starting assistant test...")

    messages = [
        {
            "role": "user",
            "content": "Can you create a 2-day Istanbul itinerary with culture and food?"
        }
    ]

    # Call GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": f} for f in functions],
        tool_choice="auto"
    )

    choice = response.choices[0].message

    # Handle function call
    if choice.tool_calls:
        tool_call = choice.tool_calls[0]
        name = tool_call.function.name
        args = eval(tool_call.function.arguments)
        print(f" GPT wants to call `{name}`")
        print(" With arguments:", args)
        result = call_backend_function(name, args)
        print(" Backend result:")
        print(result)
    else:
        print("✉️ GPT replied normally:")
        print(choice.content)
