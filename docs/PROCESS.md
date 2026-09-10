# AI Search Visibility Analyzer - Process Documentation

## Overview

This document describes the tool selection, architecture decisions, data extraction techniques, and prompt engineering strategies used in the AI Search Visibility Analyzer.

## 1. Tool Selection

### Why Python + Streamlit?

| Requirement | Choice | Rationale |
|-------------|--------|-----------|
| Core language | Python 3.11 | Rich ecosystem for web scraping, JSON parsing, HTTP requests. Dominant in AI/ML tooling. Free, open-source. |
| HTTP client | `requests` | Industry-standard, lightweight, no external dependencies beyond SSL. Free tier of any API works with it. |
| HTML parsing | `BeautifulSoup4` + `lxml` | Most forgiving parser for real-world HTML. Handles malformed markup gracefully. lxml backend for speed. |
| UI framework | `Streamlit` | Zero-boilerplate data app framework. Turns Python functions into a polished web UI in under 200 lines. Free, open-source, runs locally or on Streamlit Community Cloud. |
| CWV data | PageSpeed Insights API | Google's free API provides real Core Web Vitals (LCP, FID, CLS) from the Chrome User Experience Report and Lighthouse. No API key required for basic usage. |
| LLM insight | DeepSeek API (free tier) or heuristic fallback | DeepSeek provides a generous free tier for API access. When no key is configured, the tool falls back to a rule-based insight generator — so it always produces recommendations. |
| JSON handling | Standard library `json` | No external dependency needed. |
| Data models | `dataclasses` | Clean, typed data structures with built-in `to_dict()` serialization for export. |

### What was deliberately NOT used

- **Selenium/Playwright**: Unnecessary for this assessment. The target is static HTML analysis + API data, not JavaScript-rendered SPAs. Keeps the tool fast and dependency-light.
- **Paid SEO APIs (Moz, Ahrefs, SEMrush)**: Assessment requires free-tier only. Replaced with heuristic domain authority and real PageSpeed data.
- **Heavy ML frameworks (TensorFlow, PyTorch)**: The LLM insight is a single API call or heuristic rules — no model training or local inference needed.
- **Django/Flask**: Streamlit is simpler for a single-page analysis tool. No server routing or template management needed.

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                │
│  - URL input, Analyze button                            │
│  - Score cards (SEO / AEO / GEO)                        │
│  - Expandable metric tables                             │
│  - JSON export button                                   │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Analysis Orchestrator (app.py)             │
│  Calls each module in sequence, aggregates results      │
└───────┬────────────┬────────────┬──────────────────────┘
        │            │            │
┌───────▼───┐ ┌──────▼────┐ ┌────▼────────┐
│ SEO Module │ │ AEO Module │ │ GEO Module   │
│ (seo.py)   │ │ (aeo.py)  │ │ (geo.py)     │
└───────┬───┘ └─────┬─────┘ └────┬────────┘
        │            │            │
        ▼            ▼            ▼
┌─────────────────────────────────────────────────────────┐
│              Shared Infrastructure                       │
│  - fetch_page(): HTTP GET with realistic user-agent     │
│  - BeautifulSoup parsing                                │
│  - JSON-LD extraction                                   │
│  - Dataclass serialization (to_dict)                    │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. User enters URL in Streamlit UI → clicks Analyze
2. `app.py` calls `analyze_seo(url)`, `analyze_aeo(url)`, `analyze_geo(url)` in parallel (sequentially in v1, trivially parallelizable)
3. Each module:
   a. Fetches HTML via `fetch_page()` (shared helper with UA spoofing)
   b. Parses with BeautifulSoup
   c. Extracts domain-specific signals
   d. Computes weighted scores (0-100)
   e. Returns a `dataclass` with results
4. `app.py` renders score cards, metric tables, and export button
5. User can download full results as JSON

### Score Computation

Each module uses a weighted average of component scores:

**SEO** (9 components, weighted):
- Title tag (15%) — length 30-60 chars = optimal
- Meta description (15%) — length 100-160 chars = optimal
- H1 count (10%) — exactly 1 = optimal
- Readability (10%) — avg sentence length ≤20 = optimal
- Link ratio (10%) — 60-80% internal = optimal
- Alt coverage (10%) — ≥90% images with alt = optimal
- Canonical tag (10%) — present = 100
- Robots meta (5%) — noindex = 0, default = 100
- Core Web Vitals (15%) — from PageSpeed Insights API

**AEO** (4 components, weighted):
- Answer quality score (40%) — schema presence, FAQ/HowTo, question density, definition density, lists/tables
- Featured snippet signals (30%) — count of positive signals (FAQ schema, HowTo, questions, definitions, lists, tables, article schema)
- Schema presence (20%) — binary: any JSON-LD = 100, none = 0
- Question count (10%) — visible question marks and Q:/A: patterns

**GEO** (4 components, weighted):
- Citation potential (35%) — quote density, statistic density, entity coverage, structure, readability
- Entity coverage (25%) — brand mention density, author presence, bio box, credentials, domain authority
- LLM readability (20%) — paragraph length, heading structure, jargon density, content length
- Content structure (20%) — lists, tables, headings, word count, schema

## 3. Data Extraction Techniques

### Meta tags
```python
soup.find("meta", attrs={"name": "description"})
soup.find("meta", attrs={"name": "robots"})
soup.find("meta", property="og:title")
```

### Schema.org JSON-LD
```python
scripts = soup.find_all("script", type="application/ld+json")
for script in scripts:
    data = json.loads(script.string)
    # Walk @type fields, detect FAQPage, HowTo, Article, etc.
```

### Question detection
```python
# Question marks in text
questions = re.findall(r'[A-Z][^?]*\?', body_text)
# Q:/A: patterns
qa_pairs = re.findall(r'[Qq]\s*[:\.]\s*[A-Za-z]{10,}', body_text)
```

### Definition patterns
```python
definitions = re.findall(
    r'[A-Z][a-z]+ (?:is|refers to|means|describes|represents|known as)\s',
    body_text,
)
```

### Statistic detection
```python
statistics = re.findall(
    r'\b\d+(?:\.\d+)?\s*(?:%|percent|kg|lb|ft|mile|km|dollar|\$|USD|people|...)\b',
    text_lower,
)
```

### Core Web Vitals (PageSpeed Insights)
```python
psi_resp = requests.get(
    "https://www.googleapis.com/pagespeedonline/v5/runPagespeed",
    params={"url": url, "strategy": "desktop"},
    timeout=30,
)
# Extract LCP, FID, CLS from lighthouseResult.audits
```

### Author/E-E-A-T detection
- JSON-LD `author` field
- Meta `name="author"` tag
- CSS class patterns: `author`, `byline`, `written by`, `posted by`, `contributor`
- Author bio box detection via class regex

### Brand detection
- Prefer `og:title` → fallback to `<title>` → fallback to domain
- Strip common prefix words (the, a, an, welcome, home, about, contact)
- First significant word = brand name

## 4. Prompt Engineering Strategy

The LLM insight component uses a structured prompt designed to produce actionable, domain-specific recommendations:

**Prompt template:**
```
You are a search visibility expert analyzing a website's performance across three domains:
SEO (traditional search), AEO (answer engines/featured snippets), and GEO (generative AI citability).

Here are the metrics:
{scored metrics from all three modules}

Based on these metrics, provide:
1. A one-paragraph executive summary (3-4 sentences)
2. The single highest-impact improvement for each domain (SEO, AEO, GEO)
3. One cross-cutting recommendation that improves multiple domains simultaneously

Keep it concise. Use specific numbers from the metrics. Avoid generic advice like "improve your SEO."
```

**Design decisions:**
- Temperature: 0.3 (low creativity, high consistency — this is analysis, not creative writing)
- The prompt includes actual metric values so the LLM grounds its recommendations in data
- Forces structured output (summary + 3 recommendations) rather than free-form text
- Cross-cutting recommendation forces the model to find synergies (e.g., adding FAQ schema improves both AEO and GEO)

**Fallback (no API key):**
When no DeepSeek key is configured, a heuristic generator produces similar structured output using the same metric values. It identifies the weakest domain and provides specific, rule-based recommendations tied to the actual scores.

## 5. Error Handling

- **Network errors**: Each module catches `requests.RequestException` and returns a zeroed Result with `page_status=0`. The UI shows an error message.
- **Missing elements**: BeautifulSoup returns `None` for missing tags — each analyzer checks for `None` before accessing attributes.
- **Invalid JSON-LD**: Each script is parsed in a try/except — malformed scripts are skipped, valid ones are processed.
- **PageSpeed API failures**: CWV data is marked as unavailable (`cwvs_fetched=False`), score defaults to neutral (50/100).
- **Missing brand name**: Falls back to domain-based extraction.

## 6. Limitations

- **JavaScript-rendered content**: The tool fetches static HTML only. Client-side rendered pages (SPAs) may have incomplete data. A production version could add Playwright as an optional backend.
- **PageSpeed API rate limits**: Unauthenticated requests have rate limits. CWV data may not be available for every request.
- **Domain authority**: The current implementation uses simple TLD/length heuristics, not a real authority metric. A production version would integrate Moz/Ahrefs API (free tiers available) or use backlink count from search.
- **Brand detection**: Heuristic-based (first significant word in title). May misidentify brands with generic names.
- **Language**: Optimized for English-language content. Statistic and question patterns assume English formatting.

## 7. Dependencies

```
requests>=2.31.0       # HTTP client
beautifulsoup4>=4.12.0 # HTML parsing
lxml>=4.9.0            # Fast HTML parser backend
streamlit>=1.28.0      # Web UI framework
```
