# Product Roadmap — AI Search Visibility Analyzer

## v1.0 (Current) — Single URL Analysis
- SEO, AEO, GEO scoring for a single URL
- Streamlit UI with score cards, metrics tables, and JSON export
- Core Web Vitals via PageSpeed Insights API (free tier)
- Heuristic insight generator + optional DeepSeek LLM integration
- All free-tier infrastructure, no API keys required

---

## v1.1 — Multi-URL Batch Analysis
**Priority: High**

The single biggest request for v1 will be analyzing multiple URLs at once — agencies and consultants need to audit 10-50 client pages in one go.

**Features:**
- CSV upload or text area with one URL per line
- Batch processing queue with progress indicator
- Summary table: all URLs ranked by each score, sortable columns
- Per-URL detail expansion (same detail as single-URL view)
- Batch export: single JSON/CSV with all results
- Rate limiting awareness: sequential fetching with configurable delay to respect API limits

**Business value:** This turns the tool from a demo into a real workflow tool for consultants and agencies. A consultant can audit 20 client pages in 5 minutes instead of 20 separate single analyses.

**Implementation approach:**
- Reuse existing analyze functions — each URL is independent
- Add a batch processing wrapper that iterates URLs with a progress bar
- Store results in a list, render as a sortable table with expandable rows

---

## v1.2 — Competitor Benchmarking
**Priority: Medium-High**

Comparing your scores against competitors is the natural next step after batch analysis. If you score 65/100 on SEO and your top competitor scores 82/100, you know exactly how much ground you need to cover.

**Features:**
- Add competitor URLs alongside your own in the batch interface
- Side-by-side comparison view: your scores vs. competitor average
- Gap analysis: "You're 15 points behind on AEO — here's what that gap consists of"
- Visual comparison charts (bar charts for each domain score)
- Export: comparison report with relative positioning

**Business value:** Competitive context transforms raw scores into strategy. A 40/100 AEO score is bad in isolation — but if competitors average 35/100, you're actually ahead and should focus elsewhere.

**Implementation approach:**
- Build on v1.1 batch infrastructure
- Add comparison statistics (average, min, max per score across competitor set)
- Add gap calculation and structured recommendations for closing gaps

---

## v1.3 — Automated Remediation Scripts
**Priority: Medium**

Finding problems is half the job. The tool should generate the fix — specific code snippets the developer or content team can deploy directly.

**Features:**
- "Generate Fix" button next to each low-scoring metric
- Meta description generator: takes page content, generates an SEO-optimized meta description in the 100-160 char range
- FAQPage schema generator: extracts Q&A pairs from page content, generates valid JSON-LD
- HowTo schema generator: structures steps from content into valid HowTo JSON-LD
- Canonical tag helper: generates the correct `<link rel="canonical">` tag
- Article schema generator: builds Article JSON-LD from page metadata
- Alt text suggestions: flags missing alt text, suggests descriptions based on image context (filename, surrounding text)
- Export: "Remediation Pack" — all recommended fixes in a single file, organized by priority

**Business value:** Closes the loop from insight to action. Instead of "your AEO score is low because you have no FAQ schema," the tool says "here's the exact JSON-LD to add to your page." This dramatically reduces the friction between audit and implementation.

**Implementation approach:**
- Each fix generator is a function that takes the analysis result and page content, returns a code snippet
- Use LLM for natural-language fixes (meta description, alt text suggestions)
- Use template-based generation for structured data (JSON-LD schemas are deterministic given the input data)

---

## v1.4 — Historical Tracking & Dashboard
**Priority: Medium**

One-time audits are useful, but trends are what drive decisions. A dashboard that shows scores over time lets businesses see whether their improvements are working.

**Features:**
- Save analysis results with timestamp (local storage or free-tier cloud — e.g., Google Sheets via API, or a lightweight SQLite backend)
- Dashboard view: line charts showing SEO/AEO/GEO scores over time
- Change alerts: "Your AEO score dropped 10 points since last month — here's what changed"
- Goal tracking: set target scores, see progress toward goals
- Comparison view: your scores vs. your own baseline (first audit)

**Business value:** Turns the tool from a point-in-time audit into an ongoing monitoring solution. Businesses can see the impact of their SEO/AEO/GEO investments over time and catch regressions early.

**Implementation approach:**
- Add a lightweight storage layer — SQLite for local, or Google Sheets API for cloud sync
- Dashboard built in Streamlit using st.line_chart or Altair
- Each analysis run is timestamped and stored with the URL as key

---

## v1.5 — Notion Integration (n8n Workflow)
**Priority: Medium-Low (but high relevance to target role)**

Given the job description emphasizes Notion-centric automation, building an n8n workflow that connects this analyzer to Notion would be a direct demonstration of the role's core skills.

**Features:**
- n8n workflow template that:
  1. Triggers on schedule (e.g., weekly) or webhook (e.g., after content publish)
  2. Runs the analyzer on a list of URLs from a Notion database
  3. Writes results back to the same Notion database (score properties, insights, timestamp)
- Notion database template: pre-configured with properties for SEO/AEO/GEO scores, issues, recommendations, status
- Optional: Slack/Teams notification when scores drop below threshold
- Optional: auto-create Notion pages for URLs that need urgent attention

**Business value:** This is the bridge between "analysis tool" and "agentic automation infrastructure." It shows the ability to connect a custom Python tool to a Notion-centric workflow — exactly the kind of system the job description asks for. It also makes the tool immediately useful to any Notion-based team.

**Implementation approach:**
- Publish the analyzer as a callable module (pip installable or Docker image)
- Build n8n workflow JSON that calls the analyzer and writes to Notion API
- Provide setup instructions for importing the workflow into n8n
- Include a Notion database template export

---

## Prioritization Rationale

| Priority | Feature | Why |
|----------|---------|-----|
| 1 (v1.1) | Batch analysis | Highest demand, lowest complexity. Turns tool into a real workflow enabler for the primary user persona (consultants/agencies). |
| 2 (v1.2) | Competitor benchmarking | Natural extension of batch. Adds strategic context that transforms scores into action. |
| 3 (v1.3) | Remediation scripts | Highest per-feature business value — closes the gap between insight and action. Differentiates from passive tools. |
| 4 (v1.4) | Historical tracking | Sustains engagement over time. Turns point-in-time audit into ongoing monitoring. |
| 5 (v1.5) | Notion + n8n integration | Directly relevant to the target role. Shows agentic automation skills. Makes tool part of a Notion-centric workflow. |
