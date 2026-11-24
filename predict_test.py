
import os
import re
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent

DATASET_NAME = "PhiUSIIL_Phishing_URL_Dataset.csv"

TEST_URL = "https://www.uni-mainz.de"


# ============================================================
# FIND DATASET AUTOMATICALLY
# ============================================================

def find_dataset():
    """
    Search for PhiUSIIL_Phishing_URL_Dataset.csv
    inside the project directory and its subdirectories.
    """

    print("=" * 70)
    print("SEARCHING FOR DATASET")
    print("=" * 70)

    print("Project directory:")
    print(PROJECT_DIR)

    # First check common locations
    possible_locations = [
        PROJECT_DIR / DATASET_NAME,
        PROJECT_DIR / "data" / DATASET_NAME,
        PROJECT_DIR / "dataset" / DATASET_NAME,
        PROJECT_DIR / "datasets" / DATASET_NAME,
        PROJECT_DIR / "Data" / DATASET_NAME,
        PROJECT_DIR / "Dataset" / DATASET_NAME,
    ]

    for path in possible_locations:

        if path.exists():

            print()
            print("Dataset found:")
            print(path)

            return path

    # Search recursively
    print()
    print("Searching subdirectories...")

    matches = list(
        PROJECT_DIR.rglob(DATASET_NAME)
    )

    if matches:

        print()
        print("Dataset found:")
        print(matches[0])

        return matches[0]

    print()
    print("ERROR: Dataset was not found.")
    print()
    print("Expected filename:")
    print(DATASET_NAME)
    print()
    print("Project directory searched:")
    print(PROJECT_DIR)

    print()
    print("CSV files currently found:")

    csv_files = list(
        PROJECT_DIR.rglob("*.csv")
    )

    if csv_files:

        for csv_file in csv_files:
            print(" -", csv_file)

    else:

        print("No CSV files found.")

    return None


# ============================================================
# CLEAN URL
# ============================================================

def clean_url(value):
    """
    Convert dataset URL values such as

    [https://example.com](https://example.com)

    into

    https://example.com
    """

    if pd.isna(value):
        return ""

    value = str(value).strip()

    markdown_match = re.search(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        value
    )

    if markdown_match:
        value = markdown_match.group(2)

    value = value.strip()
    value = value.strip('"')
    value = value.strip("'")

    return value


# ============================================================
# FIND URL COLUMN
# ============================================================

def find_url_column(df):

    possible_columns = [
        "URL",
        "url",
        "Url",
        "URLName",
        "url_name",
    ]

    for column in possible_columns:

        if column in df.columns:
            return column

    # Try case-insensitive search
    for column in df.columns:

        if str(column).lower() == "url":
            return column

    return None


# ============================================================
# FIND LABEL COLUMN
# ============================================================

def find_label_column(df):

    possible_columns = [
        "label",
        "Label",
        "LABEL",
        "status",
        "Status",
        "class",
        "Class",
        "target",
        "Target",
    ]

    for column in possible_columns:

        if column in df.columns:
            return column

    # Case-insensitive search
    for column in df.columns:

        lower = str(column).lower()

        if lower in {
            "label",
            "status",
            "class",
            "target"
        }:
            return column

    return None


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    dataset_path = find_dataset()

    if dataset_path is None:

        raise FileNotFoundError(
            "\nPhiUSIIL_Phishing_URL_Dataset.csv "
            "could not be found."
        )

    print()
    print("=" * 70)
    print("LOADING DATASET")
    print("=" * 70)

    print("Path:")
    print(dataset_path)

    df = pd.read_csv(
        dataset_path,
        low_memory=False
    )

    print()
    print("Dataset loaded successfully.")

    print(
        "Rows:",
        len(df)
    )

    print(
        "Columns:",
        len(df.columns)
    )

    print()
    print("Columns:")
    print(
        df.columns.tolist()
    )

    return df


# ============================================================
# FIND TEST URL IN DATASET
# ============================================================

def find_url_in_dataset(df, test_url):

    url_column = find_url_column(df)

    if url_column is None:

        print()
        print("ERROR: URL column not found.")

        return None, None

    print()
    print("=" * 70)
    print("URL COLUMN")
    print("=" * 70)

    print(
        "URL column:",
        url_column
    )

    target_url = clean_url(test_url)

    print()
    print("Searching for:")
    print(target_url)

    # Create cleaned temporary URL column
    cleaned_urls = (
        df[url_column]
        .apply(clean_url)
        .str.lower()
        .str.rstrip("/")
    )

    search_url = (
        target_url
        .lower()
        .rstrip("/")
    )

    matches = df[
        cleaned_urls == search_url
    ]

    if len(matches) == 0:

        print()
        print("URL was not found in dataset.")

        return None, url_column

    print()
    print("URL found!")

    row = matches.iloc[0]

    return row, url_column


# ============================================================
# DISPLAY DATASET ROW
# ============================================================

def display_dataset_row(row):

    if row is None:
        return

    print()
    print("=" * 70)
    print("DATASET ROW")
    print("=" * 70)

    print(row.to_string())


# ============================================================
# DISPLAY LABEL
# ============================================================

def display_label(row, df):

    if row is None:
        return

    label_column = find_label_column(df)

    if label_column is None:

        print()
        print("Label column not found.")

        return

    label = row[label_column]

    print()
    print("=" * 70)
    print("DATASET LABEL")
    print("=" * 70)

    print(
        "Label column:",
        label_column
    )

    print(
        "Dataset label:",
        label
    )

    print()

    print(
        "IMPORTANT:"
    )

    print(
        "Do not assume that 0 = phishing or "
        "1 = phishing until the label mapping "
        "from your training code is confirmed."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("PHIUSIIL DATASET CHECK")
    print("=" * 70)

    print()
    print("Test URL:")
    print(TEST_URL)

    try:

        df = load_dataset()

    except Exception as e:

        print()
        print("DATASET ERROR:")
        print(str(e))

        return

    row, url_column = find_url_in_dataset(
        df,
        TEST_URL
    )

    if row is None:

        print()
        print("=" * 70)
        print("RESULT")
        print("=" * 70)

        print(
            "The URL is not present in the dataset."
        )

        print()
        print(
            "This is not an extractor error."
        )

        return

    display_dataset_row(row)

    display_label(
        row,
        df
    )

    print()
    print("=" * 70)
    print("CHECK FINISHED")
    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()

