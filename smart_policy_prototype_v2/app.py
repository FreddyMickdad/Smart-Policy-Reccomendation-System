
import streamlit as st
import pandas as pd
from database import init_db, fetch_policies, save_client, DB_FILE
from recommendation import recommend_policies

# Initialize DB
init_db(DB_FILE)

st.set_page_config(page_title="Smart Policy Recommendation Tool (v2)", layout="centered")
st.title("Smart Policy Recommendation Tool — Risk-aware Prototype \U0001F4CB")
st.markdown("Enter client details (including risk data) to get risk-adjusted policy recommendations.")

with st.form("client_form"):
    st.subheader("Client details")
    name = st.text_input("Client name (optional)", value="")
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    income = st.number_input("Monthly income (KES)", min_value=0, value=30000)
    dependents = st.number_input("Number of dependents", min_value=0, value=0)
    coverage = st.multiselect("Desired coverage (choose one or more)", options=["medical","life","motor","education","accident"], default=["medical"])
    budget = st.number_input("Preferred max premium (KES, optional)", min_value=0, value=0)
    loss_ratio = st.number_input("Client loss ratio (e.g. 0.7 = low risk, 1.2 = high risk)", min_value=0.0, value=1.0)
    claims_history = st.text_area("Past claims history (e.g., motor:2, medical:1) — keep it short", value="")
    submitted = st.form_submit_button("Get Recommendations and Save Client")

if submitted:
    client = {
        "name": name if name else None,
        "age": int(age),
        "income": float(income),
        "dependents": int(dependents),
        "coverage": ",".join(coverage),
        "budget": float(budget) if budget>0 else None,
        "loss_ratio": float(loss_ratio),
        "claims_history": claims_history
    }
    cid = save_client(client, DB_FILE)
    st.success(f"Client saved with id: {cid}")
    policies = fetch_policies(DB_FILE)
    results = recommend_policies(client, policies, top_n=10)
    st.subheader(f"Top {len(results)} Recommendations")
    if len(results) == 0:
        st.info("No matching policies found. Try widening coverage choices or removing budget limit.")
    else:
        df = pd.DataFrame([{
            'name': r['name'],
            'coverage_type': r['coverage_type'],
            'premium_min': r['premium_min'],
            'premium_max': r['premium_max'],
            'score': r['score'],
            'risk_penalty': r['risk_penalty']
        }  for r in results])
        st.dataframe(df)
        for r in results:
            with st.expander(f"{r['name']} — score: {r['score']}"):
                st.write(r['description'])
                st.write(f"**Coverage:** {r['coverage_type']}")
                st.write(f"**Eligibility:** {r['eligibility']}")
                st.write(f"**Premium range (KES):** {r['premium_min']} - {r['premium_max']}")
                st.write(f"**Risk penalty:** {r['risk_penalty']} (lower is better)" )
                st.write(f"**Why recommended:** coverage match={r['coverage_match']}, affordability={r['affordability']}, budget_bonus={r['budget_bonus']}")
