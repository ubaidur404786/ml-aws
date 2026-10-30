"""Download the IBM Telco Customer Churn dataset into ml/data/.

Source: https://github.com/IBM/telco-customer-churn-on-icp4d (Apache License 2.0)
"""
from pathlib import Path
from urllib.request import urlretrieve

DATASET_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    "master/data/Telco-Customer-Churn.csv"
)
DATA_DIR = Path(__file__).parent / "data"
DATA_FILE = DATA_DIR / "Telco-Customer-Churn.csv"


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if DATA_FILE.exists():
        print(f"Dataset already exists: {DATA_FILE}")
        return
    print(f"Downloading {DATASET_URL} ...")
    urlretrieve(DATASET_URL, DATA_FILE)
    print(f"Saved to {DATA_FILE} ({DATA_FILE.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
