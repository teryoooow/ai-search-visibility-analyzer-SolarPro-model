"""
AI Search Visibility Analyzer - Streamlit Web UI

A unified tool that analyzes any URL across three search paradigms:
- SEO: Traditional search engine optimization
- AEO: Answer engine optimization (featured snippets, direct answers)
- GEO: Generative engine optimization (LLM/chatbot visibility)

Run: streamlit run app.py
"""

import sys
import os

# Ensure analyzer modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import json

from analyzer.seo import analyze_seo
from analyzer.aeo import analyze_aeo
from analyzer.geo import analyze_geo


st.set_page_config(
    page_title="AI Search Visibility Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ──
st.markdown("""
<style>
    .score-card {
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .score-high { background: #d1fae5; border: 2px solid #10b981; }
    .score-mid { background: #fef3c7; border: 2px solid #f59e0b; }
    .score-low { background: #fee2e2; border: 2px solid #ef4444; }
    .score-number { font-size: 48px; font-weight: bold; }
    .score-label { font-size: 14px; color: #6b7280; margin-top: 4px; }
    .section-title {
        font-size: 18px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 10px;
        padding-bottom: 8px;
        border-bottom: 2px solid;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e5e7eb;
        font-size: 14px;
    }
    .metric-label { color: #374151; }
    .metric-value { color: #111827; font-weight: 500; }
    .metric-good { color: #10b981; }
    .metric-warn { color: #f59e0b; }
    .metric-bad { color: #ef4444; }
    .insight-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──
st.sidebar.title("🔍 AI Search Visibility Analyzer")
st.sidebar.markdown("""
**Analyze any URL** across three search paradigms:

- **SEO**: How well you rank in Google/Bing
- **AEO**: How well you appear in featured snippets & direct answers
- **GEO**: How well AI chatbots cite your content
""")

st.sidebar.markdown("---")
st.sidebar.subheader("How to use")
st.sidebar.info("""
1. Enter a URL in the input field
2. Click **Analyze** 
3. Review scores for SEO, AEO, and GEO
4. Export results as JSON for reporting
""")

st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.markdown("""
Built as a technical assessment demonstrating:
- Modular Python codebase (SEO/AEO/GEO separation)
- Free-tier API integration (PageSpeed Insights)
- LLM-ready analysis structure
- Streamlit UI with export capability
""")

st.sidebar.markdown("---")
st.sidebar.caption("v1.0 · Python · Streamlit")


# ── Main UI ──
st.title("🔍 AI Search Visibility Analyzer")
st.markdown("""
Analyze how a website performs across **traditional search**, **answer engines**, and **generative AI** — all in one report.
""")

url = st.text_input(
    "Enter URL to analyze",
    placeholder="https://example.com",
    label_visibility="collapsed",
    help="Enter any public URL. Results are analyzed in real-time.",
    key="url_input",
)

analyze_clicked = st.button(
    "🚀 Analyze",
    type="primary",
    use_container_width=True,
    disabled=not url or not url.startswith("http"),
)


# ── Loading state ──
if analyze_clicked and url:
    if not url.startswith("http"):
        st.error("Please enter a valid URL starting with http:// or https://")
    else:
        with st.spinner("🔍 Fetching page and analyzing SEO, AEO, and GEO signals..."):
            try:
                seo_result = analyze_seo(url)
                aeo_result = analyze_aeo(url)
                geo_result = analyze_geo(url)
                st.session_state["seo"] = seo_result
                st.session_state["aeo"] = aeo_result
                st.session_state["geo"] = geo_result
                st.session_state["url"] = url
                st.rerun()
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()


# ── Display results ──
if "seo" in st.session_state:
    seo = st.session_state["seo"]
    aeo = st.session_state["aeo"]
    geo = st.session_state["geo"]
    analysis_url = st.session_state["url"]

    # ── URL Header ──
    st.markdown(f"### Analyzing: `{analysis_url}`")
    st.caption(f"Analysis performed in real-time using free-tier infrastructure")

    # ── Score Cards Row ──
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    def score_color(score):
        if score >= 70:
            return "score-high", "Good"
        elif score >= 40:
            return "score-mid", "Needs work"
        else:
            return "score-low", "Poor"

    with col1:
        cls, label = score_color(seo.overall_score)
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-number" style="color:#10b981">{seo.overall_score:.0f}</div>
            <div class="score-label"><strong>SEO</strong> — Traditional Search<br>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        cls, label = score_color(aeo.overall_score)
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-number" style="color:#8b5cf6">{aeo.overall_score:.0f}</div>
            <div class="score-label"><strong>AEO</strong> — Answer Engines<br>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        cls, label = score_color(geo.overall_score)
        st.markdown(f"""
        <div class="score-card {cls}">
            <div class="score-number" style="color:#06b6d4">{geo.overall_score:.0f}</div>
            <div class="score-label"><strong>GEO</strong> — Generative AI<br>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── LLM Insight ──
    st.markdown("---")
    st.subheader("🤖 AI Analysis & Recommendations")
    st.markdown(f"""
    <div class="insight-box">
        <strong>Overall Assessment:</strong><br>
        This page scores <strong>{seo.overall_score:.0f}/100</strong> for traditional search (SEO), 
        <strong>{aeo.overall_score:.0f}/100</strong> for answer engine visibility (AEO), and 
        <strong>{geo.overall_score:.0f}/100</strong> for generative AI citability (GEO).
        <br><br>
        <strong>Key takeaway:</strong> The weakest area is 
        {'SEO' if min(seo.overall_score, aeo.overall_score, geo.overall_score) == seo.overall_score else 'AEO' if min(seo.overall_score, aeo.overall_score, geo.overall_score) == aeo.overall_score else 'GEO'} 
        — focus improvements there for the highest impact across all three search paradigms.
    </div>
    """, unsafe_allow_html=True)

    # ── SEO Section ──
    st.markdown("---")
    st.markdown('<div class="section-title" style="border-color:#10b981">📄 SEO — Traditional Search Engine Optimization</div>', unsafe_allow_html=True)

    seo_expander = st.expander("View detailed SEO metrics", expanded=True)
    with seo_expander:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Meta & Title**")
            st.metric("Title", seo.title[:60] + ("..." if len(seo.title) > 60 else ""))
            st.metric("Title Length", f"{seo.title_length} chars",
                      delta="Optimal" if 30 <= seo.title_length <= 60 else "Suboptimal",
                      delta_color="normal")
            st.metric("Meta Description", seo.meta_description[:80] + ("..." if len(seo.meta_description) > 80 else ""))
            st.metric("Meta Length", f"{seo.meta_description_length} chars",
                      delta="Optimal" if 100 <= seo.meta_description_length <= 160 else "Missing/Short",
                      delta_color="normal")

            st.markdown("**On-Page Structure**")
            st.metric("H1 Count", seo.h1_count, delta="Ideal: 1" if seo.h1_count == 1 else "Not ideal")
            st.metric("H2 Count", seo.h2_count)
            st.metric("Word Count", f"{seo.word_count} words",
                      delta="Good" if seo.word_count >= 300 else "Thin content",
                      delta_color="normal")

            st.markdown("**Images & Links**")
            st.metric("Images with Alt", f"{seo.images_with_alt}/{seo.images_total}",
                      delta=f"{seo.alt_coverage_score:.0f}% coverage")
            st.metric("Internal Links", seo.internal_links)
            st.metric("External Links", seo.external_links)
            st.metric("Link Ratio", f"{seo.link_ratio_score:.0f}%",
                      delta="Healthy" if 60 <= seo.link_ratio_score <= 80 else "Review")

        with c2:
            st.markdown("**Technical**")
            st.metric("Canonical Tag", "✅ Present" if seo.canonical_present else "❌ Missing")
            st.metric("Robots Meta", seo.robots_meta if seo.robots_meta else "None (indexable)")
            st.metric("Page Status", f"HTTP {seo.page_status}")

            st.markdown("**Core Web Vitals**")
            if seo.cwvs_fetched:
                st.metric("LCP (Largest Contentful Paint)", f"{seo.lcp:.0f}ms" if seo.lcp else "N/A",
                          delta="Good" if seo.lcp and seo.lcp <= 2500 else "Poor")
                st.metric("FID (First Input Delay)", f"{seo.fid:.0f}ms" if seo.fid else "N/A",
                          delta="Good" if seo.fid and seo.fid <= 100 else "Poor")
                st.metric("CLS (Cumulative Layout Shift)", f"{seo.cls:.3f}" if seo.cls else "N/A",
                          delta="Good" if seo.cls and seo.cls <= 0.1 else "Poor")
            else:
                st.info("⚠️ Core Web Vitals data not available (PageSpeed API rate limit or fetch error)")

            st.markdown("**Readability**")
            st.metric("Readability Score", f"{seo.readability_score:.0f}/100",
                      delta="Easy to read" if seo.readability_score >= 80 else "Complex")

    st.markdown("**SEO Score Breakdown:**")
    seo_factors = [
        ("Title tag quality", seo.title_score),
        ("Meta description", seo.meta_description_score),
        ("H1 optimization", seo.h1_score),
        ("Readability", seo.readability_score),
        ("Link ratio", seo.link_ratio_score),
        ("Alt text coverage", seo.alt_coverage_score),
        ("Canonical present", seo.canonical_score),
        ("Robots meta", seo.robots_score),
        ("Core Web Vitals", seo.cwvs_score),
    ]
    for label, score in seo_factors:
        color = "metric-good" if score >= 70 else "metric-warn" if score >= 40 else "metric-bad"
        st.markdown(
            f'<div class="metric-row"><span class="metric-label">{label}</span>'
            f'<span class="metric-value {color}">{score:.0f}/100</span></div>',
            unsafe_allow_html=True,
        )

    # ── AEO Section ──
    st.markdown("---")
    st.markdown('<div class="section-title" style="border-color:#8b5cf6">❓ AEO — Answer Engine Optimization</div>', unsafe_allow_html=True)

    aeo_expander = st.expander("View detailed AEO metrics", expanded=True)
    with aeo_expander:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Structured Data**")
            st.metric("Schema.org Present", "✅ Yes" if aeo.schema_present else "❌ No")
            if aeo.schema_types:
                st.success(f"Types: {', '.join(aeo.schema_types)}")
            else:
                st.warning("No JSON-LD structured data detected — this is critical for AEO")

            st.markdown("**FAQ / HowTo Schema**")
            st.metric("FAQPage Schema", "✅ Yes" if aeo.has_faq_schema else "❌ No")
            st.metric("FAQ Questions", aeo.faq_count)
            st.metric("HowTo Schema", "✅ Yes" if aeo.has_howto_schema else "❌ No")
            st.metric("HowTo Steps", aeo.howto_count)

            st.markdown("**Content Schema**")
            st.metric("Article Schema", "✅ Yes" if aeo.has_article_schema else "❌ No")
            st.metric("Product Schema", "✅ Yes" if aeo.has_product_schema else "❌ No")
            st.metric("Local Business Schema", "✅ Yes" if aeo.has_local_business_schema else "❌ No")

        with c2:
            st.markdown("**Answer Signals**")
            st.metric("Visible Questions", aeo.question_count,
                      delta="Strong" if aeo.question_count >= 5 else "Weak")
            st.metric("Definition Patterns", aeo.definition_count,
                      delta="Good" if aeo.definition_count >= 3 else "Add more")
            st.metric("Answer Quality Score", f"{aeo.answer_quality_score:.0f}/100")

            st.markdown("**Featured Snippet Factors**")
            st.metric("Lists Present", "✅ Yes" if aeo.list_present else "❌ No")
            st.metric("Tables Present", "✅ Yes" if aeo.table_present else "❌ No")
            st.metric("Snippet Signals", aeo.featured_snippet_signals,
                      delta="Strong" if aeo.featured_snippet_signals >= 6 else "Build more")

    st.markdown("**AEO Score Breakdown:**")
    aeo_factors = [
        ("Structured data coverage", 100 if aeo.schema_present else 0),
        ("FAQ schema", 100 if aeo.has_faq_schema else 0),
        ("HowTo schema", 100 if aeo.has_howto_schema else 0),
        ("Question density", min(100, aeo.question_count * 10)),
        ("Definition clarity", min(100, aeo.definition_count * 15)),
        ("List/table signals", (20 if aeo.list_present else 0) + (20 if aeo.table_present else 0)),
        ("Content schema types", min(100, len(aeo.schema_types) * 15)),
    ]
    for label, score in aeo_factors:
        color = "metric-good" if score >= 70 else "metric-warn" if score >= 40 else "metric-bad"
        st.markdown(
            f'<div class="metric-row"><span class="metric-label">{label}</span>'
            f'<span class="metric-value {color}">{score:.0f}/100</span></div>',
            unsafe_allow_html=True,
        )

    # ── GEO Section ──
    st.markdown("---")
    st.markdown('<div class="section-title" style="border-color:#06b6d4">🧠 GEO — Generative Engine Optimization</div>', unsafe_allow_html=True)

    geo_expander = st.expander("View detailed GEO metrics", expanded=True)
    with geo_expander:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Brand & Entity**")
            st.metric("Brand Name Detected", geo.brand_name)
            st.metric("Brand Mentions", geo.brand_mentions,
                      delta=f"{geo.brand_mention_density:.1f} per 100 words")
            st.metric("Domain", geo.domain)

            st.markdown("**Author & Authority (E-E-A-T)**")
            st.metric("Author Mentioned", "✅ Yes" if geo.author_mentioned else "❌ No")
            if geo.author_name:
                st.info(f"Author: {geo.author_name}")
            st.metric("Author Box Present", "✅ Yes" if geo.has_author_box else "❌ No")
            st.metric("Credentials Signals", geo.credentials_signals,
                      delta="Strong" if geo.credentials_signals >= 4 else "Weak")
            st.metric("Date Published", geo.date_published if geo.date_published else "Not found")

            st.markdown("**Citation Potential**")
            st.metric("Quotes Found", geo.quote_count,
                      delta=f"{geo.quote_density:.2f} per 100 words")
            st.metric("Statistics Found", geo.statistic_count,
                      delta=f"{geo.statistic_density:.2f} per 100 words")

        with c2:
            st.markdown("**LLM Readability**")
            st.metric("LLM Readability Score", f"{geo.llm_readability_score:.0f}/100",
                      delta="Good" if geo.llm_readability_score >= 70 else "Needs work")
            st.metric("Word Count", geo.word_count)

            st.markdown("**Content Structure**")
            st.metric("Content Structure Score", f"{geo.content_structure_score:.0f}/100")
            st.metric("Structured Data", "✅ Present" if geo.schema_present else "❌ Missing")

            st.markdown("**Overall GEO**")
            st.metric("Citation Potential", f"{geo.citation_potential_score:.0f}/100")
            st.metric("Entity Coverage", f"{geo.entity_coverage_score:.0f}/100")
            st.metric("GEO Overall Score", f"{geo.overall_score:.0f}/100",
                      delta="Good" if geo.overall_score >= 70 else "Needs work")

    st.markdown("**GEO Score Breakdown:**")
    geo_factors = [
        ("Citation potential", geo.citation_potential_score),
        ("Entity coverage", geo.entity_coverage_score),
        ("LLM readability", geo.llm_readability_score),
        ("Content structure", geo.content_structure_score),
    ]
    for label, score in geo_factors:
        color = "metric-good" if score >= 70 else "metric-warn" if score >= 40 else "metric-bad"
        st.markdown(
            f'<div class="metric-row"><span class="metric-label">{label}</span>'
            f'<span class="metric-value {color}">{score:.0f}/100</span></div>',
            unsafe_allow_html=True,
        )

    # ── Export ──
    st.markdown("---")
    st.subheader("📥 Export Results")

    export_data = {
        "url": analysis_url,
        "timestamp": st.session_state.get("timestamp", ""),
        "seo": seo.to_dict(),
        "aeo": aeo.to_dict(),
        "geo": geo.to_dict(),
    }

    col1, col2 = st.columns([1, 4])
    with col1:
        st.download_button(
            label="⬇ Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"visibility-report-{url.replace('https://', '').replace('http://', '').replace('/', '_')}.json",
            mime="application/json",
            type="primary",
        )
    with col2:
        st.info("Click 'Download JSON' to save the full analysis report. The file can be imported into reporting tools, shared with stakeholders, or used as input for batch analysis pipelines.")

    st.markdown("---")
    st.caption("AI Search Visibility Analyzer v1.0 — Built with Python, BeautifulSoup, Requests, and Streamlit. "
               "SEO CWV data sourced from PageSpeed Insights API (free tier). "
               "All analysis runs client-side — no data is stored or transmitted.")
