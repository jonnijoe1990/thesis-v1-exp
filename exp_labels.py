from dataclasses import dataclass
from typing import List, Literal
from questionary import Choice, select

@dataclass
class Label:
    name: Literal["gender", "mortality", "age"]
    problem_type: Literal["classification", "regression"]
    sql: str
    exclusions: List[str]

LABELS: List[Label] = [
    Label(
        "gender",
        "classification",
        "SELECT id, c_gender AS label FROM sap_ish_patient WHERE c_gender <> 'Divers'",
        ["base__c_gender"]
    ),
    Label(
        "mortality",
        "classification",
        "SELECT id, c_datetimeofdeath IS NOT NULL AS label FROM sap_ish_patient",
        ["base__c_entlassungsart"]
    ),
    Label(
        "age",
        "regression",
        "SELECT id, c_age AS label FROM sap_ish_fall WHERE c_age IS NOT NULL",
        ["base__c_age", "base__c_birthdate"]
    ),
    Label(
        "length_of_stay",
        "regression",
        """SELECT id, EXTRACT(EPOCH FROM (c_entlassung - c_aufnahme)) / 86400.0 AS label
        FROM sap_ish_fall
        WHERE c_aufnahme IS NOT NULL AND c_entlassung IS NOT NULL""",
        [
            "base__aufenthaltsdauer_tage",
            "bewegung__gesamt_stunden",
            "bewegung__0100__hours",
            "bewegung__0104__hours",
            "bewegung__0107__hours",
            "bewegung__0152__hours",
            "bewegung__0200__hours",
            "bewegung__0300__hours",
            "bewegung__0400__hours",
            "bewegung__0500__hours",
            "bewegung__0600__hours",
            "bewegung__0700__hours",
            "bewegung__0900__hours",
            "bewegung__1000__hours",
            "bewegung__1100__hours",
            "bewegung__1200__hours",
            "bewegung__1300__hours",
            "bewegung__1500__hours",
            "bewegung__1600__hours",
            "bewegung__1700__hours",
            "bewegung__1800__hours",
            "bewegung__2000__hours",
            "bewegung__2100__hours",
            "bewegung__2136__hours",
            "bewegung__2200__hours",
            "bewegung__2300__hours",
            "bewegung__2425__hours",
            "bewegung__2500__hours",
            "bewegung__2600__hours",
            "bewegung__2700__hours",
            "bewegung__2800__hours",
            "bewegung__2856__hours",
            "bewegung__2900__hours",
            "bewegung__3000__hours",
            "bewegung__3100__hours",
            "bewegung__3200__hours",
            "bewegung__3300__hours",
            "bewegung__3400__hours",
            "bewegung__3500__hours",
            "bewegung__3600__hours",
            "bewegung__3700__hours",
            "bewegung__3751__hours",
            "bewegung__9999__hours",
        ]
    )
]

def select_label() -> Label:
    choices = [Choice(title=f"{label.name} ({label.problem_type})", value=label) for label in LABELS]
    selected = select(
        message="Zielgröße wählen:",
        choices=choices,
        instruction="Pfeiltasten, Enter bestätigt"
    ).ask()
    return selected
