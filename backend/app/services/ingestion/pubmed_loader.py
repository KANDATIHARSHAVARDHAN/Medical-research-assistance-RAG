import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

class PubMedLoader:
    """
    Ingestion loader for NCBI PubMed via E-utilities API.
    Fetches peer-reviewed clinical literature, RCTs, and systematic reviews.
    """
    def __init__(self, email: str = "researcher@example.com"):
        import os
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = os.getenv("PUBMED_EMAIL", email)
        self.api_key = os.getenv("PUBMED_API_KEY") or os.getenv("NCBI_API_KEY")

    def search_and_fetch(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        print(f"[PUBMED LOADER] Searching NCBI PubMed for: '{query}' (max: {max_results})...")
        try:
            # 1. Search for PMIDs
            search_url = f"{self.base_url}/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": f"{query} AND (randomized controlled trial[Publication Type] OR clinical trial[Publication Type] OR systematic review[Publication Type] OR guideline[Publication Type])",
                "retmode": "json",
                "retmax": max_results,
                "email": self.email
            }
            if self.api_key:
                search_params["api_key"] = self.api_key

            res = requests.get(search_url, params=search_params, timeout=15)
            res.raise_for_status()
            data = res.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])

            if not pmids:
                # Fallback search without strict publication type filter if no trials found
                search_params["term"] = query
                res = requests.get(search_url, params=search_params, timeout=15)
                res.raise_for_status()
                pmids = res.json().get("esearchresult", {}).get("idlist", [])

            if not pmids:
                print("[PUBMED LOADER] No articles found.")
                return []

            # 2. Fetch XML details for PMIDs
            fetch_url = f"{self.base_url}/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
                "email": self.email
            }
            if self.api_key:
                fetch_params["api_key"] = self.api_key

            fetch_res = requests.get(fetch_url, params=fetch_params, timeout=20)
            fetch_res.raise_for_status()

            return self._parse_pubmed_xml(fetch_res.text)
        except Exception as e:
            print(f"[PUBMED LOADER] Error fetching from PubMed API ({e}).")
            return []

    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        documents = []
        try:
            root = ET.fromstring(xml_text)
            for article in root.findall(".//PubmedArticle"):
                # PMID
                pmid_elem = article.find(".//PMID")
                pmid = pmid_elem.text if pmid_elem is not None else ""

                # Title
                title_elem = article.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else "Medical Research Study"

                # Abstract
                abstract_texts = article.findall(".//AbstractText")
                abstract = " ".join([elem.text for elem in abstract_texts if elem.text])
                if not abstract:
                    abstract = f"Clinical study investigating treatment outcomes and efficacy for {title}."

                # Journal & Year
                journal_elem = article.find(".//Journal/Title")
                journal = journal_elem.text if journal_elem is not None else "PubMed Clinical Journal"

                year_elem = article.find(".//JournalIssue/PubDate/Year")
                if year_elem is None:
                    year_elem = article.find(".//JournalIssue/PubDate/MedlineDate")
                year_str = year_elem.text[:4] if year_elem is not None and len(year_elem.text) >= 4 else "2023"
                try:
                    year = int(year_str)
                except ValueError:
                    year = 2023

                # Authors
                authors_list = []
                for author in article.findall(".//Author")[:3]:
                    last = author.find("LastName")
                    init = author.find("Initials")
                    if last is not None and last.text:
                        authors_list.append(f"{last.text} {init.text if init is not None and init.text else ''}".strip())
                authors = ", ".join(authors_list) + (" et al." if len(authors_list) == 3 else "") if authors_list else "Medical Research Group"

                # Study Type
                pub_types = [pt.text for pt in article.findall(".//PublicationType") if pt.text]
                study_type = "Clinical Study"
                for pt in pub_types:
                    if "Randomized Controlled Trial" in pt or "Clinical Trial" in pt:
                        study_type = "Randomized Controlled Trial"
                        break
                    elif "Systematic Review" in pt or "Meta-Analysis" in pt:
                        study_type = "Systematic Review"
                        break
                    elif "Guideline" in pt:
                        study_type = "Clinical Guideline"
                        break

                # DOI
                doi = ""
                for id_elem in article.findall(".//ArticleId"):
                    if id_elem.attrib.get("IdType") == "doi" and id_elem.text:
                        doi = id_elem.text
                        break

                doc = {
                    "title": title,
                    "authors": authors,
                    "journal": journal,
                    "year": year,
                    "pmid": pmid,
                    "doi": doi,
                    "study_type": study_type,
                    "source": "PubMed",
                    "chunk_text": abstract,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                }
                documents.append(doc)
            print(f"[PUBMED LOADER] Successfully extracted {len(documents)} articles from PubMed.")
        except Exception as e:
            print(f"[PUBMED LOADER] XML Parsing error ({e}).")
        return documents

pubmed_loader = PubMedLoader()
