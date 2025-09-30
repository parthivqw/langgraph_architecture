# LangGraph Multi-Agent Sales & Creative System

This project is a **production-ready, multi-agent AI system** designed to handle complex, multi-step user requests. It demonstrates an advanced, orchestrated workflow built with **LangGraph**, where a central supervisor intelligently routes tasks to a suite of specialized AI agents.

The system is architected as a **decoupled microservice**, with a lightweight **FastAPI backend** and specialized AI models deployed as independent endpoints.

---

## 🌟 Key Features & Architecture

- **Advanced Agentic Workflow:** Robust state machine built with LangGraph manages complex flows and conditional transitions between agents.  
- **Intelligent Routing:** Central supervisor (`supervisor.py`) analyzes user intent and routes tasks dynamically.  
- **Interactive & Autonomous Modes:** Can run fully autonomously or engage users in multi-step conversations.  
- **Hybrid AI Strategy:**
  - **Specialized Fine-Tuned Models:** BERT model for high-accuracy, domain-specific intent classification.  
  - **Powerful Generalist LLMs:** LLMs (via Groq) handle reasoning, dynamic question generation, and final analysis.  
- **Production-Ready Deployment:** FastAPI service handles orchestration; heavy BERT model hosted on Hugging Face.

---

## 🧠 Meet the Agents

### 🕵️ Advanced Sales Agent
- Parses raw multi-day sales conversations into daily entries.  
- Calls **fine-tuned BERT** for intent prediction per day.  
- Synthesizes results with an LLM, providing narrative summary and recommended "next best action".

### 🎨 Interactive Poster Agent
- Engages users to gather creative task information.  
- Uses context-aware LLMs to generate follow-up questions dynamically.  
- Builds prompts and calls **Imagen 3 API** to generate final poster images.

---

## 🏗️ System Architecture & Workflow

```mermaid
flowchart TD
    A["User Request<br/>/generate or /continue"] --> B["FastAPI Backend<br/>main.py"]
    
    B --> C["LangGraph Supervisor<br/>supervisor.py"]
    
    subgraph "LangGraph Workflow"
        C --> C1["override_intent_node<br/>Loads app_registry.json"]
        C1 --> C2["route_after_intent<br/>Router"]
        
        C2 -->|execution_mode == 'interactive'| C3["interaction_manager_node<br/>Asks questions one-by-one"]
        C2 -->|execution_mode == 'autonomous'<br/>service == 'poster'| C4A["poster_agent_auto"]
        C2 -->|execution_mode == 'autonomous'<br/>service == 'sales'| C4B["sales_agent_auto"]
        
        C3 -->|Collects user_answers| C5["after_interaction_router"]
        
        C5 -->|interaction_is_required == true| C3
        C5 -->|Complete + Poster| C6["poster_agent_interactive<br/>run_interactive_poster_flow_node"]
        C5 -->|Complete + Sales| C4B
        
        C6 --> END1["END"]
        C4A --> END1
        C4B --> END1
    end
    
    subgraph "Poster Agent Tools"
        P1["build_image_prompt_tool<br/>Uses POSTER_PROMPT_SKELETON"]
        P2["generate_image_from_prompt_tool<br/>Calls Imagen 3 API"]
        C6 -.-> P1
        P1 -.-> P2
    end
    
    subgraph "Sales Agent Tools"
        S1["split_conversation_by_day"]
        S2["predict_sales_intent_tool<br/>Fine-tuned BERT Model"]
        S3["generate_sales_analysis_tool<br/>LLM Synthesis"]
        C4B -.-> S1
        S1 -.-> S2
        S2 -.-> S3
    end
    
    subgraph "Interaction Manager Tools"
        I1["generate_questions_from_skeleton<br/>Context-aware Q&A"]
        I2["generate_clarifying_sales_questions"]
        C3 -.-> I1
        C3 -.-> I2
    end
    
    D["Hugging Face<br/>BERT Model"] -.->|Used by| S2
    E["Groq LLM<br/>meta-llama/llama-4"] -.->|Used by| S3
    E -.->|Used by| I1
    F["a4f.co API<br/>Imagen 3"] -.->|Used by| P2
    
    END1 --> G["Final JSON Response<br/>via format_final_response"]
    G --> B
🚀 Live Model Endpoint
Fine-tuned BERT for intent detection: Sanji8421/fine_tuned_BERT

🛠️ How to Run the Project
1. Prerequisites
Python 3.9+

Hugging Face account and API key

Groq API key

(Optional) Image generation API key for Poster Agent

2. Setup
bash
Copy code
git clone https://github.com/parthivqw/langgraph-multi-agent.git
cd langgraph-multi-agent
python -m venv venv
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
pip install -r requirements.txt
Set up .env file in project root:

env
Copy code
HF_TOKEN="hf_YourHuggingFaceToken"
GROQ_API_KEY="gsk_YourGroqApiKey"
IMAGEGEN_API_KEY="your_api_key_here"
3. Running the Application
bash
Copy code
uvicorn main:app --reload
4. Interacting with the API
API docs: http://127.0.0.1:8000/docs

Start a new session (Sales Agent Interactive Mode):

bash
Copy code
curl -X POST \
  http://127.0.0.1:8000/generate \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
  "service": "sales",
  "mode": "interactive"
}'
Use /continue endpoint with thread_id to provide answers to follow-up questions.
