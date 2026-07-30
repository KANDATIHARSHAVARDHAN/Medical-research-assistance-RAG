import requests
from typing import List, Dict, Any

class OpenFDALoader:
    """
    Ingestion loader for U.S. FDA Drug Labels via openFDA API.
    Fetches structured drug labeling, indications and usage, dosage, and safety guidelines.
    """
    def __init__(self):
        import os
        self.base_url = "https://api.fda.gov/drug/label.json"
        self.api_key = os.getenv("OPENFDA_API_KEY")

    def search_and_fetch(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        print(f"[OPENFDA LOADER] Searching openFDA Drug Labels for: '{query}' (max: {max_results})...")
        try:
            # Clean query term for openFDA Lucene syntax
            clean_term = query.replace(" ", "+")
            params = {
                "search": f"(openfda.brand_name:{clean_term} OR openfda.generic_name:{clean_term} OR indications_and_usage:{clean_term})",
                "limit": max_results
            }
            if self.api_key:
                params["api_key"] = self.api_key

            res = requests.get(self.base_url, params=params, timeout=15)
            if res.status_code == 404:
                print("[OPENFDA LOADER] No FDA labels matched query.")
                return []
            res.raise_for_status()
            data = res.json()
            results = data.get("results", [])

            documents = []
            for item in results:
                openfda = item.get("openfda", {})
                brand_names = openfda.get("brand_name", [])
                generic_names = openfda.get("generic_name", [])
                title = brand_names[0] if brand_names else (generic_names[0] if generic_names else "FDA Drug Label")
                if generic_names and brand_names:
                    title = f"{brand_names[0]} ({generic_names[0]})"

                manufacturers = openfda.get("manufacturer_name", ["U.S. Food and Drug Administration"])
                authors = manufacturers[0]

                indications = item.get("indications_and_usage", [])
                description = item.get("description", [])
                warnings = item.get("warnings_and_cautions", []) or item.get("warnings", [])

                summary_parts = []
                if indications:
                    summary_parts.append(f"INDICATIONS & USAGE: {indications[0]}")
                if warnings:
                    summary_parts.append(f"WARNINGS: {warnings[0][:500]}...")
                if not summary_parts and description:
                    summary_parts.append(description[0][:600])
                summary = "\n\n".join(summary_parts) if summary_parts else f"FDA-approved official product labeling and clinical prescribing guidelines for {title}."

                eff_time = str(item.get("effective_time", "20230101"))
                year_str = eff_time[:4]
                try:
                    year = int(year_str)
                except ValueError:
                    year = 2023

                spl_id = openfda.get("spl_id", [""])[0] or item.get("id", "")

                doc = {
                    "title": f"FDA Prescribing Information: {title}",
                    "authors": authors,
                    "journal": "FDA DailyMed Registry",
                    "year": year,
                    "pmid": "",
                    "doi": spl_id,
                    "study_type": "Clinical Guideline",
                    "source": "openFDA",
                    "chunk_text": summary,
                    "url": f"https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid={spl_id}" if spl_id else "https://open.fda.gov/"
                }
                documents.append(doc)
            print(f"[OPENFDA LOADER] Successfully fetched {len(documents)} drug label records.")
            return documents
        except Exception as e:
            print(f"[OPENFDA LOADER] Error fetching from openFDA API ({e}).")
            return []

openfda_loader = OpenFDALoader()
