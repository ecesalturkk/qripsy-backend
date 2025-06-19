# Here we Assistant API with Threads & Runs: we create a thread, add a user message, run the assistant on that thread, poll to see if GPT needs to call a function if so, call our backend, submit tool outputs back to GPT and show the GPT reply

# Full Asistants API Flow works correctly and it handles tool calls correctly. Calling backend and passing output back to GPT works.
import openai
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import time

# Loading env variables (loads my OpenAI API key, used for the openai.beta.threads calls)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Loads our Assistant’s ID from .env
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

# Creating a thread (A thread is a conversation container, one Assistant can run multiple threads.)
thread = openai.beta.threads.create()

# Adding user message to the thread
openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Show me esim options for France on iPhone."
)

# Run the assistant on this thread, at this point the assistant will read the message, decide if it wants to call a function (tool) or reply normally.
run = openai.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
)

# Poll for completion
print(" Waiting for Assistant to respond...")
while True:
    run_status = openai.beta.threads.runs.retrieve(thread_id=thread.
    id, run_id=run.id)
    # This loop checks every few seconds if the Assistant is done or needs an action.
    if run_status.status == "completed":
        break
    elif run_status.status == "requires_action":
        # If GPT wants to call a function, we handle the function call here (we extract tool_call and the arguments)
        tool_call = run_status.required_action.submit_tool_outputs.tool_calls[0]
        name = tool_call.function.name
        args = eval(tool_call.function.arguments)  # Caution: Use json.loads() for safety
        print(f" Assistant wants to call {name} with {args}")

        # Send request to your backend (send the arguments to your backend)
        response = requests.post(
            url="https://qripsy-backend.onrender.com/plan_trip",
            json=args
        )

    if name == "get_esim_options":
        response = requests.post(
            url="https://qripsy-backend.onrender.com/get_esim_options",
            json=args
        )
        # We take the response from your backend, submit it back to OpenAI, the Assistant will continue the conversation
        tool_output = response.json()
        openai.beta.threads.runs.submit_tool_outputs(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call.id,
                    "output": str(tool_output)
                }
            ]
        )


    # Waits 2 seconds and check again if not ready yet
    else:
        time.sleep(2)

# Once the run completes, we list messages in the thread, print the final GPT reply.
messages = openai.beta.threads.messages.list(thread_id=thread.id)
final_msg = messages.data[0].content[0].text.value
print("\n Final GPT Reply:\n", final_msg)
