# from graph_state import AgentState
# from tools.sales_tools import get_next_best_action_tool

# def run_sales_agent_node(state: AgentState):
#     """
#     This is the Sales Agent. It receives the PREPARED payload and
#     determines the next best action.
#     """
#     print("---AGENT: Sales Agent at Work---")
#     print(f"🔍 DEBUG: Received state keys: {list(state.keys())}")
    
#     try:
#         # Debug: Print the input_payload to see what we're getting
#         input_payload_raw = state.get("input_payload", {})
#         print(f"🔍 DEBUG: Raw input_payload: {input_payload_raw}")
#         print(f"🔍 DEBUG: input_payload type: {type(input_payload_raw)}")
        
#         # Handle the payload structure from prepare_sales_payload_node
#         if isinstance(input_payload_raw, dict):
#             # Check if it's nested or direct
#             if "input_payload" in input_payload_raw:
#                 payload = input_payload_raw["input_payload"]
#                 print("🔍 DEBUG: Using nested payload structure")
#             else:
#                 payload = input_payload_raw
#                 print("🔍 DEBUG: Using direct payload structure")
#         else:
#             print(f"❌ ERROR: input_payload is not a dict: {type(input_payload_raw)}")
#             return {
#                 "final_result": {
#                     "status": "error",
#                     "message": f"Invalid payload type: {type(input_payload_raw)}"
#                 }
#             }
        
#         print(f"🔍 DEBUG: Final payload: {payload}")
        
#         # Extract conversation and predicted_intent
#         conversation = payload.get("conversation")
#         predicted_intent = payload.get("predicted_intent")
        
#         print(f"🔍 DEBUG: conversation exists: {bool(conversation)}")
#         print(f"🔍 DEBUG: predicted_intent: {predicted_intent}")
        
#         if not conversation:
#             print("❌ ERROR: Missing conversation")
#             return {
#                 "final_result": {
#                     "status": "error",
#                     "message": "Sales Agent received no conversation data."
#                 }
#             }
        
#         if not predicted_intent:
#             print("❌ ERROR: Missing predicted_intent")
#             return {
#                 "final_result": {
#                     "status": "error", 
#                     "message": "Sales Agent received no predicted intent."
#                 }
#             }
        
#         print("🔍 DEBUG: Calling get_next_best_action_tool...")
#         next_action = get_next_best_action_tool(conversation, predicted_intent)
#         print(f"🔍 DEBUG: Received next_action: {next_action[:100]}...")
        
#         print("---SUCCESS: Sales Agent Finished Task---")
        
#         # Return data that matches your AgentState field structure exactly
#         result = {
#             # These are the individual fields your AgentState expects
#             "sales_conversation": conversation,
#             "predicted_intent": predicted_intent,
#             "next_best_action": next_action,
#             "sales_analysis": {
#                 "bert_prediction": predicted_intent,
#                 "llm_recommendation": next_action,
#                 "conversation_processed": True
#             },
#             # Also populate the sales_agent field for your FastAPI
#             "sales_agent": {
#                 "final_result": {
#                     "status": "ok",
#                     "agent_type": "sales", 
#                     "predicted_intent": predicted_intent,
#                     "next_best_action": next_action
#                 }
#             }
#         }
        
#         print(f"🔍 DEBUG: Returning result: {result}")
#         print(f"🔍 DEBUG: Result type: {type(result)}")
        
#         return result
        
#     except Exception as e:
#         print(f"---ERROR in Sales Agent: {e}---")
#         import traceback
#         print(f"🔍 DEBUG: Full traceback:\n{traceback.format_exc()}")
        
#         return {
#             "final_result": {
#                 "status": "error",
#                 "message": f"Sales Agent failed: {str(e)}"
#             }
#         }

#=============================================================================================================
from graph_state import AgentState
from tools.sales_tools import (
    split_conversation_by_day,
    predict_sales_intent_tool,
    generate_sales_analysis_tool
)

def run_sales_agent_node(state: AgentState):
    """
    Orchestrates a multi-step sales analysis:
    1. Splits the conversation by day.
    2. Predicts intent for each day using a fine-tuned BERT model.
    3. Synthesizes the findings with an LLM for a final, rich analysis.
    """
    print("\n---AGENT: 🕵️ Advanced Sales Agent at Work 🕵️---\n")

    try:
        # Step 0: Get the full conversation from the interaction manager's output
        interaction_data = state.get("interaction", {})
        collected_data = interaction_data.get("collected_content", {})
        full_conversation = collected_data.get("conversation")

        if not full_conversation:
            raise ValueError("Sales Agent received no conversation data from the interaction manager.")

        # --- ORCHESTRATION PIPELINE ---

        # Step 1: Split the conversation into daily chunks
        daily_chunks = split_conversation_by_day(full_conversation)
        if not daily_chunks:
            raise ValueError("Failed to split conversation into daily chunks.")

        # Step 2: Analyze each day's intent with the BERT model
        daily_intent_analysis = []
        for chunk in daily_chunks:
            intent = predict_sales_intent_tool(chunk["content"])
            daily_intent_analysis.append({
                "day": chunk["day_marker"],
                "intent": intent,
                "text_preview": chunk["content"][:100] + "..."
            })
        print("\n📊 Daily Intent Analysis Complete:")
        for item in daily_intent_analysis:
            print(f"  - {item['day']} Intent: {item['intent']}")
        print("\n")


        # Step 3: Call the powerful LLM tool to synthesize everything
        final_analysis = generate_sales_analysis_tool(full_conversation, daily_intent_analysis)

        print("---SUCCESS: Advanced Sales Agent Finished Task---")

        # Step 4: Format the final, rich output for the AgentState
        return {
            "sales_conversation": full_conversation,
            "predicted_intent": final_analysis.get("overall_intent", "N/A"),
            "next_best_action": final_analysis.get("next_best_action", "N/A"),
            "sales_analysis_report": { # A new, structured field for the final report
                "summary": final_analysis.get("summary"),
                "daily_breakdown": daily_intent_analysis
            }
        }

    except Exception as e:
        print(f"---ERROR in Advanced Sales Agent: {e}---")
        import traceback
        traceback.print_exc()
        return {
            "errors": [f"Sales Agent failed: {str(e)}"]
        }