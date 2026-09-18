from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_community.llms import Ollama

app = FastAPI(
    title="Support Ticket AI Assistant",
    description="REST API for querying support ticket data and flagging operational anomalies.",
    version="1.0.0"
)

# Load support tickets dataset into memory
DATA_PATH = "support_tickets.csv"

try:
    df = pd.read_csv(DATA_PATH)
    # Parse created_at as datetime for temporal calculations
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
except Exception as e:
    df = pd.DataFrame()

# Request schemas
class QueryRequest(BaseModel):
    question: str

# Initialize local LLM agent
def get_pandas_agent():
    if df.empty:
        raise HTTPException(status_code=500, detail="Dataframe is empty or not loaded.")
    
    # Using local Ollama with llama3 model
    llm = Ollama(model="llama3", temperature=0)
    
    return create_pandas_dataframe_agent(
        llm,
        df,
        verbose=False,
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )

@app.get("/health")
async def health_check():
    """Endpoint 1: Health Check & System Status"""
    if df.empty:
        raise HTTPException(status_code=503, detail="Dataset unavailable.")
    return {"status": "healthy", "total_records": len(df)}

@app.post("/api/query")
async def process_query(request: QueryRequest):
    """Endpoint 2: Natural Language Query Handler"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question string cannot be empty.")
    
    try:
        agent = get_pandas_agent()
        response = agent.invoke(request.question)
        output_text = response.get("output", "No answer generated.")
        return {"question": request.question, "answer": output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM processing error: {str(e)}")

@app.get("/api/anomalies")
async def detect_anomalies():
    """Endpoint 3: Rule-Based & Statistical Anomaly Detection Engine"""
    if df.empty:
        raise HTTPException(status_code=503, detail="Dataset unavailable.")
    
    anomalies = []

    # Rule 1: High/Critical priority tickets still open > 24 hours
    now = pd.Timestamp.now()
    open_high_priority = df[
        (df["status"].isin(["Open", "Escalated"])) & 
        (df["priority"].isin(["High", "Critical"]))
    ].copy()

    if not open_high_priority.empty:
        for _, row in open_high_priority.iterrows():
            anomalies.append({
                "ticket_id": str(row["ticket_id"]),
                "anomaly_type": "Stale High-Priority Ticket",
                "severity": "High",
                "details": f"Priority '{row['priority']}' ticket status is '{row['status']}'."
            })

    # Rule 2: Resolution time statistical outliers (Z-score > 3)
    resolved_df = df[df["resol_time_hrs"].notna()].copy()
    if not resolved_df.empty:
        mean_res = resolved_df["resol_time_hrs"].mean()
        std_res = resolved_df["resol_time_hrs"].std()
        
        if std_res > 0:
            outliers = resolved_df[resolved_df["resol_time_hrs"] > (mean_res + 3 * std_res)]
            for _, row in outliers.iterrows():
                anomalies.append({
                    "ticket_id": str(row["ticket_id"]),
                    "anomaly_type": "Abnormally Long Resolution Time",
                    "severity": "Medium",
                    "details": f"Resolution took {row['resol_time_hrs']} hrs (Mean: {round(mean_res, 1)} hrs)."
                })

    return {
        "total_anomalies_found": len(anomalies),
        "anomalies": anomalies
    }