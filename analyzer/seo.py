"""
AI Search Visibility Analyzer - SEO Module
Analyzes traditional search engine optimization signals.

Covers:
- Meta tags (title, description, robots, canonical)
- Content structure (headings, word count, readability)
- Link profile (internal/external ratio)
- Image optimization (alt text coverage)
- Core Web Vitals via PageSpeed Insights API (free tier)
- Crawlability signals (robots meta, canonical, status codes)
"""

import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class SEOMetrics:
    """SEO analysis results for a URL."""
    url: str
    title: str = ""
    title_length: int = 0
    title_score: float = 0.0
    meta_description: str = ""
    meta_description_length: int = 0
    meta_description_score: float = 0.0
    h1_count: int = 0
    h1_score: float = 0.0
    h2_count: int = 0
    word_count: int = 0
    readability_score: float = 0.0
    internal_links: int = 0
    external_links: int = 0
    link_ratio_score: float = 0.0
    images_with_alt: int = 0
    images_total: int = 0
    alt_coverage_score: float = 0.0
    canonical_present: bool = False
    canonical_score: float = 0.0
    robots_meta: str = ""
    robots_score: float = 0.0
    page_status: int = 0
    cwvs_fetched: bool = False
    lcp: Optional[float] = None
    fid: Optional[float] = None
    cls: Optional[float] = None
    cwvs_score: float = 0.0
    overall_score: float = 0.0

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "title_length": self.title_length,
            "title_score": round(self.title_score, 1),
            "meta_description": (self.meta_description[:100] + "...")
                                if len(self.meta_description) > 100 else self.meta_description,
            "meta_description_length": self.meta_description_length,
            "meta_description_score": round(self.meta_description_score, 1),
            "h1_count": self.h1_count,
            "h1_score": round(self.h1_score, 1),
            "h2_count": self.h2_count,
            "word_count": self.word_count,
            "readability_score": round(self.readability_score, 1),
            "internal_links": self.internal_links,
            "external_links": self.external_links,
            "link_ratio_score": round(self.link_ratio_score, 1),
            "images_with_alt": self.images_with_alt,
            "images_total": self.images_total,
            "alt_coverage_score": round(self.alt_coverage_score, 1),
            "canonical_present": self.canonical_present,
            "canonical_score": round(self.canonical_score, 1),
            "robots_meta": self.robots_meta,
            "robots_score": round(self.robots_score, 1),
            "page_status": self.page_status,
            "cwvs_fetched": self.cwvs_fetched,
            "lcp": self.lcp,
            "fid": self.fid,
            "cls": self.cls,
            "cwvs_score": round(self.cwvs_score, 1),
            "overall_score": round(self.overall_score, 1),
        }


def fetch_page(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch HTML content from a URL with a realistic user-agent."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException:
        return None


def analyze_seo(url: str) -> SEOMetrics:
    """Run full SEO analysis on a URL."""
    metrics = SEOMetrics(url=url)

    html = fetch_page(url)
    if html is None:
        metrics.page_status = 0
        metrics.overall_score = 0.0
        return metrics

    # Get final status code
    try:
        resp = requests.get(url, timeout=15, allow_redirects=True)
        metrics.page_status = resp.status_code
    except Exception:
        metrics.page_status = 0

    if metrics.page_status != 200:
        metrics.overall_score = 0.0
        return metrics

    soup = BeautifulSoup(html, "html.parser")
    base_domain = urlparse(url).netloc.lower()

    # Title tag
    title_tag = soup.find("title")
    if title_tag:
        metrics.title = title_tag.get_text(strip=True)
        metrics.title_length = len(metrics.title)
        if 30 <= metrics.title_length <= 60:
            metrics.title_score = 100.0
        elif metrics.title_length == 0:
            metrics.title_score = 0.0
        elif metrics.title_length < 30:
            metrics.title_score = 50.0
        else:
            metrics.title_score = 70.0

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        metrics.meta_description = desc_tag["content"].strip()
        metrics.meta_description_length = len(metrics.meta_description)
        if 100 <= metrics.meta_description_length <= 160:
            metrics.meta_description_score = 100.0
        elif metrics.meta_description_length == 0:
            metrics.meta_description_score = 0.0
        elif metrics.meta_description_length < 100:
            metrics.meta_description_score = 60.0
        else:
            metrics.meta_description_score = 75.0
    else:
        metrics.meta_description_score = 0.0

    # Headings
    h1_tags = soup.find_all("h1")
    metrics.h1_count = len(h1_tags)
    if metrics.h1_count == 1:
        metrics.h1_score = 100.0
    elif metrics.h1_count == 0:
        metrics.h1_score = 20.0
    else:
        metrics.h1_score = max(0, 100 - (metrics.h1_count - 1) * 25)

    h2_tags = soup.find_all("h2")
    metrics.h2_count = len(h2_tags)

    # Word count and readability
    body_text = soup.get_text(separator=" ", strip=True)
    words = body_text.split()
    metrics.word_count = len(words)

    sentences = re.split(r'[.!?]+', body_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_sentence_len <= 20:
            metrics.readability_score = 100.0
        elif avg_sentence_len <= 30:
            metrics.readability_score = 80.0
        elif avg_sentence_len <= 40:
            metrics.readability_score = 60.0
        else:
            metrics.readability_score = 40.0
    else:
        metrics.readability_score = 0.0

    # Links
    links = soup.find_all("a", href=True)
    internal = 0
    external = 0
    for link in links:
        href = link["href"].lower()
        if href.startswith(("http", "https")):
            link_domain = urlparse(href).netloc.lower()
            if link_domain == base_domain or link_domain.endswith("." + base_domain):
                internal += 1
            else:
                external += 1
        else:
            internal += 1

    metrics.internal_links = internal
    metrics.external_links = external
    total_links = internal + external
    if total_links > 0:
        ratio = internal / total_links
        if 0.6 <= ratio <= 0.8:
            metrics.link_ratio_score = 100.0
        elif ratio > 0.8:
            metrics.link_ratio_score = 70.0
        else:
            metrics.link_ratio_score = 50.0
    else:
        metrics.link_ratio_score = 0.0

    # Images / alt text
    images = soup.find_all("img")
    metrics.images_total = len(images)
    metrics.images_with_alt = sum(1 for img in images if img.get("alt"))
    if metrics.images_total > 0:
        coverage = metrics.images_with_alt / metrics.images_total
        if coverage >= 0.9:
            metrics.alt_coverage_score = 100.0
        elif coverage >= 0.7:
            metrics.alt_coverage_score = 80.0
        elif coverage >= 0.5:
            metrics.alt_coverage_score = 60.0
        else:
            metrics.alt_coverage_score = 30.0
    else:
        metrics.alt_coverage_score = 100.0

    # Canonical
    canonical_tag = soup.find("link", rel="canonical")
    metrics.canonical_present = canonical_tag is not None
    metrics.canonical_score = 100.0 if metrics.canonical_present else 0.0

    # Robots meta
    robots_tag = soup.find("meta", attrs={"name": "robots"})
    if robots_tag and robots_tag.get("content"):
        metrics.robots_meta = robots_tag["content"].lower()
        if "noindex" in metrics.robots_meta:
            metrics.robots_score = 0.0
        elif "nofollow" in metrics.robots_meta:
            metrics.robots_score = 50.0
        else:
            metrics.robots_score = 100.0
    else:
        metrics.robots_score = 100.0

    # Core Web Vitals via PageSpeed Insights API
    try:
        psi_resp = requests.get(
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
            params={"url": url, "strategy": "desktop"},
            timeout=30,
        )
        if psi_resp.status_code == 200:
            psi_data = psi_resp.json()
            lr = psi_data.get("lighthouseResult", {})
            audits = lr.get("audits", {})

            lcp_data = audits.get("largest-contentful-paint", {})
            fid_data = audits.get("first-input-delay", {})
            cls_data = audits.get("cumulative-layout-shift", {})

            metrics.lcp = lcp_data.get("numericValue")
            metrics.fid = fid_data.get("numericValue")
            metrics.cls = cls_data.get("numericValue")
            metrics.cwvs_fetched = True

            cwvs_score = 100.0
            if metrics.lcp and metrics.lcp > 2500:
                cwvs_score -= 25
            if metrics.fid and metrics.fid > 100:
                cwvs_score -= 25
            if metrics.cls and metrics.cls > 0.1:
                cwvs_score -= 25
            metrics.cwvs_score = max(0, cwvs_score)
    except Exception:
        metrics.cwvs_fetched = False
        metrics.cwvs_score = 50.0

    # Overall SEO score (weighted average)
    weights = {
        "title_score": 0.15,
        "meta_description_score": 0.15,
        "h1_score": 0.10,
        "readability_score": 0.10,
        "link_ratio_score": 0.10,
        "alt_coverage_score": 0.10,
        "canonical_score": 0.10,
        "robots_score": 0.05,
        "cwvs_score": 0.15,
    }
    overall = sum(getattr(metrics, k) * w for k, w in weights.items())
    metrics.overall_score = round(overall, 1)

    return metrics


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python seo.py <URL>")
        sys.exit(1)
    result = analyze_seo(sys.argv[1])
    print(result.to_dict())
