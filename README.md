# LangGraph Multi-Agent Sales & Creative System

This project is a production-ready, multi-agent AI system designed to handle complex, multi-step user requests. It demonstrates an advanced, orchestrated workflow built with **LangGraph**, where a central supervisor intelligently routes tasks to a suite of specialized AI agents.

The system is architected as a modern, decoupled microservice, with a lightweight **FastAPI backend** for orchestration and specialized AI models deployed as independent, callable endpoints.

---

## 🌟 Key Features & Architecture

- **Advanced Agentic Workflow:** A robust state machine built with LangGraph manages the complex flow of information and conditional transitions between AI agents.  
- **Intelligent Routing:** A central supervisor (`supervisor.py`) analyzes user intent and dynamically routes tasks to the appropriate agent.  
- **Interactive & Autonomous Modes:** Operates in a fully autonomous mode or engages the user in a multi-step interactive conversation to gather necessary details.  
- **Hybrid AI Strategy:**  
  - **Specialized Fine-Tuned Models:** A custom fine-tuned **BERT** model provides high-accuracy, domain-specific intent classification.  
  - **Powerful Generalist LLMs:** Large Language Models (via **Groq**) are used for complex reasoning, dynamic question generation, and final analysis.  
- **Production-Ready Deployment:** FastAPI service as the core app; heavy BERT model hosted on Hugging Face for a scalable microservice architecture.

---

## 🧠 Meet the Agents

### 🕵️ Advanced Sales Agent
- **Conversation Splitting:** Parses raw conversation text into daily entries.  
- **Specialized Intent Prediction:** Uses fine-tuned BERT to predict customer intent (e.g., Information Gathering, Price Concern).  
- **Synthesized Final Analysis:** Sends conversation + daily intent to an LLM, which produces a narrative summary, overall intent, and recommended "next best action."  

### 🎨 Interactive Poster Agent
- **Context-Aware Question Generation:** Generates dynamic, relevant follow-up questions based on the user's core idea.  
- **Dynamic UI Generation:** LLM acts as a UI/UX designer, providing creative, context-aware options.  
- **Final Image Creation:** Calls a dedicated image-generation API (like Imagen 3) to create the final poster.

---

## 🏗️ System Architecture Diagram

```mermaid
flowchart LR
    A["User Request /generate"] --> B["FastAPI Backend"]
    B --> C["LangGraph Supervisor"]
    C --> D["BERT Model on Hugging Face"]
    D --> C
    C --> E["LLM on Groq"]
    E --> C
    C --> F["Final JSON Response"]
    
    subgraph "LangGraph Workflow"
        C1["override_intent"] --> C2["route_after_intent"]
        C2 -->|Interactive| C3["interaction_manager"]
        C2 -->|Autonomous| C4["sales_agent_auto / poster_agent_auto"]
        C3 --> C5["after_interaction_router"]
        C5 --> C4
    end
    B --> C1
🚀 Live Model Endpoint
The fine-tuned BERT model for intent detection is live and can be viewed on Hugging Face:

Sanji8421/fine_tuned_BERT

🛠️ How to Run the Project
1. Prerequisites
Python 3.9+

Hugging Face account

API keys for Hugging Face and Groq

2. Setup
bash
Copy code
git clone https://github.com/parthivqw/langgraph-multi-agent.git
cd langgraph-multi-agent

python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
Create a .env file in the root of the project:

env
Copy code
HF_TOKEN="hf_YourHuggingFaceToken"
GROQ_API_KEY="gsk_YourGroqApiKey"
# Optional for Poster Agent
IMAGEGEN_API_KEY="your_api_key_here"
3. Run the Application
bash
Copy code
uvicorn main:app --reload
4. Interacting with the API
Navigate to http://127.0.0.1:8000/docs for interactive Swagger UI.

Example curl command (start a new interactive Sales Agent session):

bash
Copy code
curl -X 'POST' \
  'http://127.0.0.1:8000/generate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "service": "sales",
  "mode": "interactive"
}'
Use the returned thread_id to continue the conversation via /continue.
