# AI Search Visibility Analyzer

**Live demo:** [Streamlit Cloud deployment — link coming up 👇]

A unified web app that audits any URL across three search paradigms — **SEO** (traditional search ranking), **AEO** (answer engine/featured snippet readiness), and **GEO** (generative AI/LLM citation potential) — and returns actionable recommendations.

Built with **Python + Streamlit**. Free-tier infrastructure: requests + BeautifulSoup for HTML analysis, Google PageSpeed Insights API for Core Web Vitals, and optional DeepSeek LLM insight with a heuristic fallback that always works without an API key.

## 📊 What It Measures

| Domain | Focus | Key Signals |
|--------|-------|-------------|
| **SEO** | Traditional search ranking | Title tag, meta description, H1/H2 structure, readability, link ratio, alt text coverage, canonical tag, robots meta, Core Web Vitals (LCP/FID/CLS) |
| **AEO** | Answer engine extraction | Schema.org JSON-LD presence, FAQPage/HowTo schema, visible question count, definition patterns, list/table presence, featured snippet readiness |
| **GEO** | Generative AI citability | Brand/entity mention density, author E-E-A-T signals, quote density, statistic density, LLM readability, content structure, citation potential score |

## 🚀 Quick Start (Local)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501, enter any URL, and click **Analyze**.

## 📁 Project Structure

```
ai-search-visibility-analyzer/
├── app.py                    # Streamlit web UI with score cards + JSON export
├── requirements.txt          # Python dependencies (requests, BeautifulSoup, lxml, Streamlit)
├── analyzer/
│   ├── __init__.py
│   ├── seo.py               # SEO analysis engine (full on-page + CWV)
│   ├── aeo.py               # AEO analysis engine (Schema.org + Q&A + snippet signals)
│   └── geo.py               # GEO analysis engine (entity + author + quotes + stats)
├── insights/
│   └── llm_insight.py       # DeepSeek LLM insight + heuristic fallback (no key needed)
└── docs/
    ├── PROCESS.md           # Tool selection, architecture, data extraction, prompt engineering
    ├── BUSINESS_VALUE.md    # Business case, target personas, competitive differentiation
    └── ROADMAP.md           # 5 prioritized future upgrades
```

## 📄 Documentation

- [`docs/PROCESS.md`](docs/PROCESS.md) — Tool selection rationale, system architecture diagram, data extraction techniques (regex patterns, DOM selectors), prompt engineering strategy for LLM insight, error handling, known limitations
- [`docs/BUSINESS_VALUE.md`](docs/BUSINESS_VALUE.md) — Business case for unified SEO/AEO/GEO analysis, target user personas, competitive differentiation vs. enterprise SEO platforms, business impact, monetization pathways
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — Five prioritized future upgrades: multi-URL batch mode, competitor benchmarking, automated remediation scripts, historical tracking dashboard, Notion + n8n integration

## 🧠 LLM Insight

When a DeepSeek API key is configured (`DEEPSEEK_API_KEY` environment variable), the app generates a strategic insight synthesizing strengths, gaps, and prioritized recommendations across all three domains. Without a key, it falls back to a transparent heuristic summary built from the same metric values — so the tool always produces insights.

## 📥 Export

Click the **Download JSON** button in the UI to export the full analysis as structured JSON — usable for reporting, Notion integration, or automated audit pipelines.

## License

MIT
