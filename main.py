import pprint
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from supervisor import app as langgraph_app

# --- Pydantic Models ---
class ServiceRequest(BaseModel):
    service: str  # "poster" | "sales"
    mode: str = "interactive"  # "interactive" | "autonomous"

class ContinueRequest(BaseModel):
    thread_id: str
    user_answers: Dict[str, Any]

# --- FastAPI Setup ---
app = FastAPI(title="Agentic LangGraph Backend", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

# --- Generate Endpoint ---
@app.post("/generate")
async def generate(payload: ServiceRequest):
    print(f"📥 Service requested: '{payload.service}' in '{payload.mode}' mode.")
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    initial_input = {
        "initial_request": {"service": payload.service},
        "execution_mode": payload.mode
    }

    print("🚀 Starting LangGraph execution...")

    if payload.mode == "interactive":
        async for event in langgraph_app.astream(initial_input, config=config):
            print(f"📡 Stream event: {event}")

            if "interaction_manager" in event:
                node_output = event["interaction_manager"]
                print(f"🔍 DEBUG: interaction_manager output: {node_output}")

                if node_output.get("interaction_is_required") and node_output.get("questions_for_user"):
                    print(f"⏸️ Graph paused for user input. Thread ID: {thread_id}")
                    return {
                        "status": "requires_input",
                        "thread_id": thread_id,
                        "questions": node_output["questions_for_user"]
                    }

        final_state = await langgraph_app.aget_state(config=config)
        return format_final_response(final_state)

    else: # Autonomous mode
        final_state = await langgraph_app.ainvoke(initial_input, config=config)
        print("✅ Autonomous graph execution finished.")
        return format_final_response(final_state)

# --- Continue Endpoint ---
@app.post("/continue")
async def continue_workflow(payload: ContinueRequest):
    print(f"▶️ Continuing workflow for thread: {payload.thread_id}")
    config = {"configurable": {"thread_id": payload.thread_id}}
    user_answer_input = {"user_answers": payload.user_answers}

    async for event in langgraph_app.astream(user_answer_input, config=config):
        print(f"📡 Continue stream event: {event}")

        if "interaction_manager" in event:
            node_output = event["interaction_manager"]
            if node_output.get("interaction_is_required") and node_output.get("questions_for_user"):
                print(f"⏸️ Graph paused AGAIN for user input. Thread ID: {payload.thread_id}")
                return {
                    "status": "requires_input",
                    "thread_id": payload.thread_id,
                    "questions": node_output["questions_for_user"]
                }

    final_state = await langgraph_app.aget_state(config=config)
    print("✅ Continued graph execution finished.")
    return format_final_response(final_state)


# --- Response Formatter (FIXED) ---
def format_final_response(state):
    print("\n🕵️‍♂️ --- INSPECTING FINAL STATE --- 🕵️‍♂️")
    # This safely gets the dictionary of values from the state object
    final_state_values = getattr(state, 'values', state)
    pprint.pprint(final_state_values)
    print("🕵️‍♂️ --- END OF FINAL STATE --- 🕵️‍♂️\n")

    if final_state_values.get("final_image"):
        print("🎨 Formatting response for Poster Agent...")
        return {
            "status": "success",
            "agent_type": "poster",
            "image_base64": final_state_values.get("final_image", ""),
            "message": "Poster generated!"
        }
    
    # ✅ --- THIS IS THE FIX --- ✅
    # Instead of looking for just `next_best_action`, we now look for the
    # rich `sales_analysis_report` object. This is a much better indicator
    # that the advanced sales agent ran successfully.
    elif final_state_values.get("sales_analysis_report"):
        print("💼 Formatting response for Advanced Sales Agent...")
        return {
            "status": "success",
            "agent_type": "sales",
            # We still return the top-level items for easy access
            "predicted_intent": final_state_values.get("predicted_intent"),
            "next_best_action": final_state_values.get("next_best_action"),
            # AND we include the full, rich report for our flashy UI
            "sales_analysis_report": final_state_values.get("sales_analysis_report")
        }
    else:
        # This is the fallback for any other case
        return {
            "status": "success", # Changed from 'ok' to be consistent
            "agent_type": "orchestrator",
            "message": "Workflow completed!"
        }