import os
import json
import anthropic

from .rubric import get_weights, get_penalty_config, get_time_pressure_note, SPEAKING_ONLY_CRITERIA

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

MODEL = "claude-sonnet-4-6"


def build_prompt(
    subtopic_name: str,
    subtopic_description: str,
    references: list,
    mode: str,
    strictness: str,
    user_input: str,
    time_used_sec: int,
    response_time_sec: int,
) -> str:
    weights = get_weights(mode, strictness)
    penalties = get_penalty_config(strictness)
    time_note = get_time_pressure_note(time_used_sec, response_time_sec, mode)

    ref_text = "\n".join(f"- {r['citation_text']}" + (f" ({r['url']})" if r.get("url") else "") for r in references)

    criteria_list = "\n".join(f"- {k} (weight: {v * 100:.1f}%)" for k, v in weights.items())

    strictness_guidance = {
        "lenient": "Be encouraging. Focus feedback on content and ideas over surface polish. Minor grammar/phrasing slips should barely affect the score.",
        "moderate": "Be balanced and fair. Note both strengths and weaknesses clearly without being harsh or overly generous.",
        "strict": "Be rigorous and precise, as if this were a formal evaluation (e.g. competitive exam or professional review). Do not let strong content excuse weak execution.",
    }[strictness]

    mode_label = "spoken (transcribed from speech)" if mode == "speak" else "written"

    return f"""You are an expert evaluator for a speaking/writing practice platform. Evaluate the user's {mode_label} response below.

SUBTOPIC: {subtopic_name}
SUBTOPIC CONTEXT: {subtopic_description}

REFERENCE MATERIAL PROVIDED TO USER:
{ref_text if ref_text else "(none provided)"}

EVALUATION MODE: {strictness} — {strictness_guidance}

CRITERIA AND WEIGHTS (weights sum to 100%):
{criteria_list}

TIME CONTEXT: {time_note} (used {time_used_sec}s of {response_time_sec}s allotted)

PENALTY RULES: Deduct up to {penalties['major_issue_penalty']} points (of 100) total for major issues (e.g. off-topic drift, incoherent argument, misuse or fabrication of a cited fact). Deduct up to {penalties['minor_issue_penalty']} points total for minor issues (small grammar slips, awkward phrasing) beyond what's already reflected in per-criterion scores.

USER'S RESPONSE:
\"\"\"
{user_input}
\"\"\"

Score each criterion from 0-10, then compute an overall score out of 100 using the weights above (each criterion score * weight * 10, summed), then apply penalty deductions if applicable.

Respond with ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{{
  "criteria": {{
    "<criterion_name>": {{"score": <0-10 float>, "comment": "<1 sentence>"}},
    ...
  }},
  "overall_score": <0-100 float, after penalties>,
  "feedback": "<3-5 sentence personalized narrative feedback, addressed to the user directly>",
  "strengths": ["<short point>", "<short point>"],
  "improvements": ["<short point>", "<short point>"]
}}
"""


def evaluate_response(
    subtopic_name: str,
    subtopic_description: str,
    references: list,
    mode: str,
    strictness: str,
    user_input: str,
    time_used_sec: int,
    response_time_sec: int,
) -> dict:
    prompt = build_prompt(
        subtopic_name, subtopic_description, references,
        mode, strictness, user_input, time_used_sec, response_time_sec,
    )

    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = message.content[0].text.strip()
    # Defensive cleanup in case the model wraps in fences despite instructions
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    parsed = json.loads(raw_text)

    weights = get_weights(mode, strictness)
    for k in parsed["criteria"]:
        parsed["criteria"][k]["weight"] = weights.get(k, 0)

    return parsed
