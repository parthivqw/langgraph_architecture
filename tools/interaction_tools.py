



import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from graph_state import AgentState
from tools.poster_tools import POSTER_PROMPT_SKELETON

# --- CONFIGURATION ---
load_dotenv()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
MODEL = 'openai/gpt-oss-120b'


# --- NEW FUNCTION ---
def get_poster_prompt_skeleton() -> str:
    """A simple data provider to fetch the poster skeleton for the manager."""
    print("---TOOL:  fetching poster prompt skeleton---")
    return POSTER_PROMPT_SKELETON


# --- NEW TOOL for INTERACTIVE SALES FLOW ---
def generate_clarifying_sales_questions(state: AgentState) -> dict:
    """
    Analyzes a sales conversation and generates 3 highly specific,
    context-driven questions to extract critical missing information.
    """
    print("---TOOL: Generatitheng Clarifying Sales Questions---")
    
    interaction_data = state.get("interaction", {})
    collected_content = interaction_data.get("collected_content", {})
    
    conversation = collected_content.get("conversation", "No conversation provided.")
    operation = collected_content.get("operation", "Intent Analysis") # Default operation

    system_prompt = f"""
You are a Sales Intelligence Question Generator. Your job is to analyze a sales conversation and generate 3 highly specific, context-driven questions that extract missing critical information for the selected operation.

OPERATION: {operation}
SALES CONVERSATION:
---
{conversation}
---

INSTRUCTIONS:
1. READ the conversation carefully and identify the biggest information gaps that prevent a clear analysis for the selected operation. Focus on inconsistencies, unanswered threads, missing context, or behavioral shifts.
2. GENERATE exactly 3 questions that are directly tied to the conversation details.
3. The questions should have clear multiple-choice answers (A, B, C, D) to guide the user.
4. Return ONLY a valid JSON object with a single key "questions", which is a list of question objects.

EXAMPLE FORMAT:
{{
  "questions": [
    {{
      "id": "clarification_1",
      "text": "The client mentioned a 'tight budget' on Day 1 but then asked about premium features on Day 4. What is the most likely reason for this shift?",
      "ui_element": "radio",
      "options": [
        "A) They secured more funding.",
        "B) A different, more senior stakeholder is now involved.",
        "C) They are testing our flexibility on pricing.",
        "D) Their initial budget concern was a negotiation tactic."
      ]
    }},
    {{ "id": "clarification_2", "text": "...", "ui_element": "radio", "options": [...] }},
    {{ "id": "clarification_3", "text": "...", "ui_element": "radio", "options": [...] }}
  ]
}}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        print(f"✅ Generated sales questions: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ ERROR generating sales questions: {e}")
        # Fallback with generic questions
        return {
            "questions": [
                {"id": "fallback_1", "text": "What is the primary industry of the client?", "ui_element": "text_input"},
                {"id": "fallback_2", "text": "Who is the key decision-maker you've been in contact with?", "ui_element": "text_input"}
            ]
        }
    
  # --- Tool 1: The Dynamic Question Generator ---
# ✅ --- THIS IS THE NEW, SMARTER QUESTION GENERATOR --- ✅
def generate_questions_from_skeleton(main_idea: str, prompt_skeleton: str) -> dict:
    """
    Uses an LLM to generate a CONSOLIDATED and CONTEXT-AWARE set of questions.
    """
    print(f"---TOOL: 🧠 Generating CONTEXT-AWARE questions for '{main_idea}'---")
    
    meta_prompt = f"""
You are an expert UI/UX designer and prompt engineer. Your goal is to take a user's core idea and generate a minimal, intuitive set of questions to build a poster.

**USER'S CORE IDEA:** "{main_idea}"

**YOUR TASKS:**
1.  **Internalize the Core Idea:** All your generated content must be relevant to this idea.
2.  **Generate CONSOLIDATED Questions:** Instead of asking 15 questions, group related items. Ask for visual style first, then present all text choices in a single step. The goal is 3-4 steps MAXIMUM.
3.  **Generate CONTEXT-AWARE Text Options:** For fields like "heading" or "subheading," generate 3 creative variations that are DIRECTLY related to the user's core idea.
4.  **Output structured JSON:** Return a JSON object with a "questions" key.

**EXAMPLE OUTPUT STRUCTURE:**
{{
  "questions": [
    {{
      "id": "visual_style",
      "text": "First, let's set the mood. Choose a visual style:",
      "ui_element": "radio",
      "options": ["Cinematic", "Neon / Glow", "Minimalist / Clean", "Corporate / Professional"]
    }},
    {{
      "id": "text_content",
      "text": "Great. Now select the content for your poster. Here are some AI-generated options based on your idea:",
      "ui_element": "form",
      "fields": [
        {{ "id": "heading", "label": "Main Heading", "type": "radio", "options": ["AI For All", "Python Mastery", "Code the Future"] }},
        {{ "id": "subheading", "label": "Subheading", "type": "radio", "options": ["Your AI Journey Starts Here", "Next-Level Python Bootcamp", "Build What's Next"] }}
      ]
    }},
    {{
      "id": "effects",
      "text": "Finally, add some extra visual flair (optional):",
      "ui_element": "multiselect",
      "options": ["Lens Flare", "Holograms", "Soft Gradient", "Smoke"]
    }}
  ]
}}

**PROMPT SKELETON TO REFERENCE:**
---
{prompt_skeleton}
---

Now, generate the consolidated, context-aware questions for the user's core idea: "{main_idea}".
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": meta_prompt}],
            temperature=0.4,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        print("✅ Dynamically generated a SMALLER set of questions.")
        return result
    except Exception as e:
        print(f"❌ ERROR generating consolidated questions: {e}")
        return {"questions": [{"id": "fallback", "text": "Error generating questions.", "ui_element": "text", "options": []}]}

