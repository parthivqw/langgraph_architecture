

from graph_state import AgentState
# ✅ Correctly separated imports - The manager only uses its own tools now
from tools.interaction_tools import generate_questions_from_skeleton, get_poster_prompt_skeleton
from tools.interaction_tools import generate_clarifying_sales_questions

def interaction_manager_node(state: AgentState) -> dict:
    """
    Manages a one-by-one interactive conversation for multiple agents.
    For the Poster Agent, it now uses a two-step, context-aware process.
    """
    print("\n---NODE: 🤖 INTERACTION MANAGER (Smart Q&A) 🤖---\n")

    if user_answers := state.get("user_answers"):
        print(f"🧠 Resuming interaction. Processing user answers: {user_answers}")
        interaction_data = state.get("interaction", {"collected_content": {}})
        collected_content = interaction_data.get("collected_content", {})
        collected_content.update(user_answers)
        interaction_data["collected_content"] = collected_content
        state["user_answers"] = None
    else:
        print("✨ First run of interaction. Initializing a blank state.")
        interaction_data = {"collected_content": {}}
        
    recommended_app = state.get("intent_data", {}).get("recommended_app")
    # ✅ --- THIS IS THE FIX --- ✅
    # We define collected_content here, outside the agent-specific logic,
    # so it's ALWAYS available for every agent flow.
    collected_content = interaction_data.get("collected_content", {})
    
    print(f"🎬 Recommended App: '{recommended_app}'")

    # --- SALES AGENT FLOW (Unchanged) ---
    if recommended_app == "Lead/Sales Intent Generator":
        if 'conversation' not in collected_content or 'operation' not in collected_content:
            question_to_ask = { "id": "sales_initial_input", "text": "Please provide the sales conversation and select the primary analysis goal.", "ui_element": "form", "fields": [{"id": "conversation", "label": "Sales Conversation Text", "type": "textarea"}, {"id": "operation", "label": "Analysis Goal", "type": "radio", "options": ["Intent Analysis", "Next Best Action"]}]}
            return {"interaction_is_required": True, "questions_for_user": [question_to_ask], "interaction": interaction_data}
        if 'question_queue' not in interaction_data:
            all_questions = generate_clarifying_sales_questions(state).get("questions", [])
            interaction_data['question_queue'] = all_questions if all_questions else []
        if interaction_data.get('question_queue'):
            next_question = interaction_data['question_queue'].pop(0)
            return {"interaction_is_required": True, "questions_for_user": [next_question], "interaction": interaction_data}
    
    # --- DYNAMIC POSTER AGENT FLOW (Now works on first run) ---
    elif recommended_app == "Poster Generator":
        # Step 1: Get the user's core idea if we don't have it yet.
        if 'main_idea' not in collected_content:
            print("🎨 Poster flow initiated. Asking for the core concept.")
            question_to_ask = {
                "id": "main_idea",
                "text": "What is the poster about? Be descriptive (e.g., 'An EdTech poster for a Python bootcamp').",
                "ui_element": "textarea"
            }
            return {"interaction_is_required": True, "questions_for_user": [question_to_ask], "interaction": interaction_data}

        # Step 2: If we have the core idea, generate the context-aware follow-up questions.
        if 'question_queue' not in interaction_data:
            print(f"💡 Core idea received. Generating smart follow-up questions...")
            main_idea = collected_content['main_idea']
            prompt_skeleton = get_poster_prompt_skeleton()
            all_questions = generate_questions_from_skeleton(main_idea, prompt_skeleton).get("questions", [])
            interaction_data['question_queue'] = all_questions
            print(f"🗂️ Stored {len(all_questions)} consolidated questions in the queue.")

        # Step 3: Ask the next question from our new, shorter queue.
        if interaction_data.get('question_queue'):
            next_question = interaction_data['question_queue'].pop(0)
            print(f"❓ Asking next poster question: '{next_question.get('id')}'.")
            return {"interaction_is_required": True, "questions_for_user": [next_question], "interaction": interaction_data}

    # --- EXIT ---
    print("✅ All questions answered. Interaction phase complete.")
    return {
        "interaction_is_required": False,
        "questions_for_user": [],
        "interaction": interaction_data
    }

