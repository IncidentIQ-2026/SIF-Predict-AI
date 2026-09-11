import re

RULES = {
    "Energy Isolation": ["energized", "isolation", "lockout", "tagout", "loto", "stored energy"],
    "Hot Work": ["welding", "cutting", "grinding", "hot work", "spark", "flammable"],
    "Confined Space": ["confined space", "manhole", "tank entry", "oxygen", "gas test"],
    "Line of Fire": ["line of fire", "pinch point", "struck", "caught between", "moving vehicle"],
    "Work at Height": ["height", "scaffold", "ladder", "unprotected edge", "fall arrest"],
    "Suspended Loads": ["suspended", "lifting", "crane", "load", "rigging", "hoist"],
    "Excavation": ["excavat", "trench", "collapse", "shoring", "underground service"],
}
ACTIVITIES = {
    "Equipment Maintenance": ["maintenance", "repair", "pump", "valve", "equipment"],
    "Welding and Cutting": ["welding", "cutting", "grinding", "hot work"],
    "Confined Space Entry": ["confined space", "manhole", "tank entry"],
    "Lifting Operations": ["lifting", "crane", "rigging", "suspended", "hoist"],
    "Working at Height": ["height", "scaffold", "ladder", "fall"],
    "Excavation": ["excavat", "trench", "shoring"],
}
BARRIERS = {
    "Energy Isolation": "Isolation and lockout/tagout not verified",
    "Hot Work": "Hot-work permit, gas testing or fire watch failed",
    "Confined Space": "Entry permit, atmospheric testing or standby failed",
    "Line of Fire": "Exclusion zone, guarding or positioning failed",
    "Work at Height": "Fall protection or edge protection failed",
    "Suspended Loads": "Lift plan, rigging inspection or exclusion zone failed",
    "Excavation": "Permit, shoring or underground-service control failed",
}


def _contains(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def extract_precursors(text: str, supplied_activity: str = "General Operations") -> dict[str, str]:
    normalized = re.sub(r"\s+", " ", text.lower()).strip()
    rule = max(RULES, key=lambda item: sum(term in normalized for term in RULES[item])) if any(_contains(normalized, terms) for terms in RULES.values()) else "Other"
    activity = next((name for name, terms in ACTIVITIES.items() if _contains(normalized, terms)), supplied_activity or "General Operations")
    barrier = BARRIERS.get(rule, "A critical control or safe-work practice was not effective")
    consequence = "Serious injury or fatality from uncontrolled exposure"
    if rule == "Work at Height": consequence = "Fatal fall from height or struck-by injury"
    elif rule == "Energy Isolation": consequence = "Fatal contact with hazardous energy"
    elif rule == "Confined Space": consequence = "Asphyxiation, toxic exposure or rescue failure"
    return {"life_saving_rule": rule, "activity": activity, "barrier_failure": barrier, "potential_consequence": consequence}
