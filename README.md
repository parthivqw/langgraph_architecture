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
