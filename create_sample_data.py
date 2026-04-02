"""
Generate sample ML dataset for testing the sync script.
Creates a small CSV dataset simulating tabular ML data.
"""

import csv
import os
import random
from pathlib import Path

DATASET_DIR = "sample_dataset"


def create_sample_data():
    """Create sample CSV files to test syncing."""
    Path(DATASET_DIR).mkdir(exist_ok=True)

    # Training data
    train_file = os.path.join(DATASET_DIR, "train.csv")
    with open(train_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["feature_1", "feature_2", "feature_3", "label"])
        for _ in range(100):
            writer.writerow([
                round(random.uniform(0, 10), 2),
                round(random.uniform(0, 100), 2),
                random.choice(["A", "B", "C"]),
                random.randint(0, 1),
            ])
    print(f"Created {train_file} (100 rows)")

    # Validation data
    val_file = os.path.join(DATASET_DIR, "validation.csv")
    with open(val_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["feature_1", "feature_2", "feature_3", "label"])
        for _ in range(20):
            writer.writerow([
                round(random.uniform(0, 10), 2),
                round(random.uniform(0, 100), 2),
                random.choice(["A", "B", "C"]),
                random.randint(0, 1),
            ])
    print(f"Created {val_file} (20 rows)")

    # Metadata
    meta_file = os.path.join(DATASET_DIR, "metadata.json")
    import json
    metadata = {
        "dataset_name": "sample_classification",
        "version": "1.0",
        "features": ["feature_1", "feature_2", "feature_3"],
        "target": "label",
        "train_samples": 100,
        "val_samples": 20,
    }
    with open(meta_file, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Created {meta_file}")

    print(f"\nSample dataset ready in '{DATASET_DIR}/'")


if __name__ == "__main__":
    create_sample_data()
