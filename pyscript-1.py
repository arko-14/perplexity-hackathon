import re
import csv
import random
from pathlib import Path

# CONFIG
INPUT_DIR = Path("texts4")            # Directory containing your .txt files
OUTPUT_CSV = Path("may2011.csv")  # CSV output file
NUM_FILES = 12                        # Number of random files to process

# Gather all .txt files
all_files = [p for p in INPUT_DIR.glob("*.txt") if p.is_file()]

# Randomly select up to NUM_FILES files
selected_files = random.sample(all_files, min(NUM_FILES, len(all_files)))

# Prepare rows for CSV
rows = []

for file_path in selected_files:
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # 1) case_name = first non-empty line
    case_name = next((ln.strip() for ln in lines if ln.strip()), "")

    # 2) Find CRIMINAL APPEAL NO. and its index
    case_id = ""
    start_idx = None
    for idx, ln in enumerate(lines):
        m = re.search(r'CRIMINAL\s+APPEAL\s+NO\.?\s*([\d/]+)', ln, re.IGNORECASE)
        if m:
            case_id = m.group(1).strip()
            start_idx = idx
            break

    # 3) Extract and clean judgement
    if start_idx is not None:
        raw_judg = "\n".join(lines[start_idx+1:]).strip()
    else:
        raw_judg = "\n".join(lines[1:]).strip()

    # Collapse whitespace: replace all runs of whitespace (including newlines) with a single space
    judgement = re.sub(r'\s+', ' ', raw_judg)

    rows.append({
        "case_name": case_name,
        "case_id": case_id,
        "judgement": judgement
    })

# 4) Write all rows to CSV with proper quoting
with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["case_name", "case_id", "judgement"])  # Header
    for row in rows:
        writer.writerow([row["case_name"], row["case_id"], row["judgement"]])

print(f"Processed {len(rows)} files and wrote to {OUTPUT_CSV}")
