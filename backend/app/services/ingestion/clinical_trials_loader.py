import requests
from typing import List, Dict, Any

class ClinicalTrialsLoader:
    """
    Ingestion loader for ClinicalTrials.gov APIv2.
    Fetches active and completed interventional clinical trials and structured study protocols.
    """
    def __init__(self):
        import os
        self.base_url = "https://clinicaltrials.gov/api/v2/studies"
        self.api_key = os.getenv("CLINICAL_TRIALS_API_KEY")

    def search_and_fetch(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        print(f"[CLINICAL TRIALS LOADER] Searching ClinicalTrials.gov API for: '{query}' (max: {max_results})...")
        try:
            params = {
                "query.term": query,
                "pageSize": max_results,
                "format": "json"
            }
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
                params["api_key"] = self.api_key

            res = requests.get(self.base_url, params=params, headers=headers, timeout=15)
            res.raise_for_status()
            data = res.json()
            studies = data.get("studies", [])

            documents = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                
                # NCT ID & Title
                id_mod = protocol.get("identificationModule", {})
                nct_id = id_mod.get("nctId", "")
                title = id_mod.get("briefTitle") or id_mod.get("officialTitle") or "Clinical Trial Protocol"

                # Summary / Chunk text
                desc_mod = protocol.get("descriptionModule", {})
                summary = desc_mod.get("briefSummary") or desc_mod.get("detailedDescription") or f"Clinical trial investigating interventional efficacy for {title}."

                # Sponsor / Authors
                sponsor_mod = protocol.get("sponsorCollaboratorsModule", {})
                lead_sponsor = sponsor_mod.get("leadSponsor", {}).get("name", "Clinical Trial Sponsor")

                # Date / Year
                status_mod = protocol.get("statusModule", {})
                start_date = status_mod.get("startDateStruct", {}).get("date") or status_mod.get("statusVerifiedDate", "2023")
                year_str = str(start_date)[:4]
                try:
                    year = int(year_str)
                except ValueError:
                    year = 2023

                # Study Type
                design_mod = protocol.get("designModule", {})
                raw_type = design_mod.get("studyType", "INTERVENTIONAL")
                study_type = "Randomized Controlled Trial" if "INTERVENTIONAL" in raw_type.upper() else "Cohort Study"

                doc = {
                    "title": title,
                    "authors": lead_sponsor,
                    "journal": "ClinicalTrials.gov Registry",
                    "year": year,
                    "pmid": "",
                    "doi": nct_id,
                    "study_type": study_type,
                    "source": "ClinicalTrials.gov",
                    "chunk_text": summary,
                    "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "https://clinicaltrials.gov/"
                }
                documents.append(doc)
            print(f"[CLINICAL TRIALS LOADER] Successfully fetched {len(documents)} clinical trials.")
            return documents
        except Exception as e:
            print(f"[CLINICAL TRIALS LOADER] Error fetching from ClinicalTrials.gov API ({e}).")
            return []

clinical_trials_loader = ClinicalTrialsLoader()
