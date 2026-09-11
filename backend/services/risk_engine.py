def risk_level(probability: float) -> str:
    if probability >= 0.72:
        return "HIGH"
    if probability >= 0.42:
        return "MEDIUM"
    return "LOW"
