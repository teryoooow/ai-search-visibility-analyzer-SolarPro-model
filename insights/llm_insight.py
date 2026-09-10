# -*- coding: utf-8 -*-
"""
AI Search Visibility Analyzer - LLM Insight Generator
Generates strategic recommendations using free-tier LLM APIs
with heuristic fallback when no API key is configured.
"""

import os
import sys
from typing import Optional, Dict, Any


def generate_insight(
    url: str,
    seo_score: float,
    aeo_score: float,
    geo_score: float,
    seo_metrics: Dict[str, Any],
    aeo_metrics: Dict[str, Any],
    geo_metrics: Dict[str, Any],
    api_key: Optional[str] = None,
) -> str:
    """
    Generate strategic insight using DeepSeek API (free tier).
    Falls back to heuristic analysis when no API key is provided.
    """
    if api_key and api_key.startswith("sk-"):
        return _llm_insight(
            url, seo_score, aeo_score, geo_score,
            seo_metrics, aeo_metrics, geo_metrics, api_key
        )
    return _heuristic_insight(
        url, seo_score, aeo_score, geo_score,
        seo_metrics, aeo_metrics, geo_metrics
    )


def _llm_insight(
    url: str,
    seo_score: float,
    aeo_score: float,
    geo_score: float,
    seo_metrics: Dict[str, Any],
    aeo_metrics: Dict[str, Any],
    geo_metrics: Dict[str, Any],
    api_key: str,
) -> str:
    """Call DeepSeek API for insight generation."""
    import urllib.request
    import json

    prompt = _build_prompt(url, seo_score, aeo_score, geo_score,
                           seo_metrics, aeo_metrics, geo_metrics)

    try:
        req_body = json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 2000,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=req_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]

    except Exception as e:
        # Fallback to heuristic on any API error
        return _heuristic_insight(
            url, seo_score, aeo_score, geo_score,
            seo_metrics, aeo_metrics, geo_metrics
        ) + f"\n\n[Note: LLM insight unavailable due to API error: {e}. Showing heuristic analysis instead.]\n"


def _build_prompt(
    url: str,
    seo_score: float,
    aeo_score: float,
    geo_score: float,
    seo_metrics: Dict[str, Any],
    aeo_metrics: Dict[str, Any],
    geo_metrics: Dict[str, Any],
) -> str:
    """Build the LLM prompt from analysis data."""
    return f"""You are an expert SEO, AEO, and GEO consultant. Analyze the following website audit data and provide a concise, actionable report.

URL Analyzed: {url}

=== SEO (Traditional Search) ===
Overall Score: {seo_score:.1f}/100
Key metrics:
- Title: "{seo_metrics.get('title', 'N/A')}" ({seo_metrics.get('title_length', 0)} chars)
- Meta Description: {"Present" if seo_metrics.get('meta_description', '') else "Missing"} ({seo_metrics.get('meta_description_length', 0)} chars)
- H1 Count: {seo_metrics.get('h1_count', 0)} (ideal: 1)
- H2 Count: {seo_metrics.get('h2_count', 0)}
- Word Count: {seo_metrics.get('word_count', 0)}
- Readability Score: {seo_metrics.get('readability_score', 0):.1f}/100
- Alt Text Coverage: {seo_metrics.get('alt_coverage_score', 0):.1f}% ({seo_metrics.get('images_with_alt', 0)}/{seo_metrics.get('images_total', 0)} images)
- Canonical Tag: {"Present" if seo_metrics.get('canonical_present') else "Missing"}
- Internal Links: {seo_metrics.get('internal_links', 0)}, External Links: {seo_metrics.get('external_links', 0)}
- Core Web Vitals: {"Fetched" if seo_metrics.get('cwvs_fetched') else "Not available"}
  LCP: {seo_metrics.get('lcp', 'N/A')}, FID: {seo_metrics.get('fid', 'N/A')}, CLS: {seo_metrics.get('cls', 'N/A')}
{'- Title score: ' + str(seo_metrics.get('title_score', 0)) if seo_metrics.get('title_score') else ''}
{'- Meta description score: ' + str(seo_metrics.get('meta_description_score', 0)) if seo_metrics.get('meta_description_score') else ''}

=== AEO (Answer Engine Optimization) ===
Overall Score: {aeo_score:.1f}/100
Key metrics:
- Schema.org Present: {"Yes" if aeo_metrics.get('schema_present') else "No"}
- Schema Types: {aeo_metrics.get('schema_types', [])}
- FAQPage Schema: {"Yes" if aeo_metrics.get('has_faq_schema') else "No"}
- HowTo Schema: {"Yes" if aeo_metrics.get('has_howto_schema') else "No"}
- Article Schema: {"Yes" if aeo_metrics.get('has_article_schema') else "No"}
- Question Count (visible in text): {aeo_metrics.get('question_count', 0)}
- Definition Patterns: {aeo_metrics.get('definition_count', 0)}
- Lists Present: {"Yes" if aeo_metrics.get('list_present') else "No"}
- Tables Present: {"Yes" if aeo_metrics.get('table_present') else "No"}
- Featured Snippet Signals: {aeo_metrics.get('featured_snippet_signals', 0)}
- Answer Quality Score: {aeo_metrics.get('answer_quality_score', 0):.1f}/100

=== GEO (Generative Engine Optimization) ===
Overall Score: {geo_score:.1f}/100
Key metrics:
- Brand Name Detected: "{geo_metrics.get('brand_name', 'N/A')}"
- Brand Mentions: {geo_metrics.get('brand_mentions', 0)} ({geo_metrics.get('brand_mention_density', 0):.2f} per 100 words)
- Author Mentioned: {"Yes" if geo_metrics.get('author_mentioned') else "No"}
- Author Name: {geo_metrics.get('author_name', 'N/A')}
- Date Published: {geo_metrics.get('date_published', 'N/A')}
- Author Bio Box: {"Yes" if geo_metrics.get('has_author_box') else "No"}
- Credentials Signals: {geo_metrics.get('credentials_signals', 0)}
- Quote Count: {geo_metrics.get('quote_count', 0)} ({geo_metrics.get('quote_density', 0):.2f} per 100 words)
- Statistic Count: {geo_metrics.get('statistic_count', 0)} ({geo_metrics.get('statistic_density', 0):.2f} per 100 words)
- Entity Coverage Score: {geo_metrics.get('entity_coverage_score', 0):.1f}/100
- LLM Readability Score: {geo_metrics.get('llm_readability_score', 0):.1f}/100
- Content Structure Score: {geo_metrics.get('content_structure_score', 0):.1f}/100
- Citation Potential Score: {geo_metrics.get('citation_potential_score', 0):.1f}/100

Based on these metrics, provide a concise report covering:

1. EXECUTIVE SUMMARY (2-3 sentences): Overall visibility posture across all three domains. What's the single most important takeaway?

2. TOP 3 STRENGTHS: What this page does well across SEO/AEO/GEO. Be specific — cite actual metrics.

3. TOP 3 WEAKNESSES: The most impactful gaps. Prioritize by business impact, not by score magnitude. A missing canonical tag is more actionable than a slightly low readability score.

4. TOP 3 ACTIONABLE RECOMMENDATIONS: Specific, implementable actions ranked by impact. For each: what to do, why it matters, and rough effort level (quick win / medium / significant).

5. CROSS-DOMAIN SYNERGIES: Which single change would improve multiple scores simultaneously? (e.g., adding FAQPage schema boosts both AEO and GEO)

Keep the report under 500 words. Use specific numbers from the metrics. Avoid generic advice like "improve your SEO" — be concrete and actionable.
"""


def _heuristic_insight(
    url: str,
    seo_score: float,
    aeo_score: float,
    geo_score: float,
    seo_metrics: Dict[str, Any],
    aeo_metrics: Dict[str, Any],
    geo_metrics: Dict[str, Any],
) -> str:
    """Generate insight using rule-based analysis (no API key required)."""
    lines = []
    lines.append(f"# AI Search Visibility Analysis: {url}")
    lines.append("")
    lines.append(f"**Analysis generated by AI Search Visibility Analyzer** (heuristic mode — no LLM API configured)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Overall Scores")
    lines.append("")
    lines.append(f"| Domain | Score | Assessment |")
    lines.append(f"|--------|-------|------------|")
    lines.append(f"| SEO (Traditional Search) | {seo_score:.0f}/100 | {'_' + _assessment(seo_score)} |")
    lines.append(f"| AEO (Answer Engines) | {aeo_score:.0f}/100 | {'_' + _assessment(aeo_score)} |")
    lines.append(f"| GEO (Generative AI) | {geo_score:.0f}/100 | {'_' + _assessment(geo_score)} |")
    lines.append("")
    lines.append(f"**Composite visibility score: {(seo_score + aeo_score + geo_score) / 3:.0f}/100**")
    lines.append("")

    # Weakest area
    scores = {"SEO": seo_score, "AEO": aeo_score, "GEO": geo_score}
    weakest = min(scores, key=scores.get)
    strongest = max(scores, key=scores.get)
    lines.append(f"## Key Finding")
    lines.append("")
    lines.append(f"The weakest area is **{weakest}** ({scores[weakest]:.0f}/100). "
                 f"The strongest is **{strongest}** ({scores[strongest]:.0f}/100). "
                   f"Focus improvement efforts on {weakest} for the highest marginal impact.")
    lines.append("")

    # Specific recommendations based on metric gaps
    lines.append("## Strengths")
    lines.append("")
    strengths = []
    if seo_metrics.get("title_score", 0) >= 80:
        strengths.append(f"- SEO: Title tag is well-optimized ({seo_metrics.get('title_length', 0)} chars)")
    if seo_metrics.get("meta_description_score", 0) >= 80:
        strengths.append(f"- SEO: Meta description is optimal ({seo_metrics.get('meta_description_length', 0)} chars)")
    if seo_metrics.get("h1_score", 0) >= 80:
        strengths.append(f"- SEO: H1 structure is correct ({seo_metrics.get('h1_count', 0)} H1 tag(s))")
    if seo_metrics.get("alt_coverage_score", 0) >= 80:
        strengths.append(f"- SEO: Image alt text coverage is strong ({seo_metrics.get('images_with_alt', 0)}/{seo_metrics.get('images_total', 0)} images)")
    if aeo_metrics.get("schema_present"):
        schema_types = ", ".join(aeo_metrics.get("schema_types", []))
        strengths.append(f"- AEO: Structured data present ({schema_types})")
    if aeo_metrics.get("has_faq_schema"):
        strengths.append(f"- AEO: FAQPage schema detected ({aeo_metrics.get('faq_count', 0)} questions)")
    if aeo_metrics.get("question_count", 0) >= 5:
        strengths.append(f"- AEO: Strong question density ({aeo_metrics.get('question_count', 0)} visible questions)")
    if geo_metrics.get("author_mentioned"):
        strengths.append(f"- GEO: Author identified ({geo_metrics.get('author_name', 'unknown')})")
    if geo_metrics.get("quote_density", 0) > 0.5:
        strengths.append(f"- GEO: Good quote density ({geo_metrics.get('quote_count', 0)} quotes, {geo_metrics.get('quote_density', 0):.2f} per 100 words)")
    if geo_metrics.get("statistic_density", 0) > 0.3:
        strengths.append(f"- GEO: Strong statistic density ({geo_metrics.get('statistic_count', 0)} stats, {geo_metrics.get('statistic_density', 0):.2f} per 100 words)")
    if geo_metrics.get("llm_readability_score", 0) >= 80:
        strengths.append(f"- GEO: LLM readability is excellent ({geo_metrics.get('llm_readability_score', 0):.0f}/100)")

    if strengths:
        lines.extend(strengths)
    else:
        lines.append("- No significant strengths detected at threshold levels")
    lines.append("")

    lines.append("## Critical Gaps & Recommendations")
    lines.append("")
    gaps = []

    # SEO gaps
    if seo_score < 70:
        if seo_metrics.get("title_score", 0) < 70:
            gaps.append(
                f"- **SEO: Fix title tag** — Current title is {seo_metrics.get('title_length', 0)} chars "
                f"(should be 30-60). Title appears in search results and is the #1 on-page SEO factor. "
                f"Effort: Quick win. Rewrite to include primary keyword near the front, keep under 60 chars."
            )
        if seo_metrics.get("meta_description_score", 0) < 70:
            gaps.append(
                f"- **SEO: Add/optimize meta description** — Meta description is "
                f"{'missing' if seo_metrics.get('meta_description_length', 0) == 0 else str(seo_metrics.get('meta_description_length', 0)) + ' chars (target 100-160)'}. "
                f"Meta descriptions don't directly affect rankings but significantly impact click-through rate from search results. "
                f"Effort: Quick win. Write a compelling 100-160 char description with target keywords and a clear value proposition."
            )
        if not seo_metrics.get("canonical_present"):
            gaps.append(
                "- **SEO: Add canonical tag** — No self-referential canonical found. Without this, duplicate content issues can dilute ranking signals. "
                "Effort: Quick win. Add `<link rel=\"canonical\" href=\"[this page URL]\">` to the `<head>`."
            )
        if seo_metrics.get("h1_score", 0) < 70:
            gaps.append(
                f"- **SEO: Fix H1 structure** — Found {seo_metrics.get('h1_count', 0)} H1 tags (ideal: exactly 1). "
                "Multiple H1s confuse search engines about the page's primary topic. "
                "Effort: Quick win. Ensure exactly one H1 per page that matches the title tag's primary keyword."
            )
        if seo_metrics.get("word_count", 0) < 300:
            gaps.append(
                f"- **SEO: Expand content depth** — Only {seo_metrics.get('word_count', 0)} words detected. "
                "Thin content rarely ranks well and provides less material for AEO/GEO extraction. "
                "Effort: Medium. Add substantive content (500+ words) covering the topic comprehensively."
            )
        if seo_metrics.get("cwvs_fetched") and seo_metrics.get("cwvs_score", 0) < 70:
            gaps.append(
                f"- **SEO: Improve Core Web Vitals** — CWV score is {seo_metrics.get('cwvs_score', 0):.0f}/100. "
                f"LCP: {seo_metrics.get('lcp', 'N/A')}, FID: {seo_metrics.get('fid', 'N/A')}, CLS: {seo_metrics.get('cls', 'N/A')}. "
                "Poor CWV hurts both rankings and user experience. Effort: Medium-Significant. Optimize images, reduce JS execution time, prevent layout shifts."
            )

    # AEO gaps
    if aeo_score < 70:
        if not aeo_metrics.get("schema_present"):
            gaps.append(
                "- **AEO: Add Schema.org structured data** — No JSON-LD detected. This is the single highest-impact AEO improvement. "
                "Search engines use schema to understand content and extract answers. "
                "Effort: Medium. Add appropriate schema type (Article, WebPage, Product, FAQPage, etc.) as JSON-LD in the `<head>`. "
                "Use Google's Structured Data Markup Helper or a schema generator tool."
            )
        if not aeo_metrics.get("has_faq_schema") and aeo_metrics.get("question_count", 0) >= 2:
            gaps.append(
                f"- **AEO: Add FAQPage schema** — {aeo_metrics.get('question_count', 0)} questions detected on page but not wrapped in FAQPage schema. "
                "FAQ schema directly targets featured snippets and direct answer extraction. "
                "Effort: Quick win (if questions already exist). Wrap existing Q&A pairs in FAQPage JSON-LD."
            )
        if aeo_metrics.get("question_count", 0) < 3:
            gaps.append(
                "- **AEO: Add more Q&A content** — Only a few questions detected. Answer engines look for question-and-answer patterns. "
                "Effort: Medium. Add a FAQ section with 5-10 questions that your audience actually searches for. "
                "Use Google's 'People Also Ask' for question ideas."
            )
        if not aeo_metrics.get("list_present") and not aeo_metrics.get("table_present"):
            gaps.append(
                "- **AEO: Add lists or tables** — No lists or tables detected. Featured snippets frequently extract list items and table data. "
                "Effort: Quick win. Convert procedural content into ordered lists, comparisons into tables, and key points into bullet lists."
            )

    # GEO gaps
    if geo_score < 70:
        if not geo_metrics.get("author_mentioned"):
            gaps.append(
                "- **GEO: Add author information** — No author detected. LLMs prioritize content with clear authorship as an authority signal. "
                "Effort: Medium. Add author bylines, bio sections, and author schema markup (Person JSON-LD). "
                "Include credentials, expertise, and links to author's other work or social profiles."
            )
        if not geo_metrics.get("has_author_box"):
            gaps.append(
                "- **GEO: Add author bio box** — Author bio section missing. Bio boxes signal expertise to both users and AI systems. "
                "Effort: Quick win. Add an author bio section at the end of articles with brief credentials and links."
            )
        if geo_metrics.get("quote_count", 0) < 3:
            gaps.append(
                "- **GEO: Add quotable content** — Only a few quotes detected. LLMs preferentially cite content with specific, verifiable claims. "
                "Effort: Medium. Include expert quotes, cite specific statistics with sources, and use direct quotes from credible sources. "
                "Each article should have at least 3-5 quotable passages."
            )
        if geo_metrics.get("statistic_count", 0) < 2:
            gaps.append(
                "- **GEO: Add statistics and data** — Content lacks data points. LLMs favor content with specific numbers and statistics. "
                "Effort: Medium. Add statistics from credible sources (research reports, government data, industry surveys). "
                "Each statistic should have a clear source citation."
            )
        if geo_metrics.get("brand_mention_density", 0) < 0.5:
            gaps.append(
                f"- **GEO: Increase brand mentions** — Brand '{geo_metrics.get('brand_name', 'N/A')}' appears infrequently. "
                "Natural brand mentions throughout content improve entity recognition by LLMs. "
                "Effort: Low. Add contextual brand references in introduction, conclusion, and where naturally relevant."
            )
        if geo_metrics.get("llm_readability_score", 0) < 70:
            gaps.append(
                f"- **GEO: Improve LLM readability** — Score is {geo_metrics.get('llm_readability_score', 0):.0f}/100. "
                "LLMs parse content more easily when it's well-structured. "
                "Effort: Quick win. Use shorter paragraphs (under 80 words), add clear heading hierarchy (H1→H2→H3), "
                "and prefer simple sentence structures."
            )

    if gaps:
        lines.extend(gaps)
    else:
        lines.append("- All areas are at or above target thresholds. Focus on maintaining and monitoring.")
    lines.append("")

    # Cross-domain synergy
    lines.append("## Cross-Domain Opportunities")
    lines.append("")
    synergy_found = False

    if not aeo_metrics.get("schema_present") and seo_score < 70:
        lines.append(
            "1. **Add Schema.org structured data** — This single change improves both AEO (direct answer extraction) "
            "and SEO (better understanding by search engines). Start with Article or WebPage schema, then add "
            "FAQPage if you have Q&A content. This is the highest-leverage single action for most pages."
        )
        synergy_found = True

    if not geo_metrics.get("author_mentioned") and aeo_metrics.get("schema_present"):
        lines.append(
            "2. **Add author schema (Person JSON-LD)** — Improves GEO (LLM authority signal) and AEO (richer structured data). "
            "Add author name, bio, and credentials as structured data."
        )
        synergy_found = True

    if geo_metrics.get("quote_count", 0) < 3 and seo_metrics.get("word_count", 0) < 500:
        lines.append(
            "3. **Expand content with quotable data** — Adding 300+ words of content with specific statistics and expert quotes "
            "simultaneously improves SEO (content depth), AEO (more extractable answers), and GEO (more citable material). "
            "This is the best multi-domain content investment."
        )
        synergy_found = True

    if not synergy_found:
        lines.append(
            "1. **Monitor and maintain** — Current scores are reasonable across domains. "
            "Focus on tracking changes over time and addressing any new gaps promptly. "
            "Set up periodic re-analysis to catch regressions."
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"_Analysis generated by AI Search Visibility Analyzer v1.0_. ")
    lines.append(f"SEO CWV data from PageSpeed Insights API (free tier). ")
    lines.append(f"Heuristic insight mode — LLM API not configured. ")
    lines.append(f"Set DEEPSEEK_API_KEY environment variable to enable AI-generated insights.")

    return "\n".join(lines)


def _assessment(score: float) -> str:
    """Return assessment label for a score."""
    if score >= 70:
        return "Healthy"
    elif score >= 40:
        return "Needs improvement"
    else:
        return "Critical gaps"


if __name__ == "__main__":
    import json

    # Demo with test data
    result = generate_insight(
        url="https://example.com",
        seo_score=47.5,
        aeo_score=0.0,
        geo_score=40.9,
        seo_metrics={
            "title": "Example Domain",
            "title_length": 14,
            "meta_description": "",
            "meta_description_length": 0,
            "h1_count": 1,
            "h2_count": 0,
            "word_count": 21,
            "readability_score": 100.0,
            "images_with_alt": 0,
            "images_total": 0,
            "alt_coverage_score": 100.0,
            "canonical_present": False,
            "internal_links": 0,
            "external_links": 1,
            "cwvs_fetched": False,
            "lcp": None,
            "fid": None,
            "cls": None,
        },
        aeo_metrics={
            "schema_present": False,
            "schema_types": [],
            "has_faq_schema": False,
            "faq_count": 0,
            "has_howto_schema": False,
            "howto_count": 0,
            "has_article_schema": False,
            "has_product_schema": False,
            "has_local_business_schema": False,
            "question_count": 0,
            "definition_count": 0,
            "list_present": False,
            "table_present": False,
            "featured_snippet_signals": 0,
            "answer_quality_score": 0.0,
        },
        geo_metrics={
            "brand_name": "Example",
            "brand_mentions": 2,
            "brand_mention_density": 9.52,
            "author_mentioned": False,
            "author_name": "",
            "date_published": "",
            "has_author_box": False,
            "credentials_signals": 0,
            "quote_count": 0,
            "quote_density": 0.0,
            "statistic_count": 0,
            "statistic_density": 0.0,
            "entity_coverage_score": 33.0,
            "llm_readability_score": 70.0,
            "content_structure_score": 50.0,
            "citation_potential_score": 24.6,
        },
        api_key=None,  # No key — uses heuristic fallback
    )
    print(result)
