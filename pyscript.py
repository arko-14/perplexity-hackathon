import re
import csv
from pathlib import Path

# CONFIG
INPUT_FILE = Path("texts/3397.txt")
OUTPUT_CSV = Path("output_clean.csv")

# Read all lines
text = INPUT_FILE.read_text(encoding="utf-8", errors="ignore")
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

# 4) Write to CSV with proper quoting
with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    # Header
    writer.writerow(["case_name", "case_id", "judgement"])
    # Single row
    writer.writerow([case_name, case_id, judgement])

print(f"Cleaned CSV written to {OUTPUT_CSV}")
