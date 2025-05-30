import openai
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load .env file and API key
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")
print(" API Key Loaded:", api_key)

client = openai.OpenAI(api_key=api_key)

# Define backend-executable GPT function
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
    }
]

#  Function that calls your FastAPI backend
def call_backend_function(name, arguments):
    if name == "plan_trip":
        print(" Calling backend with:", arguments)
        response = requests.post("http://127.0.0.1:8000/plan_trip", json=arguments)
        return response.json()

#  Main interaction
if __name__ == "__main__":
    print(" Starting assistant test...")

    messages = [
        {
            "role": "user",
            "content": "Plan a 2-day trip to Istanbul with a focus on culture and food."
        }
    ]

    #  Make GPT call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=[{"type": "function", "function": f} for f in functions],
        tool_choice="auto"
    )

    choice = response.choices[0].message

    #  Handle function call if GPT triggers it
    if choice.tool_calls:
        tool_call = choice.tool_calls[0]
        name = tool_call.function.name
        args = eval(tool_call.function.arguments)  # safe here, coming from GPT

        print(f" GPT wants to call `{name}`")
        print(" With arguments:", args)

        result = call_backend_function(name, args)
        print("\n Backend result:")
        print(result)

    else:
        print("\n GPT replied with a message:")
        print(choice.content)
