import os
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load API key
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Your assistant ID 
ASSISTANT_ID = "asst_ycdcK3wwWe2YLxt1ThRKVtZq"  

def call_backend_function(name, args):
    if name == "plan_trip":
        print(" Sending request to backend...")
        response = requests.post(
            "https://qripsy-backend.onrender.com/plan_trip",
            json=args
        )
        return response.json()
    return {"error": "Unknown function"}

# Start a thread
thread = client.beta.threads.create()

# Simulate user message
user_message = "Plan a 3-day cultural and food trip to Rome"
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_message
)

# Run the assistant (let it decide what to do)
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID
)

# Poll until run is complete
import time
while run.status != "completed":
    time.sleep(1)
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

# Check for tool call
messages = client.beta.threads.messages.list(thread_id=thread.id)
latest = messages.data[0]
if latest.role == "assistant" and latest.content[0].type == "tool_call":
    tool_call = latest.content[0].tool_call
    name = tool_call.function.name
    args = eval(tool_call.function.arguments)  # trusted source (GPT)
    
    result = call_backend_function(name, args)

    # Send result back to assistant
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="tool",
        tool_call_id=tool_call.id,
        content=str(result)
    )

    # Re-run GPT to get final reply
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

# Show final response
final_messages = client.beta.threads.messages.list(thread_id=thread.id)
print("\n GPT's Final Response:")
print(final_messages.data[0].content[0].text.value)
