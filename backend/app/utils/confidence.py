def aggregate_confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0
    bounded = [min(max(score, 0.0), 1.0) for score in scores]
    return round(sum(bounded) / len(bounded), 2)
