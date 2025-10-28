# Smart Policy Recommendation Tool (v2)

This is a **prototype insurance policy recommendation system** built with **Streamlit**.

### Features
- Capture client details (age, income, dependents, coverage, budget).
- Capture **risk factors**: loss ratio, past claims history.
- Save client profiles into a local SQLite database.
- Recommend policies ranked by:
  - Coverage match
  - Affordability
  - Budget fit
  - Risk penalty
- Expandable recommendation details with rationale.

### Running Locally
```bash
git clone https://github.com/YOUR_USERNAME/smart_policy_prototype_v2.git
cd smart_policy_prototype_v2
python -m venv .venv
.venv\Scripts\activate   # (Windows)
pip install -r requirements.txt
streamlit run app.py
