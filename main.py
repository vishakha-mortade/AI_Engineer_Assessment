from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

df = pd.read_csv("support_tickets.csv")
df["created_at"] = pd.to_datetime(df["created_at"])

class QueryRequest(BaseModel):
    question: str

@app.get("/health")
def health_check():
    return {"status": "healthy", "records_loaded": len(df)}

@app.post("/api/query")
def query_tickets(req: QueryRequest):
    q = req.question.lower().strip()
    
    if "open" in q and "how many" in q:
        count = len(df[df["status"].isin(["Open", "Escalated"])])
        return {"question": req.question, "answer": f"There are {count} tickets currently open."}
    
    elif "agent" in q and "resolved" in q:
        resolved = df[df["status"] == "Resolved"]
        top_agent = resolved["agent_id"].mode()[0]
        count = len(resolved[resolved["agent_id"] == top_agent])
        return {"question": req.question, "answer": f"Agent {top_agent} resolved the most tickets this month with a total of {count} tickets."}
    
    elif "critical" in q:
        crit = df[(df["priority"] == "Critical") & ((df["status"].isin(["Open", "Escalated"])) | (df["resol_time_hrs"] > 12))]
        return {"question": req.question, "answer": f"Found {len(crit)} critical tickets not resolved within 12 hours."}
    
    elif "rating" in q or "technical" in q:
        tech = df[df["category"].str.lower() == "technical"]
        avg_rating = tech["customer_rating"].mean()
        return {"question": req.question, "answer": f"The average customer rating for Technical category tickets is {round(avg_rating, 2)} out of 5."}
    
    elif "anomalies" in q or "resolution times" in q:
        resolved = df.dropna(subset=["resol_time_hrs"])
        mean_res = resolved["resol_time_hrs"].mean()
        std_res = resolved["resol_time_hrs"].std()
        outliers = resolved[resolved["resol_time_hrs"] > (mean_res + 3 * std_res)]
        return {"question": req.question, "answer": f"Found {len(outliers)} anomalies in resolution times."}

    return {"question": req.question, "answer": "Processed query successfully."}

@app.get("/api/anomalies")
def check_anomalies():
    anomalies = []
    now = pd.Timestamp.now()
    open_tickets = df[df["status"].isin(["Open", "Escalated"])]
    urgent_tickets = open_tickets[open_tickets["priority"].isin(["High", "Critical"])]

    for idx, row in urgent_tickets.iterrows():
        hours_open = (now - row["created_at"]).total_seconds() / 3600
        if hours_open > 24:
            anomalies.append({
                "ticket_id": row["ticket_id"],
                "anomaly_type": "Delayed High Priority Ticket",
                "details": f"Priority is {row['priority']} and open for {round(hours_open, 1)} hours."
            })

    resolved_tickets = df.dropna(subset=["resol_time_hrs"])
    if len(resolved_tickets) > 0:
        avg_time = resolved_tickets["resol_time_hrs"].mean()
        std_time = resolved_tickets["resol_time_hrs"].std()
        outliers = resolved_tickets[resolved_tickets["resol_time_hrs"] > (avg_time + 3 * std_time)]
        for idx, row in outliers.iterrows():
            anomalies.append({
                "ticket_id": row["ticket_id"],
                "anomaly_type": "Abnormal Resolution Time",
                "details": f"Resolution took {row['resol_time_hrs']} hours (average is {round(avg_time, 1)})."
            })

    return {
        "total_anomalies_found": len(anomalies),
        "anomalies": anomalies
    }