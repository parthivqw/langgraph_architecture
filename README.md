# LangGraph Multi-Agent Sales & Creative System

This project is a **production-ready, multi-agent AI system** designed to handle complex, multi-step user requests. It demonstrates an advanced, orchestrated workflow built with **LangGraph**, where a central supervisor intelligently routes tasks to a suite of specialized AI agents.

The system is architected as a modern, **decoupled microservice**, with a lightweight **FastAPI backend** for orchestration and specialized AI models deployed as independent, callable endpoints.

---

## 🌟 Key Features & Architecture

- **Advanced Agentic Workflow:** A robust state machine built with LangGraph manages complex flows and conditional transitions between different AI agents.  
- **Intelligent Routing:** The central supervisor (`supervisor.py`) analyzes user intent and dynamically routes tasks to the appropriate agent.  
- **Interactive & Autonomous Modes:** Operates either autonomously or engages the user in multi-step interactive conversations to gather necessary details.  
- **Hybrid AI Strategy:**  
  - **Specialized Fine-Tuned Models:** A custom BERT model for high-accuracy domain-specific intent classification.  
  - **Powerful Generalist LLMs:** Large Language Models (via Groq) for complex reasoning, question generation, and final analysis.  
- **Production-Ready Deployment:** FastAPI backend + Hugging Face hosted BERT model for scalable, microservice architecture.

---

## 🧠 Meet the Agents

### 🕵️ Advanced Sales Agent

Handles **multi-day sales conversation analysis**:

1. **Conversation Splitting:** Parses raw conversation into daily entries.  
2. **Specialized Intent Prediction:** Calls the fine-tuned BERT model to predict day-by-day customer intent (e.g., Information Gathering, Price Concern).  
3. **Synthesized Final Analysis:** Sends the conversation and intent data to a LLM to generate a narrative summary, overall intent, and recommended "next best action."  

### 🎨 Interactive Poster Agent

Handles **dynamic creative tasks**:

1. **Context-Aware Question Generation:** Asks for user's core idea (e.g., "Poster for Python Bootcamp").  
2. **Dynamic UI Generation:** LLM generates follow-up questions and creative multiple-choice options.  
3. **Final Image Creation:** Builds a prompt and calls an image generation API (like Imagen 3) to create the final poster.

---

## 🏗️ System Architecture Diagram

```mermaid
flowchart LR
    A[User Request (/generate)] --> B[FastAPI Backend]
    B --> C[LangGraph Supervisor]
    C --> D[BERT Model on Hugging Face]
    D --> C
    C --> E[LLM on Groq]
    E --> C
    C --> F[Final JSON Response]
    
    %% LangGraph workflow details
    subgraph LangGraph Workflow
        C1[override_intent] --> C2[route_after_intent]
        C2 -->|Interactive| C3[interaction_manager]
        C2 -->|Autonomous| C4[sales_agent_auto / poster_agent_auto]
        C3 --> C5[after_interaction_router]
        C5 --> C4
    end
    B --> C1
🚀 Live Model Endpoint
Fine-tuned BERT model for intent detection:

Sanji8421/fine_tuned_BERT

🛠️ How to Run the Project
1. Prerequisites
Python 3.9+

Hugging Face account

API keys for Hugging Face and Groq

2. Setup
Clone the repository:

bash
Copy code
git clone https://github.com/parthivqw/langgraph-multi-agent.git
cd langgraph-multi-agent
Create and activate a virtual environment:

bash
Copy code
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Set up your .env file:

env
Copy code
HF_TOKEN="hf_YourHuggingFaceToken"
GROQ_API_KEY="gsk_YourGroqApiKey"
# Optional for Poster Agent
IMAGEGEN_API_KEY="your_api_key_here"
3. Running the Application
Start the FastAPI server:

bash
Copy code
uvicorn main:app --reload
4. Interacting with the API
Open Swagger UI:

arduino
Copy code
http://127.0.0.1:8000/docs
Example curl to start a new interactive Sales Agent session:

bash
Copy code
curl -X POST "http://127.0.0.1:8000/generate" \
-H "accept: application/json" \
-H "Content-Type: application/json" \
-d '{
  "service": "sales",
  "mode": "interactive"
}'
Use the returned thread_id to continue the session with the /continue endpoint and provide answers to the follow-up questions.
