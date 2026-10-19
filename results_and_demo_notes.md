# HireWise AI — Results and Demonstration Notes

## Evaluation approach
The provided profiles are fictional and intentionally varied. The app computes a score for each profile using:
- 60% required-skill coverage
- 20% preferred-skill coverage
- 20% experience fit

Do not present synthetic results as evidence of improved real recruitment outcomes. Instead, present them as functional verification that the prototype can execute its defined workflow.

## Expected functional outcomes
- Each valid candidate receives a score from 0 to 100.
- Candidate ranks are ordered from highest score to lowest.
- Matched and missing required skills are displayed for explanation.
- The Critic Agent validates score range, unique candidate IDs, rank sequence, and skill accounting.
- Duplicate IDs or an empty required-skill list cause validation to fail.
- A recruiter can select which suggested candidates to include in the shortlist and download CSV/JSON outputs.

## Metrics to report honestly
| Metric | How to obtain | Interpretation |
|---|---|---|
| Candidate records processed | App result table | Functional coverage only |
| Average match score | App metric | Score summary, not hiring quality |
| Validation pass/fail | Critic output | Internal consistency checks |
| Unit test pass rate | `pytest -q` output | Software tests passed / tests run |
| Runtime | Time a demo run locally | Depends on device and candidate count |

## Demo script
“Our problem is that recruiters repeatedly compare many candidate profiles with a job description. HireWise AI divides that work into four software agents. The Planner defines the steps; the Analysis Agent extracts job-relevant matches; the Scoring Agent applies an explicit formula; and the Critic checks whether the results are internally consistent. The Streamlit dashboard shows why each score was assigned. A recruiter can review and edit the shortlist. The prototype uses synthetic data and a transparent rule-based model, so it does not claim to replace human judgment or prove real-world hiring performance.”

## Important result-reporting note
Run the tests on your own computer and capture screenshots of the actual running app and test output. Do not claim tests passed unless you have executed `pytest -q` successfully.
