

#=========================================================================================
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph_state import AgentState
from agents.interaction_manager import interaction_manager_node
from agents.poster_agent import run_poster_agent_node, run_interactive_poster_flow_node
from agents.sales_agent import run_sales_agent_node
from tools.orchestrator_tools import prepare_poster_payload_node, prepare_sales_payload_node
import os
import json

# --- 1. THE NODE: Its only job is to update the state ---
def override_intent_node(state: AgentState) -> dict:
    """
    Reads the initial request and adds the 'intent_data' to the state.
    It returns a dictionary, which is the correct output for a node.
    """
    print("---NODE: Overriding Intent---")
    service = state.get("initial_request", {}).get("service")

    # This path assumes app_registry.json is in the same directory as supervisor.py
    registry_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app_registry.json'))
    with open(registry_path, 'r') as f:
        registry = json.load(f)

    if service == "sales":
        app_name = "Lead/Sales Intent Generator"
        intent_text = "Analyze sales conversation and generate next best action"
    elif service == "poster":
        app_name = "Poster Generator"
        intent_text = "Generate poster content based on selected fields"
    else:
        app_name = "orchestrator"
        intent_text = "No specific app selected"

    intent_data = {
        "status": "ok",
        "intent": intent_text,
        "recommended_app": app_name,
        "entrypoint": registry.get(app_name, {}).get("entrypoint"),
        "required_fields": registry.get(app_name, {}).get("required_fields", [])
    }
    
    return {"intent_data": intent_data}

# --- 2. THE ROUTER: Its only job is to decide the next step ---
def route_after_intent(state: AgentState) -> str:
    """
    Reads the state and returns a string to route the workflow.
    """
    print("---ROUTER: Deciding path after intent override---")
    execution_mode = state.get("execution_mode")
    service = state.get("initial_request", {}).get("service")

    if execution_mode == "interactive":
        return "interaction_manager"
    else: # Autonomous mode
        if service == "sales":
            # In a real autonomous flow, you might have a different prep step
            return "sales_agent_auto" 
        elif service == "poster":
            # This would be the entry point for the autonomous poster flow
            return "poster_agent_auto"
        else:
            return END

# --- 3. THE ROUTER AFTER INTERACTION (FIXED) ---
def after_interaction_router(state: AgentState) -> str:
    """
    This router directs the flow AFTER the interaction_manager has run.
    """
    if state.get("interaction_is_required", False):
        return "interaction_manager" # Loop back if more questions are needed
    
    # Interaction is complete, route to the correct agent
    intent_data = state.get("intent_data", {})
    recommended_app = intent_data.get("recommended_app")
    
    if recommended_app == "Poster Generator":
        # ✅ THE FIX: Point to the correct interactive poster node
        return "poster_agent_interactive"
    elif recommended_app == "Lead/Sales Intent Generator":
        return "sales_agent_auto"
    else:
        return END

# --- STATE GRAPH DEFINITION ---
workflow = StateGraph(AgentState)

# --- ADD NODES ---
workflow.add_node("override_intent", override_intent_node)
workflow.add_node("interaction_manager", interaction_manager_node)
# Autonomous nodes (can be placeholders if not used)
workflow.add_node("poster_agent_auto", run_poster_agent_node) 
workflow.add_node("sales_agent_auto", run_sales_agent_node)
# Interactive node for poster
workflow.add_node("poster_agent_interactive", run_interactive_poster_flow_node)

# --- GRAPH ENTRY POINT ---
workflow.set_entry_point("override_intent")

# --- CONNECT NODES (EDGES) ---
workflow.add_conditional_edges(
    "override_intent",
    route_after_intent,
    {
        "interaction_manager": "interaction_manager",
        "poster_agent_auto": "poster_agent_auto",
        "sales_agent_auto": "sales_agent_auto",
        END: END
    }
)

workflow.add_conditional_edges(
    "interaction_manager",
    after_interaction_router,
    {
        "interaction_manager": "interaction_manager",
        "poster_agent_interactive": "poster_agent_interactive",
        "sales_agent_auto": "sales_agent_auto",
        END: END
    }
)

# Define end points for the agents
workflow.add_edge("poster_agent_auto", END)
workflow.add_edge("sales_agent_auto", END)
workflow.add_edge("poster_agent_interactive", END)


# --- COMPILE GRAPH ---
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

print("✅ Supervisor graph compiled: Full interactive poster flow is now online.")
