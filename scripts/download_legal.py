import os
import csv
import random
import time
import requests

# ─── CONFIG ─────────────────────────────────────────────
API_TOKEN       = "33c261ae66ce5617e0b14d61723e373929cba65f"  # ← replace with your token  
BASE_URL        = "https://api.indiankanoon.org"
SAMPLE_SIZE     = 80                         # between 50–100
PAGE_SIZE       = 50
PAGES_PER_COURT = 2
# ───────────────────────────────────────────────────────

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Accept": "application/json",
}

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/metadata", exist_ok=True)

def search_court(court_name):
    """
    Return a list of docids for the given court_name, via POST requests.
    """
    ids = []
    for page in range(PAGES_PER_COURT):
        payload = {
            "formInput": f"docsource: {court_name}",
            "pagenum": page,
            "maxpages": PAGE_SIZE
        }
        resp = requests.post(f"{BASE_URL}/search/", headers=HEADERS, data=payload, timeout=10)
        resp.raise_for_status()
        docs = resp.json().get("docs", [])
        if not docs:
            break
        ids.extend(d["tid"] for d in docs)
        time.sleep(0.1)
    return ids

def fetch_case(docid):
    """
    Fetch metadata and full text for a given docid via POST.
    """
    m_resp = requests.post(f"{BASE_URL}/docmeta/{docid}/", headers=HEADERS, timeout=10)
    m_resp.raise_for_status()
    meta = m_resp.json()

    t_resp = requests.post(f"{BASE_URL}/doc/{docid}/", headers=HEADERS, timeout=10)
    t_resp.raise_for_status()
    text = t_resp.json().get("judgmentText", "")

    return meta, text

def main():
    # 1) gather IDs
    sc_ids = search_court("Supreme Court")
    hc_ids = search_court("High Court")
    pool   = list(set(sc_ids + hc_ids))

    if len(pool) < SAMPLE_SIZE:
        raise RuntimeError(f"Found only {len(pool)} cases; try increasing PAGE_SIZE or PAGES_PER_COURT")

    # 2) random sample
    chosen = random.sample(pool, SAMPLE_SIZE)

    rows = []
    for docid in chosen:
        try:
            m, txt = fetch_case(docid)
            court = m.get("docsource", "")
            if not any(c in court for c in ("Supreme","High")):
                continue

            cid = str(docid)
            rows.append({
                "case_id":       cid,
                "title":         m.get("title",""),
                "date":          m.get("publishdate",""),
                "bench":         ";".join(m.get("judges", [])),
                "citation_count":m.get("citationCount", 0),
                "verdict":       m.get("verdict",""),
                "description":   m.get("summary",""),
                "source_url":    m.get("sourceUrl","")
            })

            # write text
            with open(f"data/raw/{cid}.txt", "w", encoding="utf8") as f:
                f.write(txt)

            time.sleep(0.1)

        except Exception as e:
            print(f"Skipping {docid}: {e}")

    # 3) write CSV
    csv_path = "data/metadata/cases_metadata.csv"
    with open(csv_path, "w", newline="", encoding="utf8") as fout:
        writer = csv.DictWriter(fout, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Done: fetched {len(rows)} cases → data/raw + {csv_path}")

if __name__ == "__main__":
    main()

