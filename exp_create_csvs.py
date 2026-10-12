from sklearn.model_selection import train_test_split
from pathlib import Path

from exp_misc import db_path
from exp_db import DB
from exp_labels import select_label

out_dir = Path(__file__).parent.joinpath("csvs")
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