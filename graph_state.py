

from typing import TypedDict, Annotated, List, Optional, Dict, Any

def update_dict(original: Optional[Dict], new: Optional[Dict]) -> Optional[Dict]:
    """Helper function to merge dictionaries for the state."""
    if original is None:
        original = {}
    if new is not None:
        original.update(new)
    return original

class AgentState(TypedDict):
    """
    Shared memory ("whiteboard") for the agentic pipeline.
    This version is architected to support BOTH autonomous and interactive workflows.
    """
    
    # --- Core Inputs & Workflow Control ---
    initial_request: Dict[str, Any]
    messages: List
    execution_mode: Optional[str]
    
    # --- Orchestrator Outputs ---
    intent_data: Annotated[Optional[Dict[str, Any]], update_dict]
    input_payload: Annotated[Optional[Dict[str, Any]], update_dict]
    
    # --- Interactive Session Data ---
    interaction: Annotated[Optional[Dict[str, Any]], update_dict]
    
    # --- INTERACTIVE FLOW CONTROL FIELDS ---
    interaction_is_required: Optional[bool]
    questions_for_user: Optional[List[Dict[str, Any]]]
    user_answers: Annotated[Optional[Dict[str, Any]], update_dict]
    
    # --- AGENT-SPECIFIC OUTPUT FIELDS ---
    # Poster Agent
    poster_fields: Optional[Dict[str, Any]]
    image_prompt: Optional[str]
    final_image: Optional[str]
    
    # Sales Agent
    sales_conversation: Optional[str]
    predicted_intent: Optional[str] # Will hold the 'overall_intent' from the LLM
    next_best_action: Optional[str] # Will hold the final recommendation
    
    # ✨ NEW FIELD FOR THE ADVANCED ANALYSIS ✨
    sales_analysis_report: Optional[Dict[str, Any]] # Will hold the full JSON report
    
    # --- Generic Final Result ---
    final_result: Optional[Dict[str, Any]]
    
    # --- Meta / Error Handling ---
    errors: Optional[List[str]]