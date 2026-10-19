import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agents import HireWiseOrchestrator, CandidateAnalysisAgent

JOB = {"title":"Data Analyst","required_skills":["python","sql","statistics"],
       "preferred_skills":["pandas","power bi"],"minimum_experience":1}
CANDIDATES = [
 {"candidate_id":"C1","name":"Candidate One","skills":["python","sql","statistics","pandas"],"experience_years":1},
 {"candidate_id":"C2","name":"Candidate Two","skills":["sql"],"experience_years":0.5}
]

def test_score_is_bounded_and_breakdown_exists():
    out = CandidateAnalysisAgent().analyze(CANDIDATES[0], JOB)
    assert 0 <= out["match_score"] <= 100
    assert "matched_required" in out and "missing_required" in out

def test_orchestrator_returns_ranked_candidates_and_validation():
    result = HireWiseOrchestrator().run(JOB, CANDIDATES)
    assert len(result["ranked_candidates"]) == 2
    assert [x["rank"] for x in result["ranked_candidates"]] == [1, 2]
    assert result["validation"]["passed"] is True

def test_ranking_descending():
    result = HireWiseOrchestrator().run(JOB, CANDIDATES)
    scores = [x["match_score"] for x in result["ranked_candidates"]]
    assert scores == sorted(scores, reverse=True)

def test_duplicate_ids_flagged():
    duplicate = [CANDIDATES[0], dict(CANDIDATES[1], candidate_id="C1")]
    result = HireWiseOrchestrator().run(JOB, duplicate)
    assert result["validation"]["passed"] is False
    assert any("Duplicate candidate IDs" in issue for issue in result["validation"]["issues"])

def test_no_required_skills_warned():
    job = dict(JOB, required_skills=[])
    result = HireWiseOrchestrator().run(job, CANDIDATES)
    assert result["validation"]["passed"] is False
    assert any("No required skills" in issue for issue in result["validation"]["issues"])
