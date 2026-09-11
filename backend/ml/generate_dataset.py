from pathlib import Path
import csv
import random

random.seed(26165)
SITES = ["Duliajan Central", "Bongaigaon Refinery", "Digboi Field", "Numaligarh Terminal", "Jorhat Pipeline", "Guwahati Depot", "Lakwa Production"]
DEPARTMENTS = ["Production", "Maintenance", "Drilling", "Projects", "Logistics", "Electrical", "Process Safety"]
TEMPLATES = [
    ("Unsafe Act", "Maintenance was carried out while the equipment was still energized and proper isolation was not confirmed.", "Energy Isolation", "Equipment Maintenance", True),
    ("Unsafe Condition", "A temporary scaffold at the work front had an unprotected edge and no inspected fall-arrest anchor.", "Work at Height", "Working at Height", True),
    ("Near Miss", "A suspended load shifted during crane lifting while personnel were inside the exclusion zone.", "Suspended Loads", "Lifting Operations", True),
    ("Incident", "Gas testing was not completed before entry into a vessel and the standby arrangement was missing.", "Confined Space", "Confined Space Entry", True),
    ("Unsafe Condition", "Good housekeeping was needed around a walkway; minor oil residue was observed near the pump.", "Other", "Routine Inspection", False),
    ("Near Miss", "A hand tool was found without its tether during routine workshop work, with no exposure reported.", "Other", "Workshop Operations", False),
    ("Unsafe Act", "The operator used the designated PPE and completed the pre-job briefing before starting the task.", "Other", "Routine Operations", False),
    ("Unsafe Condition", "A warning sign was faded at the warehouse entrance but the access route remained controlled.", "Other", "Material Handling", False),
]


def main():
    destination = Path(__file__).parents[1] / "data" / "safety_reports.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for index in range(1000):
        kind, base, rule, activity, sif = TEMPLATES[index % len(TEMPLATES)]
        variation = [" during the morning shift", " during planned work", " near the main work area", " reported by the field supervisor", " before handover"][(index // len(TEMPLATES)) % 5]
        rows.append({"report_text": base + variation, "report_type": kind, "location": random.choice(SITES), "department": random.choice(DEPARTMENTS), "activity": activity, "life_saving_rule": rule, "barrier_failure": "Critical control not effective" if sif else "Minor control gap", "potential_consequence": "Serious injury or fatality" if sif else "Low-severity injury or property damage", "sif_label": "SIF-Potential" if sif else "Non-SIF-Potential"})
    with destination.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} records at {destination}")


if __name__ == "__main__":
    main()
