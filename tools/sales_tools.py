

# import os
# import re
# import json
# import torch
# from transformers import BertTokenizerFast, BertForSequenceClassification
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# # --- Tool 1: Split Conversation by Day (NEW HELPER) ---
# def split_conversation_by_day(conversation_text: str) -> list[dict]:
#     """
#     Takes a raw conversation string and splits it into a list of dictionaries,
#     each representing a day's interaction.
#     """
#     print("---TOOL: Splitting Conversation by Day---")
#     # Regex to find "Day X:" patterns
#     # We use a positive lookahead (?=...) to split *before* the pattern, keeping the delimiter
#     days = re.split(r'(?=\bDay \d+:)', conversation_text)
    
#     daily_interactions = []
#     for entry in days:
#         if not entry.strip():
#             continue
        
#         # Extract the "Day X:" part and the content
#         match = re.match(r'(Day \d+:)(.*)', entry, re.DOTALL)
#         if match:
#             day_marker = match.group(1).strip()
#             content = match.group(2).strip()
#             daily_interactions.append({"day_marker": day_marker, "content": content})
            
#     print(f"✅ Split into {len(daily_interactions)} daily interactions.")
#     return daily_interactions


# # --- Tool 2: Predict Sales Intent using Fine-Tuned BERT (UNCHANGED CORE) ---
# model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'fine_tuned_bert'))
# tokenizer = BertTokenizerFast.from_pretrained(model_path)
# model = BertForSequenceClassification.from_pretrained(model_path)
# model.eval()
# label_map = {0: 'Enrolled', 1: 'Ghosted', 2: 'Information Gathering', 3: 'Interested', 4: 'Meeting Scheduled', 5: 'Not Interested', 6: 'Price Concern', 7: 'Wants Demo'}

# def predict_sales_intent_tool(text: str) -> str:
#     """Given a conversation string, return the predicted sales intent."""
#     # This tool is now used for smaller, daily chunks of text.
#     print(f"---TOOL: Predicting intent for chunk: '{text[:50]}...'---")
#     inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
#     with torch.no_grad():
#         outputs = model(**inputs)
#     probs = torch.softmax(outputs.logits, dim=1)
#     pred_class = torch.argmax(probs, dim=1).item()
#     return label_map.get(pred_class, "Unknown Intent")


# # --- Tool 3: Generate Full Sales Analysis using LLM (NEW & POWERFUL) ---
# def generate_sales_analysis_tool(full_conversation: str, daily_analysis: list[dict]) -> dict:
#     """
#     Given the full conversation and a day-by-day intent analysis,
#     generate a comprehensive summary and next best action.
#     """
#     print("---TOOL: Generating Full Sales Analysis with LLM---")
#     client = OpenAI(
#         api_key=os.getenv("GROQ_API_KEY"),
#         base_url="https://api.groq.com/openai/v1"
#     )

#     # Format the daily analysis for the prompt
#     formatted_daily_analysis = json.dumps(daily_analysis, indent=2)

#     system_prompt = f"""
# You are a world-class senior sales analyst. Your task is to analyze a sales conversation by synthesizing the raw text with a pre-computed, day-by-day intent analysis.

# **INSTRUCTIONS:**
# 1.  Read the **FULL CONVERSATION** to understand the complete context, nuance, and relationship.
# 2.  Review the **DAILY INTENT ANALYSIS**. This provides a structured look at the conversation's progression.
# 3.  Synthesize both inputs to create a final, insightful analysis.
# 4.  Your output **MUST** be a valid JSON object with the following three keys:
#     - `summary`: A 2-3 sentence narrative of the sales cycle. How did it start, what were the key turning points, and where is it now?
#     - `overall_intent`: Based on the *most recent* interactions and the overall trend, what is the customer's current primary intent? (e.g., "Ready to Schedule", "Stalling on Price", "Seeking Final Clarification").
#     - `next_best_action`: A single, concrete, and actionable next step for the sales representative. Be specific.

# **FULL CONVERSATION:**
# ---
# {full_conversation}
# ---

# **DAILY INTENT ANALYSIS:**
# ---
# {formatted_daily_analysis}
# ---

# Provide your final analysis as a JSON object only.
# """
#     try:
#         response = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=[{"role": "system", "content": system_prompt}],
#             temperature=0.3,
#             response_format={"type": "json_object"}
#         )
#         result = json.loads(response.choices[0].message.content)
#         print(f"✅ LLM analysis generated successfully.")
#         return result
#     except Exception as e:
#         print(f"❌ ERROR in LLM analysis tool: {e}")
#         # Provide a fallback error structure
#         return {
#             "summary": "Failed to generate LLM analysis due to an API error.",
#             "overall_intent": "Error",
#             "next_best_action": "Review the conversation manually and check API keys."
#         }


import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
import requests
from tenacity import retry, stop_after_attempt, wait_fixed # <-- Import tenacity for retries

load_dotenv()

# --- Tool 1: Split Conversation by Day (UNCHANGED) ---
def split_conversation_by_day(conversation_text: str) -> list[dict]:
    """
    Takes a raw conversation string and splits it into a list of dictionaries,
    each representing a day's interaction.
    """
    print("---TOOL: Splitting Conversation by Day---")
    days = re.split(r'(?=\bDay \d+:)', conversation_text)
    
    daily_interactions = []
    for entry in days:
        if not entry.strip():
            continue
        
        match = re.match(r'(Day \d+:)(.*)', entry, re.DOTALL)
        if match:
            day_marker = match.group(1).strip()
            content = match.group(2).strip()
            daily_interactions.append({"day_marker": day_marker, "content": content})
            
    print(f"✅ Split into {len(daily_interactions)} daily interactions.")
    return daily_interactions


# --- Tool 2: Predict Sales Intent using HUGGING FACE API (NOW WITH RETRIES) ---
HF_API_URL = "https://api-inference.huggingface.co/models/Sanji8421/fine_tuned_BERT"
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
label_map = {
    'LABEL_0': 'Enrolled', 'LABEL_1': 'Ghosted', 'LABEL_2': 'Information Gathering', 
    'LABEL_3': 'Interested', 'LABEL_4': 'Meeting Scheduled', 'LABEL_5': 'Not Interested', 
    'LABEL_6': 'Price Concern', 'LABEL_7': 'Wants Demo'
}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(10)) # <-- THE FIX: Retry 3 times, waiting 10 seconds between attempts
def call_hf_api(payload):
    """Helper function to call the HF API with retry logic."""
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()

def predict_sales_intent_tool(text: str) -> str:
    """Given a conversation chunk, calls the Hugging Face Inference API to get the predicted sales intent."""
    print(f"---TOOL: Predicting intent via Hugging Face for: '{text[:50]}...'---")
    
    if not HF_TOKEN:
        return "Error: HUGGINGFACE_TOKEN not found."

    payload = {"inputs": text}
    
    try:
        result = call_hf_api(payload)
        if result and result[0]:
            predicted_label = result[0][0]['label']
            print(f"✅ HF Prediction Successful: {label_map.get(predicted_label)}")
            return label_map.get(predicted_label, "Unknown Intent")
        else:
            return "Unknown Intent"
            
    except Exception as e:
        print(f"❌ ERROR calling Hugging Face API after retries: {e}")
        return "Error in Intent Prediction"


# --- Tool 3: Generate Full Sales Analysis using LLM (UPDATED MODEL) ---
def generate_sales_analysis_tool(full_conversation: str, daily_analysis: list[dict]) -> dict:
    """
    Given the full conversation and a day-by-day intent analysis,
    generate a comprehensive summary and next best action.
    """
    print("---TOOL: Generating Full Sales Analysis with LLM---")
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1"
    )

    formatted_daily_analysis = json.dumps(daily_analysis, indent=2)

    system_prompt = f"""
You are a world-class senior sales analyst. Your task is to analyze a sales conversation by synthesizing the raw text with a pre-computed, day-by-day intent analysis. Your output MUST be a valid JSON object with three keys: `summary`, `overall_intent`, and `next_best_action`.

**FULL CONVERSATION:**
---
{full_conversation}
---

**DAILY INTENT ANALYSIS:**
---
{formatted_daily_analysis}
---

Provide your final analysis as a JSON object only.
"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct", # <-- THE FIX: Using a current, powerful model
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        print(f"✅ LLM analysis generated successfully.")
        return result
    except Exception as e:
        print(f"❌ ERROR in LLM analysis tool: {e}")
        return {
            "summary": "Failed to generate LLM analysis due to an API error.",
            "overall_intent": "Error",
            "next_best_action": "Review the conversation manually and check API keys."
        }

