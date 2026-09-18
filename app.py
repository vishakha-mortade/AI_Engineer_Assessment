import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Support Ticket AI Assistant", layout="wide")
st.title("🎫 Support Ticket AI Assistant")

tab1, tab2 = st.tabs(["Query Assistant", "Operational Anomalies"])

with tab1:
    st.header("Ask Questions About Support Tickets")
    user_query = st.text_input("Enter your question:", placeholder="e.g., How many tickets are high priority?")
    
    if st.button("Submit Query"):
        if user_query.strip():
            with st.spinner("Processing query via local LLM..."):
                try:
                    res = requests.post(f"{API_URL}/api/query", json={"question": user_query})
                    if res.status_code == 200:
                        st.success("Answer:")
                        st.write(res.json().get("answer"))
                    else:
                        st.error(f"Server Error ({res.status_code}): {res.text}")
                except Exception as e:
                    st.error(f"Failed to reach backend API: {e}")

with tab2:
    st.header("System & Operational Anomalies")
    if st.button("Run Audit"):
        with st.spinner("Auditing ticket records..."):
            try:
                res = requests.get(f"{API_URL}/api/anomalies")
                if res.status_code == 200:
                    data = res.json()
                    st.metric("Total Flagged Anomalies", data.get("total_anomalies_found", 0))
                    st.dataframe(data.get("anomalies", []), use_container_width=True)
                else:
                    st.error(f"Server Error ({res.status_code}): {res.text}")
            except Exception as e:
                st.error(f"Failed to reach backend API: {e}")