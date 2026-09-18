<<<<<<< HEAD
# Support Ticket AI Assistant

This project is an end-to-end system built to analyze customer support tickets, answer natural language queries using an LLM, and flag operational anomalies.

## Architecture
- Backend: FastAPI providing endpoints for health monitoring, rule-based anomaly detection, and query execution.
- LLM & Data Engine: Pandas for CSV data handling paired with LangChain's dataframe agent and local Llama 3 (via Ollama) to answer user questions.
- Frontend: Streamlit web UI with separate tabs for natural language search and operational audit views.

## Setup Instructions

1. Install required packages:
   pip install -r requirements.txt

2. Make sure Ollama is running in a terminal:
   ollama run llama3

3. Run the FastAPI server:
   uvicorn main:app --reload

4. Run the Streamlit application in another terminal:
   streamlit run app.py

## API Endpoints
- GET /health: System health status and loaded dataset row count.
- GET /api/anomalies: Evaluates dataset for delayed resolutions and stale high-priority tickets.
- POST /api/query: Accepts JSON payload `{"question": "string"}` and returns the generated answer.

## Example Queries
- "How many critical tickets are unresolved?"
- "Which agent has the lowest average customer rating?"
- "What is the average response time for Technical issues?"

## Limitations & Trade-offs
- In-memory data processing with Pandas works well for 500 rows, but large production datasets would require migration to SQL or vector storage.
- Python code execution by the agent runs locally for this prototype; production deployments would require isolated container sandboxing.
=======
# AI_Engineer_Assessment
An AI-powered support ticket assistant and operational anomaly detection system built with FastAPI, Streamlit, and Python.
>>>>>>> 7518fb8e63422673aa7c8171e4f4b19ef4c45e39
