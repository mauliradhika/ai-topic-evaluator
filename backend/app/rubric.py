"""
Rubric weighting engine.

Design principle:
- Base criteria are shared across modes, but weights shift based on:
    1. mode (speak vs write) - speaking cares more about structure/fluency-under-pressure,
       writing cares more about grammar/sentence precision since there's no excuse for typos.
    2. strictness (lenient/moderate/strict) - strict mode redistributes weight toward
       precision criteria (grammar, terminology) and penalizes major issues harder;
       lenient mode redistributes weight toward content/structure and softens penalties.

Weights must sum to 1.0 per configuration.
"""

BASE_CRITERIA = ["grammar", "sentence_formation", "terminology", "structure", "content_relevance"]
SPEAKING_ONLY_CRITERIA = ["fluency_pacing"]


def get_weights(mode: str, strictness: str) -> dict:
    if mode == "write":
        weights = {
            "grammar": 0.25,
            "sentence_formation": 0.20,
            "terminology": 0.15,
            "structure": 0.20,
            "content_relevance": 0.20,
        }
    else:  # speak
        weights = {
            "grammar": 0.10,
            "sentence_formation": 0.15,
            "terminology": 0.15,
            "structure": 0.20,
            "content_relevance": 0.20,
            "fluency_pacing": 0.20,
        }

    # Strictness modifiers: shift weight toward/away from precision criteria
    if strictness == "strict":
        shift = 0.07
        precision_keys = ["grammar", "terminology"]
        lenient_keys = ["content_relevance", "structure"]
    elif strictness == "lenient":
        shift = -0.07
        precision_keys = ["grammar", "terminology"]
        lenient_keys = ["content_relevance", "structure"]
    else:
        shift = 0
        precision_keys = []
        lenient_keys = []

    if shift != 0:
        per_key_shift = shift / len(precision_keys)
        per_key_reduction = shift / len(lenient_keys)
        for k in precision_keys:
            if k in weights:
                weights[k] += per_key_shift
        for k in lenient_keys:
            if k in weights:
                weights[k] -= per_key_reduction

    # Normalize to sum exactly 1.0 (guards against float drift)
    total = sum(weights.values())
    weights = {k: round(v / total, 4) for k, v in weights.items()}
    return weights


def get_penalty_config(strictness: str) -> dict:
    """
    Controls how harshly 'major issues' (e.g. off-topic content, incoherent
    argument, factual misuse of a cited reference) hit the overall score.
    Returned as a max percentage deduction applied on top of the weighted score.
    """
    return {
        "lenient": {"major_issue_penalty": 5, "minor_issue_penalty": 1},
        "moderate": {"major_issue_penalty": 12, "minor_issue_penalty": 3},
        "strict": {"major_issue_penalty": 20, "minor_issue_penalty": 5},
    }[strictness]


def get_time_pressure_note(time_used_sec: int, response_time_sec: int, mode: str) -> str:
    """
    Used inside the eval prompt to give the AI context on whether the user
    used the full time, cut it short, or ran close to the limit - relevant
    for evaluating structure/completeness fairly.
    """
    ratio = time_used_sec / response_time_sec if response_time_sec else 1
    if ratio < 0.4:
        return "The user ended significantly early - be mindful evaluating structure/completeness fairly, but do not penalize speed itself."
    elif ratio > 0.95:
        return "The user used nearly the full allotted time."
    else:
        return "The user used a moderate portion of the allotted time."
