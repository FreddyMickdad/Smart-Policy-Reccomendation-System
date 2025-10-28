
from typing import List, Dict, Any, Tuple
import math, json

def parse_eligibility(elig: str) -> Tuple[int, int]:
    try:
        parts = elig.split('-')
        return int(parts[0]), int(parts[1])
    except Exception:
        return 0, 120

def coverage_match_score(client_coverage: str, policy_coverage: str) -> int:
    client_tokens = set([t.strip().lower() for t in client_coverage.split(',') if t.strip()])
    policy_tokens = set([t.strip().lower() for t in policy_coverage.split(',') if t.strip()])
    return len(client_tokens & policy_tokens)

def affordability_score(client_income: float, policy_min: float, policy_max: float) -> float:
    if client_income is None or client_income <= 0:
        return 0.0
    comfortable = client_income * 0.25
    if comfortable >= policy_min and comfortable <= policy_max:
        return 1.0
    if comfortable < policy_min:
        return max(0.0, 1 - (policy_min - comfortable) / (policy_min + 1))
    return max(0.0, 1 - (comfortable - policy_max) / (comfortable + 1))

def parse_claims_history(claims_raw: Any) -> Dict[str, int]:
    if not claims_raw:
        return {}
    if isinstance(claims_raw, dict):
        return claims_raw
    try:
        if isinstance(claims_raw, str):
            try:
                return json.loads(claims_raw)
            except Exception:
                parts = [p.strip() for p in claims_raw.split(',') if p.strip()]
                out = {}
                for part in parts:
                    if ':' in part:
                        k,v = part.split(':',1)
                        out[k.strip().lower()] = int(v.strip())
                return out
    except Exception:
        return {}
    return {}

def risk_penalty(client: Dict[str, Any], policy: Dict[str, Any]) -> float:
    loss_ratio = client.get('loss_ratio', None)
    claims = parse_claims_history(client.get('claims_history', {}))
    penalty = 0.0
    if loss_ratio is not None:
        if loss_ratio >= 1.5:
            penalty += 0.4
        elif loss_ratio >= 1.2:
            penalty += 0.25
        elif loss_ratio >= 1.0:
            penalty += 0.15
        elif loss_ratio < 0.5:
            penalty -= 0.05
    for k,v in claims.items():
        if v <= 0:
            continue
        if k in policy.get('coverage_type','').lower():
            penalty += 0.15 * min(v, 4)
        else:
            penalty += 0.08 * min(v, 4)
    rt = policy.get('risk_tolerance','medium').lower()
    if rt == 'high':
        penalty *= 0.9
    elif rt == 'low':
        penalty *= 1.1
    penalty = max(0.0, min(0.9, penalty))
    return round(penalty,3)

def recommend_policies(client: Dict[str, Any], policies: List[Dict[str, Any]], top_n: int = 10) -> List[Dict[str, Any]]:
    scored = []
    for p in policies:
        min_age, max_age = parse_eligibility(p.get('eligibility','0-120'))
        if client.get('age') is None or client.get('age') < min_age or client.get('age') > max_age:
            continue
        cscore = coverage_match_score(client.get('coverage',''), p.get('coverage_type',''))
        if cscore == 0:
            continue
        aff = affordability_score(client.get('income',0), p.get('premium_min',0), p.get('premium_max',0))
        budget = client.get('budget', None)
        budget_bonus = 0.0
        if budget is not None and p.get('premium_min',0) <= budget:
            budget_bonus = 0.15
        penalty = risk_penalty(client, p)
        total_score = (0.5 * cscore) + (0.3 * aff) + (0.15 * budget_bonus) - penalty
        total_score = round(max(0.0, total_score),3)
        if total_score <= 0:
            continue
        scored.append({
            **p,
            "score": total_score,
            "coverage_match": cscore,
            "affordability": round(aff,3),
            "budget_bonus": budget_bonus,
            "risk_penalty": penalty
        })
    scored_sorted = sorted(scored, key=lambda x: (-x['score'], x['premium_min']))
    return scored_sorted[:top_n]
