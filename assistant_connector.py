import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the function schema
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
                },
            },
            "required": ["destination", "days", "interests"],
        },
    }
]

# Prepare a clear user input
user_input = {
    "role": "user",
    "content": "Plan a 3-day trip to Rome based on history, art, and culture."
}

# Step 1: Ask GPT what to do
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[user_input],
    tools=[{"type": "function", "function": functions[0]}],
    tool_choice="auto"
)

# Step 2: Check GPT's reply
message = response.choices[0].message

print("\n DEBUG: GPT Message:")
print(message)

if message.tool_calls:
    tool_call = message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)

    print(f"\n GPT wants to call `{tool_call.function.name}` with:")
    print(json.dumps(function_args, indent=2))

    # Step 3: Call local FastAPI backend
    try:
        backend_response = requests.post(
            url="https://qripsy-backend.onrender.com/plan_trip",
            json=function_args,
            timeout=10
        )
        backend_response.raise_for_status()
        result = backend_response.json()
        print("\n Backend responded with:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(" Backend error:", str(e))
else:
    print("⚠️ GPT did not decide to call any function.")
