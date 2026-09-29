from dataclasses import dataclass
from typing import List, Literal
from questionary import Choice, select
from sklearn.model_selection import train_test_split
from pathlib import Path

from misc import db_path
from db import DB

@dataclass
class Label:
    name: Literal["gender", "mortality"]
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
        "SELECT id, (c_datetimeofdeath IS NOT NULL) AS label FROM sap_ish_patient",
        []
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


out_dir = Path(__file__).parent.parent.joinpath("csvs")
out_dir.mkdir(exist_ok=True)
folds = 5

label = select_label()
if label is not None:
    with DB(db_path) as db:

        feature_matrix_table_name = f"features_{label.name}"

        db.execute(f"""
            CREATE TEMP TABLE {feature_matrix_table_name} AS 
                SELECT 
                    label,
                    t.* {f"EXCLUDE ({', '.join(label.exclusions)})" if label.exclusions else ''}
                FROM ({label.sql}) AS labels
                JOIN transformed AS t 
                    ON labels.id = t.id
        """)

        labels = db.execute(f"SELECT id, label FROM {feature_matrix_table_name}").fetchdf()

        for i in range(folds):

            train_ids, test_ids = train_test_split(
                labels[["id"]],
                test_size=0.2,
                random_state=i,
                stratify=labels["label"] if label.problem_type == "classification" else None
            )

            for split_name, split_frame in [("train", train_ids), ("test", test_ids)]:
                ###
                split_table_name = f"{split_name}_ids"
                csv_fn = f"{label.name}_{split_name}_{i}.csv"
                ###
                db.register(split_table_name, split_frame)
                db.execute(f"""
                    COPY (
                        SELECT
                            fm.*
                        FROM {split_table_name} AS included
                        JOIN {feature_matrix_table_name} AS fm
                            ON included.id = fm.id
                    ) TO '{out_dir.joinpath(csv_fn)}'
                    (FORMAT CSV, HEADER)
                """)
                db.unregister(split_table_name)
                ###
                print(f"wrote: {csv_fn}") 