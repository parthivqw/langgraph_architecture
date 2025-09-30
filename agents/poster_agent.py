# import json
# from graph_state import AgentState

# # The Agent imports the tools it needs from its toolbox.
# from tools.poster_tools import (
#     call_llama_generate_fields,
#     build_image_generation_prompt,
#     generate_poster_image,
#     enhance_interactive_content
# )

# # Helper class to convert dict to object
# class DictToObject:
#     def __init__(self, **entries):
#         self.__dict__.update(entries)

# # THIS IS THE POSTER AGENT NODE. ITS HOME IS HERE.
# def run_poster_agent_node(state: AgentState):
#     print("---AGENT: Poster Agent at Work---")
#     try:
#         # Get payload from input_payload
#         payload = state.get("input_payload", {})
        
#         # Handle both nested and direct payload structures  
#         if "input_payload" in payload:
#             actual_payload = payload["input_payload"]
#         else:
#             actual_payload = payload
            
#         if not actual_payload:
#             return {
#                 "poster_agent": {
#                     "status": "error",
#                     "errors": ["Poster Agent received no payload."]
#                 }
#             }

#         payload_obj = DictToObject(**actual_payload)

#         # The agent now uses its tools in sequence.
#         raw_text_fields = call_llama_generate_fields(payload_obj)
#         poster_fields = json.loads(raw_text_fields)
        
#         final_prompt = build_image_generation_prompt(poster_fields)
        
#         image_b64 = generate_poster_image(final_prompt)

#         print("---SUCCESS: Poster Agent Finished Task---")
        
#         # Return comprehensive results in the new state structure
#         return {
#             "poster_agent": {
#                 "status": "success",
#                 "poster_fields": poster_fields,
#                 "image_prompt": final_prompt,
#                 "final_image": image_b64
#             },
#             # Also populate individual fields for easier access
#             "poster_fields": poster_fields,
#             "image_prompt": final_prompt,
#             "final_image": image_b64,
#             "current_agent": "poster",
#             "workflow_type": "poster"
#         }
        
#     except Exception as e:
#         print(f"---ERROR in Poster Agent: {e}---")
#         return {
#             "poster_agent": {
#                 "status": "error",
#                 "errors": [f"Poster Agent failed: {str(e)}"]
#             },
#             "errors": [f"Poster Agent failed: {str(e)}"],
#             "current_agent": "poster", 
#             "workflow_type": "poster"
#         }
# #---NEW "LITE" AGENT FOR INTERACTIVE FLOW---
# def run_interactive_poster_flow_node(state: AgentState):
#     """
#     This "lite" agent takes the user-confirmed data from the interactive session,
#     enhances it, builds the final image prompt, and generates the image.
#     """
#     print("---AGENT:Poster Agent (Interactive Flow) at work---")
#     try:
#         #We get the final payload directly from the interaction state
#         #Which is where the entire interactive conversation has been built.
#         interaction_data=state.get('interaction',{})
#         collected_content=interaction_data.get("collected_content",{})
#         initial_prompt=state.get("intent_data",{}).get("raw_prompt","a poster")

#         if not collected_content:
#             raise ValueError("No content was collected from the user.")
        
#         # Step 1:"Buff up" the user's raw content with our new tool
#         enhanced_content_str=enhance_interactive_content(collected_content,initial_prompt)
#         ehnanced_fields=json.loads(enhanced_content_str)

#         #Step 2:RE_USE your exisitng, powerful prompt builder tool
#         print("Using enhanced content to build the final prompt...")
#         final_prompt=build_image_generation_prompt(ehnanced_fields)

#         # Step 3:RE_USE your existing image generation tool
#         image_b64=generate_poster_image(final_prompt)

#         print("---SUCCESS:Interactive Poster Flow Finished---")

#         return{
#             "final_image":image_b64,
#             "image_prompt":final_prompt,
#             "poster_fields":ehnanced_fields, #Store the buffed up content for the UI
#             "final_result":{"status":"success","image":image_b64}
#         }
#     except Exception as e:
#         print(f"---ERROR in Interactive Poster Flow:{e}---")
#         return { "errors":[f"Interactive Poster Flow failed:{str(e)}"]}


#+====================================================================================================
import json
from graph_state import AgentState
from tools.poster_tools import build_image_prompt_tool, generate_image_from_prompt_tool

def run_interactive_poster_flow_node(state: AgentState):
    """
    The Poster Agent for the interactive workflow.
    1. Takes the final collected content from the interaction manager.
    2. Builds the detailed, structured prompt for the image model.
    3. Calls the image generation API to get the final poster.
    """
    print("\n---AGENT: 🎨 Poster Agent (Interactive) at Work 🎨---\n")

    try:
        # Step 0: Get the complete brief from the interaction manager
        interaction_data = state.get("interaction", {})
        collected_data = interaction_data.get("collected_content", {})

        if not collected_data:
            raise ValueError("Poster Agent received no content from the interaction manager.")

        # --- The Two-Step Pipeline ---

        # Step 1: Build the final mega-prompt using the artist's tool
        final_image_prompt = build_image_prompt_tool(collected_data)

        # Step 2: Generate the image using the artist's tool
        final_image_base64 = generate_image_from_prompt_tool(final_image_prompt)

        print("---SUCCESS: Interactive Poster Flow Finished---")
        
        # Return all the necessary data to update the state
        return {
            "final_image": final_image_base64,
            "image_prompt": final_image_prompt,
            "poster_fields": collected_data, # Store the user's final choices
        }

    except Exception as e:
        print(f"---ERROR in Interactive Poster Flow: {e}---")
        return {"errors": [f"Interactive Poster Flow failed: {str(e)}"]}

# To keep the supervisor clean, we can have the autonomous node point here for now.
run_poster_agent_node = run_interactive_poster_flow_node

