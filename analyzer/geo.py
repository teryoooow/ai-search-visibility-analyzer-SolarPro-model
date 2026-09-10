"""
AI Search Visibility Analyzer - GEO Module
Analyzes Generative Engine Optimization signals.

Covers:
- Brand/entity citation potential (mentions in content)
- Entity authority signals (E-E-A-T proxies: author mentions, credentials, dates)
- Quotation and statistic density (LLM-citable content signals)
- Structured content for AI extraction (clear headings, concise paragraphs)
- Brand name mentions and domain authority proxies
- LLM readability (how easily an LLM can parse and cite the content)
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class GEOMetrics:
    """GEO analysis results for a URL."""
    url: str
    fetch_failed: bool = False
    domain: str = ""
    brand_name: str = ""
    brand_mentions: int = 0
    brand_mention_density: float = 0.0
    author_mentioned: bool = False
    author_name: str = ""
    date_published: str = ""
    has_author_box: bool = False
    credentials_signals: int = 0
    quote_count: int = 0
    quote_density: float = 0.0
    statistic_count: int = 0
    statistic_density: float = 0.0
    entity_coverage_score: float = 0.0
    llm_readability_score: float = 0.0
    content_structure_score: float = 0.0
    citation_potential_score: float = 0.0
    schema_present: bool = False
    word_count: int = 0
    overall_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "fetch_failed": self.fetch_failed,
            "domain": self.domain,
            "brand_name": self.brand_name,
            "brand_mentions": self.brand_mentions,
            "brand_mention_density": round(self.brand_mention_density, 2),
            "author_mentioned": self.author_mentioned,
            "author_name": self.author_name,
            "date_published": self.date_published,
            "has_author_box": self.has_author_box,
            "credentials_signals": self.credentials_signals,
            "quote_count": self.quote_count,
            "quote_density": round(self.quote_density, 2),
            "statistic_count": self.statistic_count,
            "statistic_density": round(self.statistic_density, 2),
            "entity_coverage_score": round(self.entity_coverage_score, 1),
            "llm_readability_score": round(self.llm_readability_score, 1),
            "content_structure_score": round(self.content_structure_score, 1),
            "citation_potential_score": round(self.citation_potential_score, 1),
            "schema_present": self.schema_present,
            "word_count": self.word_count,
            "overall_score": round(self.overall_score, 1),
        }


def fetch_page(url: str, timeout: int = 15) -> Optional[str]:
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


def extract_domain_authority(domain: str) -> int:
    score = 50
    tld_bonuses = {".edu": 30, ".gov": 30, ".org": 15, ".com": 10}
    for tld, bonus in tld_bonuses.items():
        if domain.endswith(tld):
            score += bonus
            break
    if len(domain) <= 10:
        score += 10
    elif len(domain) <= 20:
        score += 5
    return min(100, score)


def analyze_geo(url: str) -> GEOMetrics:
    metrics = GEOMetrics(url=url)

    html = fetch_page(url)
    if html is None:
        metrics.fetch_failed = True
        metrics.overall_score = 0.0
        return metrics

    soup = BeautifulSoup(html, "html.parser")
    body_text = soup.get_text(separator=" ", strip=True)
    words = body_text.split()
    word_count = len(words) if words else 1
    text_lower = body_text.lower()
    metrics.word_count = word_count

    parsed = urlparse(url)
    metrics.domain = parsed.netloc

    # Schema.org detection (early, used later)
    json_ld_scripts = soup.find_all("script", type="application/ld+json")
    metrics.schema_present = len(json_ld_scripts) > 0

    # ── Brand detection ──
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title_text = og_title["content"].strip()
    else:
        title_tag = soup.find("title")
        title_text = title_tag.get_text(strip=True) if title_tag else ""

    title_words = title_text.split()
    if title_words:
        prefix_words = {"the", "a", "an", "welcome", "home", "about", "contact"}
        for tw in title_words:
            if tw.lower() not in prefix_words and len(tw) > 2:
                metrics.brand_name = tw
                break
    if not metrics.brand_name:
        metrics.brand_name = parsed.netloc.replace("www.", "").split(".")[0]

    brand_lower = metrics.brand_name.lower()
    metrics.brand_mentions = len(re.findall(r'\b' + re.escape(brand_lower) + r'\b', text_lower))
    metrics.brand_mention_density = (metrics.brand_mentions / word_count) * 100

    # ── Author detection (E-E-A-T) ──
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string or "") if script.string else {}
            if isinstance(data, dict):
                author = data.get("author", {})
                if isinstance(author, dict):
                    name = author.get("name", "")
                    if name:
                        metrics.author_mentioned = True
                        metrics.author_name = name
                        metrics.credentials_signals += 2
                elif isinstance(author, str) and author:
                    metrics.author_mentioned = True
                    metrics.author_name = author
                    metrics.credentials_signals += 1
        except (json.JSONDecodeError, AttributeError, ValueError):
            continue

    byline_patterns = ["author", "byline", "written by", "posted by", "contributor"]
    for pattern in byline_patterns:
        elements = soup.find_all(attrs={"class": re.compile(pattern, re.I)})
        if elements:
            metrics.author_mentioned = True
            metrics.credentials_signals += 1
            break

    author_meta = soup.find("meta", attrs={"name": "author"})
    if author_meta and author_meta.get("content"):
        metrics.author_mentioned = True
        if not metrics.author_name:
            metrics.author_name = author_meta["content"]
        metrics.credentials_signals += 1

    # ── Date published ──
    date_meta = soup.find("meta", attrs={"property": "article:published_time"})
    if not date_meta:
        date_meta = soup.find("meta", attrs={"name": "date"})
    if not date_meta:
        date_el = soup.find("time")
        if date_el:
            date_meta = date_el
    if date_meta:
        date_content = ""
        if hasattr(date_meta, "get"):
            date_content = date_meta.get("content", "") or ""
        if not date_content and hasattr(date_meta, "get_text"):
            date_content = date_meta.get_text(strip=True)
        if date_content:
            metrics.date_published = date_content[:50]
            metrics.credentials_signals += 2

    author_boxes = soup.find_all(attrs={"class": re.compile(r"author|bio|profile|contributor", re.I)})
    metrics.has_author_box = len(author_boxes) > 0
    if metrics.has_author_box:
        metrics.credentials_signals += 2

    # ── Quotation density ──
    quotes = re.findall(r'"(?:[^"\n]{20,})"', body_text)
    metrics.quote_count = len(quotes)
    metrics.quote_density = (metrics.quote_count / word_count) * 100

    # ── Statistic density ──
    statistics = re.findall(
        r'\b\d+(?:\.\d+)?\s*(?:%|percent|kg|lb|ft|mile|km|dollar|\$|USD|'
        r'people|users|clients|customers|years|months|weeks|days|hours)\b',
        text_lower,
    )
    metrics.statistic_count = len(statistics)
    metrics.statistic_density = (metrics.statistic_count / word_count) * 100

    # ── Entity coverage score ──
    entity_score = 0.0
    if 0.5 <= metrics.brand_mention_density <= 3.0:
        entity_score += 25
    elif metrics.brand_mention_density > 0:
        entity_score += 15
    else:
        entity_score += 5

    if metrics.author_mentioned:
        entity_score += 20
    else:
        entity_score += 5

    if metrics.has_author_box:
        entity_score += 15

    entity_score += min(20, metrics.credentials_signals * 4)
    domain_auth = extract_domain_authority(metrics.domain)
    entity_score += domain_auth * 0.2

    metrics.entity_coverage_score = min(100.0, entity_score)

    # ── LLM readability score ──
    readability = 70.0

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p.split()) > 5]
    if paragraphs:
        avg_para_words = sum(len(p.split()) for p in paragraphs) / len(paragraphs)
        if avg_para_words <= 80:
            readability += 10
        elif avg_para_words <= 120:
            readability += 5
        else:
            readability -= 5

    heading_count = len(soup.find_all(["h1", "h2", "h3"]))
    if heading_count >= 5:
        readability += 10
    elif heading_count >= 3:
        readability += 5

    long_words = [w for w in words if len(w) > 8
                  and not w.endswith(("ing", "ed", "tion", "ness", "ment"))]
    jargon_ratio = len(long_words) / word_count if word_count > 0 else 0
    if jargon_ratio < 0.05:
        readability += 5
    elif jargon_ratio > 0.15:
        readability -= 10

    if 500 <= word_count <= 3000:
        readability += 5
    elif word_count < 200:
        readability -= 10

    metrics.llm_readability_score = min(100.0, max(0.0, readability))

    # ── Content structure score ──
    structure = 50.0
    list_count = len(soup.find_all(["ul", "ol"]))
    if list_count > 0:
        structure += 10

    table_count = len(soup.find_all("table"))
    if table_count > 0:
        structure += 10

    if heading_count >= 3:
        structure += 10
    if heading_count >= 6:
        structure += 10

    if word_count >= 300:
        structure += 5

    if metrics.schema_present:
        structure += 5

    metrics.content_structure_score = min(100.0, structure)

    # ── Citation potential score ──
    citation = 0.0
    citation += min(25, metrics.quote_density * 200)
    citation += min(25, metrics.statistic_density * 200)
    citation += min(20, metrics.entity_coverage_score * 0.2)
    citation += min(15, metrics.content_structure_score * 0.15)
    citation += min(15, metrics.llm_readability_score * 0.15)

    metrics.citation_potential_score = min(100.0, citation)

    # ── Overall GEO score ──
    weights = {
        "citation_potential_score": 0.35,
        "entity_coverage_score": 0.25,
        "llm_readability_score": 0.20,
        "content_structure_score": 0.20,
    }
    overall = sum(getattr(metrics, k) * w for k, w in weights.items())
    metrics.overall_score = round(overall, 1)

    return metrics


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python geo.py <URL>")
        sys.exit(1)
    result = analyze_geo(sys.argv[1])
    print(result.to_dict())
