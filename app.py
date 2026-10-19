import json
from pathlib import Path
import pandas as pd
import streamlit as st
from agents import HireWiseOrchestrator

st.set_page_config(page_title="HireWise AI", page_icon="🧭", layout="wide")
st.title("🧭 HireWise AI")
st.caption("Explainable, multi-agent recruitment decision-support PoC")
st.warning("Demo only: scores support human review; they must not be used as the sole basis for hiring. Use job-relevant criteria and review all candidates fairly.")

DATA_PATH = Path(__file__).parent / "data" / "synthetic_candidates.json"

@st.cache_data
def load_candidates():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

defaults = load_candidates()
with st.sidebar:
    st.header("Job requirements")
    job_title = st.text_input("Job title", "Junior Data Analyst")
    req_text = st.text_input("Required skills (comma-separated)", "python, sql, statistics")
    pref_text = st.text_input("Preferred skills (comma-separated)", "power bi, pandas, excel")
    min_exp = st.number_input("Minimum experience (years)", min_value=0.0, max_value=30.0, value=1.0, step=0.5)
    shortlist_size = st.slider("Shortlist size", min_value=1, max_value=10, value=3)
    run_button = st.button("Run agent workflow", type="primary", use_container_width=True)

st.subheader("1. Candidate data")
st.write("The PoC uses fictional profiles. You can inspect them below; no real resumes are needed.")
candidate_df = pd.DataFrame([{
    "Candidate ID": c["candidate_id"], "Name": c["name"],
    "Skills": ", ".join(c["skills"]), "Experience (years)": c["experience_years"]
} for c in defaults])
st.dataframe(candidate_df, use_container_width=True, hide_index=True)

if run_button or "result" not in st.session_state:
    required = [x.strip().lower() for x in req_text.split(",") if x.strip()]
    preferred = [x.strip().lower() for x in pref_text.split(",") if x.strip()]
    job = {"title": job_title, "required_skills": required,
           "preferred_skills": preferred, "minimum_experience": min_exp}
    orchestrator = HireWiseOrchestrator()
    st.session_state["result"] = orchestrator.run(job, defaults)
    st.session_state["job"] = job

result = st.session_state["result"]
ranked = result["ranked_candidates"]
validation = result["validation"]

st.subheader("2. Agent execution trace")
events_df = pd.DataFrame(result["events"])
st.dataframe(events_df, use_container_width=True, hide_index=True)
with st.expander("View Planner Agent task plan"):
    for i, task in enumerate(result["plan"]["tasks"], 1):
        st.write(f"{i}. {task}")

st.subheader("3. Results")
c1, c2, c3 = st.columns(3)
c1.metric("Candidates analyzed", len(ranked))
c2.metric("Average match score", f"{sum(x['match_score'] for x in ranked)/len(ranked):.1f}%" if ranked else "—")
c3.metric("Validation", "PASSED" if validation["passed"] else "REVIEW REQUIRED")

if validation["issues"]:
    for issue in validation["issues"]:
        st.error(issue)
else:
    st.success("Critic Agent checks passed: scores are in range, IDs and ranks are consistent, and required-skill accounting is coherent.")

if ranked:
    display = pd.DataFrame([{
        "Rank": x["rank"], "Candidate": x["name"], "ID": x["candidate_id"],
        "Match score": x["match_score"], "Required skill fit": x["required_skill_fit"],
        "Preferred skill fit": x["preferred_skill_fit"], "Experience fit": x["experience_fit"],
        "Missing required skills": ", ".join(x["missing_required"]) or "None"
    } for x in ranked])
    st.dataframe(display, use_container_width=True, hide_index=True)
    st.bar_chart(display.set_index("Candidate")["Match score"])

    st.subheader("4. Explain an individual match")
    options = {f"{x['rank']}. {x['name']} ({x['candidate_id']})": x for x in ranked}
    chosen_label = st.selectbox("Choose candidate", list(options.keys()))
    chosen = options[chosen_label]
    a, b = st.columns(2)
    with a:
        st.metric("Overall score", f"{chosen['match_score']:.2f}%")
        st.write("**Matched required skills**")
        st.write(", ".join(chosen["matched_required"]) or "None")
        st.write("**Missing required skills**")
        st.write(", ".join(chosen["missing_required"]) or "None")
    with b:
        st.write("**Matched preferred skills**")
        st.write(", ".join(chosen["matched_preferred"]) or "None")
        st.write("**Scoring formula**")
        st.code("Score = 0.60 × required-skill fit\n      + 0.20 × preferred-skill fit\n      + 0.20 × experience fit")
        st.caption("Each component is capped at 100%. Weights are illustrative and editable in source code.")

    st.subheader("5. Recruiter-reviewed shortlist")
    st.caption("The system suggests candidates by rank; the recruiter makes the final decision.")
    shortlist = ranked[:shortlist_size]
    selected_ids = []
    cols = st.columns(min(3, len(shortlist)))
    for i, x in enumerate(shortlist):
        with cols[i % len(cols)]:
            if st.checkbox(f"{x['name']} — {x['match_score']:.1f}%", value=True, key=f"short_{x['candidate_id']}"):
                selected_ids.append(x["candidate_id"])
    shortlist_rows = [x for x in ranked if x["candidate_id"] in selected_ids]
    export = pd.DataFrame([{
        "candidate_id": x["candidate_id"], "name": x["name"],
        "match_score": x["match_score"], "matched_required": "; ".join(x["matched_required"]),
        "missing_required": "; ".join(x["missing_required"]), "rank": x["rank"]
    } for x in shortlist_rows])
    st.download_button("Download reviewed shortlist CSV", export.to_csv(index=False).encode("utf-8"),
                       file_name="hirewise_reviewed_shortlist.csv", mime="text/csv")
    st.download_button("Download full analysis JSON", json.dumps(result, indent=2).encode("utf-8"),
                       file_name="hirewise_analysis.json", mime="application/json")

with st.expander("Limitations, fairness, and responsible use"):
    st.markdown("""
    - Synthetic data only; results do not establish real-world hiring performance.
    - The scoring rubric is a transparent demonstration, not a validated employment assessment.
    - Keyword matching may miss synonyms, context, transferable skills, and quality of experience.
    - Profiles are not assessed using protected attributes; real deployment would require legal, privacy, security, and bias evaluation.
    - Human reviewers should verify evidence, consider reasonable accommodations, and not treat score or rank as a hiring decision.
    - Critic checks validate software consistency, not whether the rubric itself is fair or job-valid.
    """)
