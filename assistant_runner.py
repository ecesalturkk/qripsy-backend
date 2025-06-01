import openai
import os
from dotenv import load_dotenv
import requests
from pathlib import Path

# Load API key from .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define your assistant message
messages = [
    {"role": "user", "content": "Plan a 3-day cultural trip to Rome."}
]

# Define tool (same as in OpenAI Assistant panel)
functions = [
    {
        "name": "plan_trip",
        "description": "Creates a travel itinerary based on city, number of days, and interests",
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
    }
]

# Simulate the assistant calling your function
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=[{"type": "function", "function": functions[0]}],
    tool_choice="auto"
)

# Check if tool was triggered
message = response.choices[0].message

if message.tool_calls:
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = eval(tool_call.function.arguments)

    print(" GPT chose to call:", function_name)
    print(" With arguments:", arguments)

    # Now call your live backend API
    res = requests.post(
        "https://qripsy-backend.onrender.com/plan_trip",
        json=arguments
    )

    print(" Backend replied with:")
    print(res.json())

else:
    print("GPT replied normally:")
    print(message.content)
