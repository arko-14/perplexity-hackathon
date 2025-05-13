import requests
from bs4 import BeautifulSoup
import json

base_url = "https://indiankanoon.org/browse/supremecourt/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

case_list = []

for page in range(1, 101):
    url = f"{base_url}?page={page}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    cases = soup.find_all("a", href=True)
    for case in cases:
        href = case['href']
        if href.startswith("/doc/"):
            case_info = {
                "title": case.text.strip(),
                "link": f"https://indiankanoon.org{href}"
            }
            case_list.append(case_info)

# Save to JSON file
with open("supreme_court_cases.json", "w", encoding="utf-8") as f:
    json.dump(case_list, f, ensure_ascii=False, indent=2) 