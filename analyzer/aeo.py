"""
AI Search Visibility Analyzer - AEO Module
Analyzes Answer Engine Optimization signals.

Covers:
- Schema.org structured data (JSON-LD) presence and type coverage
- FAQPage, HowTo, Article schema detection
- Q&A content patterns (question-answer formatting)
- Featured snippet readiness signals
- Direct answer extractability from content
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class AEOMetrics:
    """AEO analysis results for a URL."""
    url: str
    schema_present: bool = False
    schema_types: List[str] = field(default_factory=list)
    has_faq_schema: bool = False
    faq_count: int = 0
    has_howto_schema: bool = False
    howto_count: int = 0
    has_article_schema: bool = False
    has_product_schema: bool = False
    has_local_business_schema: bool = False
    question_count: int = 0  # Visible question patterns in text
    answer_quality_score: float = 0.0
    definition_count: int = 0  # "X is..." pattern density
    list_present: bool = False
    table_present: bool = False
    featured_snippet_signals: int = 0
    overall_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "schema_present": self.schema_present,
            "schema_types": self.schema_types,
            "has_faq_schema": self.has_faq_schema,
            "faq_count": self.faq_count,
            "has_howto_schema": self.has_howto_schema,
            "howto_count": self.howto_count,
            "has_article_schema": self.has_article_schema,
            "has_product_schema": self.has_product_schema,
            "has_local_business_schema": self.has_local_business_schema,
            "question_count": self.question_count,
            "answer_quality_score": round(self.answer_quality_score, 1),
            "definition_count": self.definition_count,
            "list_present": self.list_present,
            "table_present": self.table_present,
            "featured_snippet_signals": self.featured_snippet_signals,
            "overall_score": round(self.overall_score, 1),
        }


def fetch_page(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch HTML content from a URL."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException:
        return None


def extract_json_ld(soup: BeautifulSoup) -> List[dict]:
    """Extract all JSON-LD structured data from the page."""
    scripts = soup.find_all("script", type="application/ld+json")
    results = []
    for script in scripts:
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                results.append(data)
            elif isinstance(data, list):
                results.extend(data)
        except (json.JSONDecodeError, AttributeError):
            continue
    return results


def analyze_aeo(url: str) -> AEOMetrics:
    """Run full AEO analysis on a URL."""
    metrics = AEOMetrics(url=url)

    html = fetch_page(url)
    if html is None:
        metrics.overall_score = 0.0
        return metrics

    soup = BeautifulSoup(html, "html.parser")
    body_text = soup.get_text(separator=" ", strip=True)
    text_lower = body_text.lower()

    # ── Schema.org detection ──
    json_ld_data = extract_json_ld(soup)
    metrics.schema_present = len(json_ld_data) > 0

    all_types = set()
    for entry in json_ld_data:
        schema_type = entry.get("@type", "")
        if isinstance(schema_type, str):
            all_types.add(schema_type.lower())
            if schema_type.lower() == "faqpage":
                metrics.has_faq_schema = True
            elif schema_type.lower() == "howto":
                metrics.has_howto_schema = True
            elif schema_type.lower() == "article":
                metrics.has_article_schema = True
            elif schema_type.lower() == "product":
                metrics.has_product_schema = True
            elif schema_type.lower() == "localbusiness":
                metrics.has_local_business_schema = True
        elif isinstance(schema_type, list):
            for t in schema_type:
                all_types.add(t.lower())
                if t.lower() == "faqpage":
                    metrics.has_faq_schema = True
                elif t.lower() == "howto":
                    metrics.has_howto_schema = True
                elif t.lower() == "article":
                    metrics.has_article_schema = True
                elif t.lower() == "product":
                    metrics.has_product_schema = True
                elif t.lower() == "localbusiness":
                    metrics.has_local_business_schema = True

    metrics.schema_types = sorted(all_types)

    # FAQ count from schema
    for entry in json_ld_data:
        if entry.get("@type", "").lower() == "faqpage":
            main_entity = entry.get("mainEntity", [])
            if isinstance(main_entity, list):
                metrics.faq_count += len(main_entity)
            elif isinstance(main_entity, dict):
                metrics.faq_count += 1

    # HowTo count from schema
    for entry in json_ld_data:
        if entry.get("@type", "").lower() == "howto":
            steps = entry.get("step", [])
            if isinstance(steps, list):
                metrics.howto_count += len(steps)
            else:
                metrics.howto_count += 1

    # ── Question patterns in visible text ──
    # Count FAQ-like patterns: questions ending with ?
    questions = re.findall(r'[A-Z][^?]*\?', body_text)
    metrics.question_count = len(questions)

    # Also detect Q: / A: patterns
    qa_pairs = re.findall(r'[Qq]\s*[:\.]\s*[A-Za-z]{10,}', body_text)
    metrics.question_count += len(qa_pairs)

    # ── Definition patterns ("X is...", "X refers to...") ──
    definitions = re.findall(
        r'[A-Z][a-z]+ (?:is|refers to|means|describes|represents|known as)\s',
        body_text,
    )
    metrics.definition_count = len(definitions)

    # ── Featured snippet signals ──
    # Lists
    lists = soup.find_all(["ul", "ol"])
    metrics.list_present = len(lists) > 0

    # Tables
    tables = soup.find_all("table")
    metrics.table_present = len(tables) > 0

    # Count strong snippet signals
    signals = 0
    if metrics.has_faq_schema:
        signals += 3
    if metrics.has_howto_schema:
        signals += 2
    if metrics.schema_present:
        signals += 1
    if metrics.question_count >= 3:
        signals += 2
    if metrics.definition_count >= 2:
        signals += 1
    if metrics.list_present:
        signals += 1
    if metrics.table_present:
        signals += 1
    if metrics.has_article_schema:
        signals += 1

    metrics.featured_snippet_signals = signals

    # ── Answer quality score ──
    # Based on: question density, definition density, structured data, lists/tables
    aeo_components = {
        "schema_bonus": 30.0 if metrics.schema_present else 0.0,
        "faq_bonus": 20.0 if metrics.has_faq_schema else 0.0,
        "howto_bonus": 15.0 if metrics.has_howto_schema else 0.0,
        "question_density": min(15.0, metrics.question_count * 3),
        "definition_density": min(10.0, metrics.definition_count * 5),
        "list_signal": 5.0 if metrics.list_present else 0.0,
        "table_signal": 5.0 if metrics.table_present else 0.0,
    }
    metrics.answer_quality_score = sum(aeo_components.values())
    metrics.answer_quality_score = min(100.0, metrics.answer_quality_score)

    # ── Overall AEO score ──
    weights = {
        "answer_quality_score": 0.40,
        "featured_snippet_signals": 0.30,
        "schema_present_score": 0.20,
        "question_count_score": 0.10,
    }
    schema_present_score = 100.0 if metrics.schema_present else 0.0
    question_count_score = min(100.0, metrics.question_count * 10)

    overall = (
        metrics.answer_quality_score * weights["answer_quality_score"] +
        (metrics.featured_snippet_signals / 10.0 * 100) * weights["featured_snippet_signals"] +
        schema_present_score * weights["schema_present_score"] +
        question_count_score * weights["question_count_score"]
    )
    metrics.overall_score = round(min(100.0, overall), 1)

    return metrics


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python aeo.py <URL>")
        sys.exit(1)
    result = analyze_aeo(sys.argv[1])
    print(result.to_dict())
