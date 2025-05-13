import os
import csv
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# 1. Configuration
CSV_FILE   = "supreme_court_jan2011_cases.csv"   # your input CSV (must have a column named "url")
OUTPUT_DIR = "texts2"            # folder to save .txt files
HEADERS    = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 2. Prepare output folder
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 3. Helper to generate a safe filename from URL
def txt_filename_from_url(url):
    path = urlparse(url).path.rstrip("/")
    name = path.split("/")[-1] or "case"
    return f"{name}.txt"

# 4. Read CSV and process each URL
with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for idx, row in enumerate(reader, start=1):
        page_url = row["url"].strip()
        print(f"[{idx}] Loading: {page_url}")
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            print(f"    ✖️ Failed to load page: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # 5. Extract the judgment text
        content_div = soup.find("div", id="documentContent")
        if content_div:
            text = content_div.get_text(separator="\n").strip()
        else:
            print("    ⚠️ No documentContent div found—saving full page text instead.")
            text = soup.get_text(separator="\n").strip()

        # 6. Write to .txt file
        filename = txt_filename_from_url(page_url)
        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"    ✅ Saved as: {out_path}")

print("\nAll done! Check the ‘texts/’ folder for your .txt files.")
