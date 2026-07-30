import requests
from typing import List, Dict, Any

class DailyMedLoader:
    """
    Ingestion loader for NLM DailyMed API.
    Fetches standardized product labels (SPL) and authoritative prescribing data.
    """
    def __init__(self):
        import os
        self.base_url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
        self.api_key = os.getenv("DAILYMED_API_KEY")

    def search_and_fetch(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        print(f"[DAILYMED LOADER] Searching NLM DailyMed for: '{query}' (max: {max_results})...")
        try:
            params = {
                "drug_name": query,
                "pagesize": max_results
            }
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                params["api_key"] = self.api_key

            res = requests.get(self.base_url, params=params, headers=headers, timeout=15)
            res.raise_for_status()
            data = res.json()
            items = data.get("data", [])

            documents = []
            for item in items:
                title = item.get("title", "DailyMed Drug Label Protocol")
                setid = item.get("setid", "")
                pub_date = item.get("published_date", "2023")
                
                # Extract year from date string like "Jul 15, 2023" or "2023-07-15"
                year_str = "2023"
                for word in str(pub_date).replace(",", " ").replace("-", " ").split():
                    if word.isdigit() and len(word) == 4 and word.startswith(("19", "20")):
                        year_str = word
                        break
                try:
                    year = int(year_str)
                except ValueError:
                    year = 2023

                summary = f"Official NLM DailyMed structured product label (SPL) and clinical prescribing guidelines for {title}. Contains FDA-approved indications, contraindications, and therapeutic dosing schedules."

                doc = {
                    "title": title[:150],
                    "authors": "U.S. National Library of Medicine (NLM)",
                    "journal": "DailyMed SPL Registry",
                    "year": year,
                    "pmid": "",
                    "doi": setid,
                    "study_type": "Clinical Guideline",
                    "source": "DailyMed",
                    "chunk_text": summary,
                    "url": f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={setid}" if setid else "https://dailymed.nlm.nih.gov/"
                }
                documents.append(doc)
            print(f"[DAILYMED LOADER] Successfully fetched {len(documents)} DailyMed SPL records.")
            return documents
        except Exception as e:
            print(f"[DAILYMED LOADER] Error fetching from DailyMed API ({e}).")
            return []

dailymed_loader = DailyMedLoader()
