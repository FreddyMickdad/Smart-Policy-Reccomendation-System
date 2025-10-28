
# Smart Policy Recommendation Tool — Risk-aware Prototype (v2)

This upgraded prototype includes client risk data (loss ratio, claims history), a client logging table, and a risk-aware recommendation engine.

## Files
- `database.py` — initializes `policies_v2.db`, creates `policies` & `clients` tables, seeds sample policies, and provides `fetch_policies()` and `save_client()`.
- `recommendation.py` — risk-aware recommendation logic (coverage, affordability, budget bonus, risk penalty).
- `app.py` — Streamlit front-end (accepts risk fields and saves client records).
- `requirements.txt` — dependencies to install in the virtual environment.
- `policies_v2.db` — created when initializing the DB (included in zip).

## Quick start (local)
1. Activate your virtual environment:
   ```bash
   .venv\\Scripts\\activate.bat   # Windows CMD
   # or for PowerShell: .\\.venv\\Scripts\\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. Open http://localhost:8501

## Next recommendations
- Add more realistic policy entries and a richer claims data model.
- Tune risk_penalty weights to match agency risk policy.
- Add role-based authentication for agents and audit trails.
