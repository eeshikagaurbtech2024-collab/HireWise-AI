"""
HireWise AI: transparent, deterministic multi-agent recruitment PoC.
These are software agents with distinct responsibilities, not LLMs.
"""
from dataclasses import dataclass, asdict
from typing import Any
import re

@dataclass
class AgentEvent:
    agent: str
    action: str
    status: str
    details: str

class PlannerAgent:
    name = "Planner Agent"
    def plan(self, job: dict, candidates: list[dict]) -> dict:
        tasks = [
            "Validate job requirements and candidate records",
            "Extract candidate skills and experience",
            "Calculate explainable job-match scores",
            "Rank candidates using the configured scoring rubric",
            "Validate calculations and flag missing information",
            "Prepare a recruiter-reviewed shortlist"
        ]
        return {"tasks": tasks, "candidate_count": len(candidates),
                "required_skills": job.get("required_skills", [])}

class CandidateAnalysisAgent:
    name = "Candidate Analysis Agent"
    def analyze(self, candidate: dict, job: dict) -> dict:
        candidate_skills = {str(s).strip().lower() for s in candidate.get("skills", []) if str(s).strip()}
        required = {str(s).strip().lower() for s in job.get("required_skills", []) if str(s).strip()}
        preferred = {str(s).strip().lower() for s in job.get("preferred_skills", []) if str(s).strip()}
        matched_required = sorted(required & candidate_skills)
        missing_required = sorted(required - candidate_skills)
        matched_preferred = sorted(preferred & candidate_skills)
        exp = candidate.get("experience_years", 0)
        try:
            exp = max(0.0, float(exp))
        except (TypeError, ValueError):
            exp = 0.0
        min_exp = max(0.0, float(job.get("minimum_experience", 0) or 0))
        # Experience fit is capped at 100%; no bonus for excessive experience.
        exp_fit = 100.0 if min_exp == 0 else min(100.0, exp / min_exp * 100.0)
        # Transparent rubric: required skills 60%, preferred skills 20%, experience 20%.
        req_fit = 100.0 if not required else len(matched_required) / len(required) * 100.0
        pref_fit = 100.0 if not preferred else len(matched_preferred) / len(preferred) * 100.0
        score = round(0.60 * req_fit + 0.20 * pref_fit + 0.20 * exp_fit, 2)
        return {
            "candidate_id": candidate.get("candidate_id", "UNKNOWN"),
            "name": candidate.get("name", "Unnamed candidate"),
            "skills": sorted(candidate_skills),
            "matched_required": matched_required,
            "missing_required": missing_required,
            "matched_preferred": matched_preferred,
            "experience_years": exp,
            "experience_fit": round(exp_fit, 2),
            "required_skill_fit": round(req_fit, 2),
            "preferred_skill_fit": round(pref_fit, 2),
            "match_score": score,
            "notes": candidate.get("notes", "")
        }

class ScoringRankingAgent:
    name = "Scoring & Ranking Agent"
    def rank(self, analyses: list[dict]) -> list[dict]:
        # Stable, deterministic ordering: score descending, candidate ID ascending.
        ranked = sorted(analyses, key=lambda x: (-float(x["match_score"]), str(x["candidate_id"])))
        for i, item in enumerate(ranked, start=1):
            item["rank"] = i
        return ranked

class CriticValidationAgent:
    name = "Critic / Validation Agent"
    def validate(self, ranked: list[dict], candidates: list[dict], job: dict) -> dict:
        issues = []
        ids = [str(c.get("candidate_id", "")) for c in candidates]
        if len(ids) != len(set(ids)):
            issues.append("Duplicate candidate IDs detected.")
        if not job.get("required_skills"):
            issues.append("No required skills provided; skill-match scores may be uninformative.")
        if not candidates:
            issues.append("No candidate records provided.")
        seen_ranks = set()
        for item in ranked:
            score = item.get("match_score")
            if not isinstance(score, (int, float)) or not 0 <= score <= 100:
                issues.append(f"{item.get('candidate_id')}: score is outside 0–100.")
            if item.get("rank") in seen_ranks:
                issues.append("Duplicate rank detected.")
            seen_ranks.add(item.get("rank"))
            expected_missing = sorted(set(job.get("required_skills", [])) - set(item.get("matched_required", [])))
            # Case-normalized expected comparison
            expected_missing = sorted(s.lower() for s in expected_missing)
            actual_missing = sorted(s.lower() for s in item.get("missing_required", []))
            if expected_missing != actual_missing:
                issues.append(f"{item.get('candidate_id')}: missing-skill calculation inconsistent.")
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "checks": [
                {"check": "Score range 0–100", "passed": all(isinstance(x.get("match_score"), (int,float)) and 0 <= x["match_score"] <= 100 for x in ranked)},
                {"check": "Unique candidate IDs", "passed": len(ids) == len(set(ids))},
                {"check": "Rank sequence", "passed": sorted(seen_ranks) == list(range(1, len(ranked)+1))},
                {"check": "Required-skill accounting", "passed": not any("missing-skill calculation" in x for x in issues)}
            ]
        }

class HireWiseOrchestrator:
    def __init__(self):
        self.planner = PlannerAgent()
        self.analyst = CandidateAnalysisAgent()
        self.ranker = ScoringRankingAgent()
        self.critic = CriticValidationAgent()

    def run(self, job: dict, candidates: list[dict]) -> dict:
        events = []
        plan = self.planner.plan(job, candidates)
        events.append(AgentEvent("Planner Agent", "Create execution plan", "completed",
                                 f"Created {len(plan['tasks'])} tasks for {len(candidates)} candidates."))
        # Input checks are explicit and surfaced to the UI.
        clean = []
        input_warnings = []
        for c in candidates:
            if not c.get("candidate_id"):
                input_warnings.append("A candidate record is missing candidate_id.")
                continue
            if not c.get("name"):
                input_warnings.append(f"{c['candidate_id']} has no name.")
            clean.append(c)
        events.append(AgentEvent("Candidate Analysis Agent", "Extract skills and experience", "completed",
                                 f"Analyzed {len(clean)} valid candidate records."))
        analyses = [self.analyst.analyze(c, job) for c in clean]
        ranked = self.ranker.rank(analyses)
        events.append(AgentEvent("Scoring & Ranking Agent", "Calculate scores and rank", "completed",
                                 "Applied a documented 60/20/20 scoring rubric."))
        validation = self.critic.validate(ranked, clean, job)
        events.append(AgentEvent("Critic / Validation Agent", "Validate output", "passed" if validation["passed"] else "needs review",
                                 "All configured checks passed." if validation["passed"] else "; ".join(validation["issues"])))
        validation["input_warnings"] = input_warnings
        return {"plan": plan, "ranked_candidates": ranked, "validation": validation,
                "events": [asdict(e) for e in events]}
