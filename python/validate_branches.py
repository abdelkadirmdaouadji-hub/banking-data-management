from pathlib import Path
import sys
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) > 1:
    file_name = sys.argv[1]
else:
    file_name = "branches.csv"

BRANCHES_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / file_name
)

branches = pd.read_csv(
    BRANCHES_FILE,
    parse_dates=["opening_date"]
)

print("Branches dataset loaded.")
print(f"Rows: {len(branches):,}")
print(f"Columns: {len(branches.columns)}")

# 1. Duplicate branch IDs
duplicate_branch_ids = branches["branch_id"].duplicated(
    keep=False
).sum()

# 2. Future opening dates
today = pd.Timestamp.today().normalize()

future_opening_dates = (
    branches["opening_date"] > today
).sum()

# 3. Missing values
missing_branch_id = branches["branch_id"].isna().sum()
missing_branch_name = branches["branch_name"].isna().sum()
missing_city = branches["city"].isna().sum()
missing_region = branches["region"].isna().sum()
missing_country = branches["country"].isna().sum()
missing_opening_date = branches["opening_date"].isna().sum()
missing_manager_name = branches["manager_name"].isna().sum()

print(f"\nDuplicate branch IDs: {duplicate_branch_ids}")
print(f"Future opening dates: {future_opening_dates}")

print("\nMissing values:")
print(f"branch_id: {missing_branch_id}")
print(f"branch_name: {missing_branch_name}")
print(f"city: {missing_city}")
print(f"region: {missing_region}")
print(f"country: {missing_country}")
print(f"opening_date: {missing_opening_date}")
print(f"manager_name: {missing_manager_name}")

valid_city_regions = {
    "Brussels": "Brussels-Capital",
    "Antwerp": "Flanders",
    "Ghent": "Flanders",
    "Bruges": "Flanders",
    "Leuven": "Flanders",
    "Mechelen": "Flanders",
    "Hasselt": "Flanders",
    "Liege": "Wallonia",
    "Namur": "Wallonia",
    "Mons": "Wallonia",
    "Charleroi": "Wallonia",
    "Tournai": "Wallonia"
}

invalid_city_region = branches.apply(
    lambda row: (
        row["city"] not in valid_city_regions
        or valid_city_regions[row["city"]] != row["region"]
    ),
    axis=1
).sum()

print(f"\nInvalid city/region combinations: {invalid_city_region}")

quality_checks = [
    {
        "check": "Duplicate branch IDs",
        "errors": duplicate_branch_ids
    },
    {
        "check": "Future opening dates",
        "errors": future_opening_dates
    },
    {
        "check": "Missing branch ID",
        "errors": missing_branch_id
    },
    {
        "check": "Missing branch name",
        "errors": missing_branch_name
    },
    {
        "check": "Missing city",
        "errors": missing_city
    },
    {
        "check": "Missing region",
        "errors": missing_region
    },
    {
        "check": "Missing country",
        "errors": missing_country
    },
    {
        "check": "Missing opening date",
        "errors": missing_opening_date
    },
    {
        "check": "Missing manager name",
        "errors": missing_manager_name
    },
    {
        "check": "Invalid city/region combination",
        "errors": invalid_city_region
    }
]

quality_report = pd.DataFrame(quality_checks)

quality_report["status"] = quality_report["errors"].apply(
    lambda x: "PASS" if x == 0 else "FAIL"
)

print("\n--- BRANCHES DATA QUALITY REPORT ---")
print(quality_report)

overall_status = (
    "PASS"
    if (quality_report["errors"] == 0).all()
    else "FAIL"
)

print(f"\nOverall data quality status: {overall_status}")

QUALITY_REPORT_DIR = PROJECT_ROOT / "data" / "quality_reports"

report_name = f"{Path(file_name).stem}_quality_report.csv"

report_file = QUALITY_REPORT_DIR / report_name

quality_report.to_csv(
    report_file,
    index=False
)

print(f"Quality report saved to: {report_file}")

if overall_status == "FAIL":
    sys.exit(1)

sys.exit(0)

