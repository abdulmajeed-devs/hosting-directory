"""
HostAdvice Authentic Comparison Engine & Static Site Generator
Renders an ultra-attractive, modern, world-class head-to-head comparison page for all hosting providers,
featuring:
1. Prominent Hero Showdown Battle Arena with real brand logos, star ratings, and official CTAs
2. 4-Card Executive Benchmark Highlights Ribbon
3. Brand logos embedded directly inside all comparison tables
4. Detailed specifications across Pricing, Server Performance, and Customer Support
5. Authentic Pros & Cons side-by-side evaluation
6. Dedicated Customer Reviews & Ratings Comparison section at the end with verified user testimonials
7. Static Rounded Capsule Navigation Bar with quick anchors
"""

import os
import json
import itertools
from compare_matrix_engine import compare_two_companies
from company_portfolio_data import get_company_portfolio_data

def format_ha_val(val):
    val_str = str(val).strip()
    lower = val_str.lower()
    
    # Positive specs
    if any(pos in lower for pos in ['yes', 'included', 'unlimited', 'free', '100%']):
        return f'''<span class="ha-val-pill ha-val-yes">
            <svg class="ha-icon-check" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
            </svg>
            <span>{val_str}</span>
        </span>'''
        
    # Negative specs
    elif any(neg in lower for neg in ['no', 'none', 'paid add-on', 'not included', 'separate', 'n/a']):
        return f'''<span class="ha-val-pill ha-val-no">
            <svg class="ha-icon-cross" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
            </svg>
            <span>{val_str}</span>
        </span>'''
        
    # Standard text spec
    return f'<span class="ha-val-text">{val_str}</span>'

def build_ha_compare_table(rows, name_a, name_b, slug_a, slug_b, price_a, price_b, winner_name, meta_a, meta_b, category_title="Key Feature / Specification"):
    is_win_a = (winner_name == name_a)
    is_win_b = (winner_name == name_b)
    
    cls_hdr_a = "hosting-col winner" if is_win_a else "hosting-col"
    cls_hdr_b = "hosting-col winner" if is_win_b else "hosting-col"
    
    winner_tag_a = '<div class="winner-ribbon"><svg class="trophy-svg" viewBox="0 0 24 24" fill="currentColor"><path d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94A5.01 5.01 0 0011 15.9V19H7v2h10v-2h-4v-3.1c1.92-.35 3.44-1.74 3.96-3.56C19.28 12.03 21 9.95 21 7V5h-2zm-14 3c0-1.65 1.35-3 3-3v3.82C6.18 8.6 5 7.6 5 6.3V8zm14 0c0 1.3-1.18 2.3-3 2.52V5c1.65 0 3 1.35 3 3z"/></svg> <span>OVERALL WINNER</span></div>' if is_win_a else '<div class="runner-ribbon"><span>CONTENDER</span></div>'
    winner_tag_b = '<div class="winner-ribbon"><svg class="trophy-svg" viewBox="0 0 24 24" fill="currentColor"><path d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94A5.01 5.01 0 0011 15.9V19H7v2h10v-2h-4v-3.1c1.92-.35 3.44-1.74 3.96-3.56C19.28 12.03 21 9.95 21 7V5h-2zm-14 3c0-1.65 1.35-3 3-3v3.82C6.18 8.6 5 7.6 5 6.3V8zm14 0c0 1.3-1.18 2.3-3 2.52V5c1.65 0 3 1.35 3 3z"/></svg> <span>OVERALL WINNER</span></div>' if is_win_b else '<div class="runner-ribbon"><span>CONTENDER</span></div>'
    
    logo_a = meta_a.get('logo_url', f"https://logo.clearbit.com/{meta_a.get('domain', 'example.com')}")
    fav_a = meta_a.get('favicon_url', f"https://www.google.com/s2/favicons?domain={meta_a.get('domain', 'example.com')}&sz=128")
    logo_b = meta_b.get('logo_url', f"https://logo.clearbit.com/{meta_b.get('domain', 'example.com')}")
    fav_b = meta_b.get('favicon_url', f"https://www.google.com/s2/favicons?domain={meta_b.get('domain', 'example.com')}&sz=128")

    html = f'''
    <div class="compare-table-wrap">
      <div class="compare-table">
        <header>
          <div class="overview">
            <span class="overview-badge">
              <svg class="overview-svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1v-2zm1 5a1 1 0 00-1 1v2a1 1 0 001 1h12a1 1 0 001-1v-2a1 1 0 00-1-1H4z" clip-rule="evenodd"/></svg>
              BENCHMARK MATRIX
            </span>
            <div class="overview-title">{category_title}</div>
            <span class="overview-sub">Direct Tier Comparison</span>
          </div>
          <div class="hosting-info">
            <div class="{cls_hdr_a}">
              {winner_tag_a}
              <div class="table-brand-logo-card">
                <img src="{logo_a}" alt="{name_a} Logo" class="table-brand-logo-img" onerror="this.onerror=null; this.src='{fav_a}';" loading="lazy">
              </div>
              <a href="../pages/{slug_a}.html" class="brand-title-link" title="View {name_a} Portfolio & Specs">{name_a}</a>
              <div class="brand-price-tag">
                <span class="price-prefix">From</span>
                <span class="price-amount">{price_a}</span>
              </div>
              <div class="btn-group-col">
                <a class="btn-ha-official" href="{meta_a.get('website', '#')}" target="_blank" rel="noopener">Official Site &nearr;</a>
                <a class="btn-ha-profile" href="../pages/{slug_a}.html">View Company Info</a>
              </div>
            </div>
            <div class="{cls_hdr_b}">
              {winner_tag_b}
              <div class="table-brand-logo-card">
                <img src="{logo_b}" alt="{name_b} Logo" class="table-brand-logo-img" onerror="this.onerror=null; this.src='{fav_b}';" loading="lazy">
              </div>
              <a href="../pages/{slug_b}.html" class="brand-title-link" title="View {name_b} Portfolio & Specs">{name_b}</a>
              <div class="brand-price-tag">
                <span class="price-prefix">From</span>
                <span class="price-amount">{price_b}</span>
              </div>
              <div class="btn-group-col">
                <a class="btn-ha-official" href="{meta_b.get('website', '#')}" target="_blank" rel="noopener">Official Site &nearr;</a>
                <a class="btn-ha-profile" href="../pages/{slug_b}.html">View Company Info</a>
              </div>
            </div>
          </div>
        </header>
        <div class="compare-rows">
    '''
    
    for idx, r in enumerate(rows):
        attr = r['attribute']
        val_a = format_ha_val(r[name_a])
        val_b = format_ha_val(r[name_b])
        is_last = (idx == len(rows) - 1)
        
        cls_val_a = "val-col winner" if is_win_a else "val-col"
        cls_val_b = "val-col winner" if is_win_b else "val-col"
        
        if is_last:
            if is_win_a: cls_val_a += " last-winner"
            if is_win_b: cls_val_b += " last-winner"
            
        html += f'''
          <div class="compare-row">
            <div class="row-name">
              <span class="row-dot"></span>
              <span class="row-label">{attr}</span>
            </div>
            <div class="values">
              <div class="{cls_val_a}">{val_a}</div>
              <div class="{cls_val_b}">{val_b}</div>
            </div>
          </div>
        '''
        
    html += '''
        </div>
      </div>
    </div>
    '''
    return html

def render_comparison_html(comp_data):
    ca = comp_data['company_a']
    cb = comp_data['company_b']
    name_a = ca['name']
    name_b = cb['name']
    slug_a = ca['slug']
    slug_b = cb['slug']
    winner = comp_data['overall_winner']
    verdict = comp_data['verdict']

    is_win_a = ca['is_winner']
    is_win_b = cb['is_winner']

    price_a = ca['price']
    price_b = cb['price']

    # Get rich portfolio metadata for direct official URLs, logos, and reviews
    meta_a = get_company_portfolio_data(slug_a, name_a)
    meta_b = get_company_portfolio_data(slug_b, name_b)

    logo_a = meta_a.get('logo_url', f"https://logo.clearbit.com/{meta_a.get('domain', 'example.com')}")
    fav_a = meta_a.get('favicon_url', f"https://www.google.com/s2/favicons?domain={meta_a.get('domain', 'example.com')}&sz=128")
    logo_b = meta_b.get('logo_url', f"https://logo.clearbit.com/{meta_b.get('domain', 'example.com')}")
    fav_b = meta_b.get('favicon_url', f"https://www.google.com/s2/favicons?domain={meta_b.get('domain', 'example.com')}&sz=128")

    winner_slug = slug_a if is_win_a else slug_b
    runner_slug = slug_b if is_win_a else slug_a
    runner_up = name_b if is_win_a else name_a

    # Pros & Cons
    pros_a = "".join([f'<li><span class="pro-dot">✓</span><span>{p}</span></li>' for p in ca['pros']])
    cons_a = "".join([f'<li><span class="con-dot">✕</span><span>{c}</span></li>' for c in ca['cons']])
    pros_b = "".join([f'<li><span class="pro-dot">✓</span><span>{p}</span></li>' for p in cb['pros']])
    cons_b = "".join([f'<li><span class="con-dot">✕</span><span>{c}</span></li>' for c in cb['cons']])

    # Section Tables
    plan_winner = comp_data['plan_comparison']['winner']
    plan_table_html = build_ha_compare_table(
        comp_data['plan_comparison']['rows'],
        name_a, name_b, slug_a, slug_b, price_a, price_b, plan_winner,
        meta_a, meta_b, category_title="Plan Feature"
    )

    perf_winner = comp_data['performance_comparison']['winner']
    perf_table_html = build_ha_compare_table(
        comp_data['performance_comparison']['rows'],
        name_a, name_b, slug_a, slug_b, price_a, price_b, perf_winner,
        meta_a, meta_b, category_title="Hardware & Speed"
    )

    supp_winner = comp_data['support_comparison']['winner']
    supp_table_html = build_ha_compare_table(
        comp_data['support_comparison']['rows'],
        name_a, name_b, slug_a, slug_b, price_a, price_b, supp_winner,
        meta_a, meta_b, category_title="Support Channel / SLA"
    )

    # Top Quick Summary Table (6 key comparison metrics)
    quick_rows = [
        {"attribute": "Starting Price", name_a: price_a, name_b: price_b},
        {"attribute": "Overall Rating", name_a: f"{ca['rating']} / 5.0", name_b: f"{cb['rating']} / 5.0"},
        {"attribute": "Server Performance", name_a: comp_data['performance_comparison']['rows'][0][name_a], name_b: comp_data['performance_comparison']['rows'][0][name_b]},
        {"attribute": "Web Server Architecture", name_a: comp_data['performance_comparison']['rows'][1][name_a], name_b: comp_data['performance_comparison']['rows'][1][name_b]},
        {"attribute": "Customer Support", name_a: comp_data['support_comparison']['rows'][0][name_a], name_b: comp_data['support_comparison']['rows'][0][name_b]},
        {"attribute": "Money-Back Guarantee", name_a: comp_data['plan_comparison']['rows'][8][name_a], name_b: comp_data['plan_comparison']['rows'][8][name_b]}
    ]
    quick_table_html = build_ha_compare_table(
        quick_rows, name_a, name_b, slug_a, slug_b, price_a, price_b, winner,
        meta_a, meta_b, category_title="Key Metric"
    )

    # Build FAQ Schema JSON-LD
    import json
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f['question'],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f['answer']
                }
            } for f in comp_data.get('faqs', [])
        ]
    }
    faq_json_ld = json.dumps(faq_schema, ensure_ascii=False)

    # FAQs
    faq_html = ""
    for idx, f in enumerate(comp_data['faqs'], 1):
        is_open = 'open' if idx == 1 else ''
        faq_html += f"""
        <details class="ha-faq-item" {is_open}>
            <summary class="ha-faq-question">
                <h3 class="ha-faq-title">{f['question']}</h3>
                <span class="ha-faq-chevron">
                    <svg viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"/></svg>
                </span>
            </summary>
            <div class="ha-faq-answer">
                <p>{f['answer']}</p>
            </div>
        </details>
        """

    # Customer Reviews for Company A & B
    reviews_a = meta_a.get('reviews', [])[:2]
    reviews_b = meta_b.get('reviews', [])[:2]

    def render_review_box(rev, host_name):
        stars_html = "".join(['★' for _ in range(rev['rating'])]) + "".join(['☆' for _ in range(5 - rev['rating'])])
        return f"""
        <div class="comp-review-item">
            <div class="rev-hdr">
                <div class="rev-author-badge" style="background-color:{rev['avatar_color']};">{rev['author'][:1]}</div>
                <div>
                    <div style="font-weight:700; color:var(--ha-slate-900); font-size:0.95rem;">{rev['author']} <span class="verified-tag">✓ Verified User</span></div>
                    <div style="font-size:0.8rem; color:var(--ha-slate-500);">{rev['role']} &bull; {rev['country']}</div>
                </div>
            </div>
            <div style="margin:0.5rem 0; display:flex; align-items:center; gap:0.5rem;">
                <span style="color:var(--ha-star); font-size:1rem; letter-spacing:1px;">{stars_html}</span>
                <span style="font-size:0.8rem; color:var(--ha-slate-600); font-weight:600;">{rev['plan_used']}</span>
            </div>
            <h4 class="comp-rev-headline" style="font-weight:700; font-size:0.95rem; margin-bottom:0.35rem; color:var(--ha-slate-900);">{rev['headline']}</h4>
            <p style="font-size:0.875rem; color:var(--ha-slate-700); line-height:1.6; margin-bottom:0.25rem;">{rev['body']}</p>
        </div>
        """

    revs_html_a = "".join([render_review_box(r, name_a) for r in reviews_a])
    revs_html_b = "".join([render_review_box(r, name_b) for r in reviews_b])

    # Related comparisons pills
    related_pills = f"""
    <a href="{slug_a}-vs-hostinger.html" class="ha-chip">{name_a} vs Hostinger</a>
    <a href="{slug_a}-vs-bluehost.html" class="ha-chip">{name_a} vs Bluehost</a>
    <a href="{slug_a}-vs-siteground.html" class="ha-chip">{name_a} vs SiteGround</a>
    <a href="{slug_b}-vs-hostinger.html" class="ha-chip">{name_b} vs Hostinger</a>
    <a href="{slug_b}-vs-bluehost.html" class="ha-chip">{name_b} vs Bluehost</a>
    <a href="{slug_b}-vs-siteground.html" class="ha-chip">{name_b} vs SiteGround</a>
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name_a} vs {name_b} (2026): Which Web Host Actually Wins?</title>
    <meta name="description" content="Side-by-side technical benchmark comparing {name_a} and {name_b}. Real server speed, plan pricing, uptime reliability, and 24/7 customer support compared.">
    <link rel="canonical" href="{slug_a}-vs-{slug_b}.html">
    <script type="application/ld+json">
    {faq_json_ld}
    </script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --ha-font: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --ha-blue: #1d4ed8;
            --ha-blue-hover: #1e40af;
            --ha-blue-light: #eff6ff;
            --ha-blue-border: #bfdbfe;
            --ha-orange: #f97316;
            --ha-green: #15803d;
            --ha-green-light: #dcfce7;
            --ha-red: #b91c1c;
            --ha-red-light: #fee2e2;
            --ha-star: #eab308;
            --ha-slate-900: #0f172a;
            --ha-slate-800: #1e293b;
            --ha-slate-700: #334155;
            --ha-slate-600: #475569;
            --ha-slate-500: #64748b;
            --ha-slate-200: #e2e8f0;
            --ha-bg: #f8fafc;
            --ha-white: #ffffff;
            --ha-max-w: 1180px;
            --ha-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
            --ha-shadow-lg: 0 10px 30px -5px rgba(15, 23, 42, 0.08), 0 4px 10px -2px rgba(15, 23, 42, 0.04);
        }}

        /* Reset & Base */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        html {{ scroll-behavior: smooth; font-size: 16px; -webkit-text-size-adjust: 100%; }}
        body {{
            font-family: var(--ha-font);
            background-color: var(--ha-bg);
            color: var(--ha-slate-900);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }}

        /* Top Bar Header */
        .ha-topbar {{
            background: var(--ha-white);
            border-bottom: 1px solid var(--ha-slate-200);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .ha-topbar-inner {{
            max-width: var(--ha-max-w);
            margin: 0 auto;
            padding: 0.85rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .ha-brand {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            text-decoration: none;
            color: var(--ha-slate-900);
            font-weight: 800;
            font-size: 1.25rem;
            letter-spacing: -0.02em;
        }}
        .ha-brand-pill {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: white;
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
        }}
        .ha-crumb {{
            font-size: 0.875rem;
            color: var(--ha-slate-500);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .ha-crumb a {{ color: var(--ha-slate-700); text-decoration: none; font-weight: 500; }}
        .ha-crumb a:hover {{ color: var(--ha-blue); }}

        /* Rounded Capsule Navigation Bar */
        .capsule-nav-wrapper {{
            position: sticky;
            top: 54px;
            z-index: 90;
            display: flex;
            justify-content: center;
            padding: 0.65rem 1rem;
            background: rgba(248, 250, 252, 0.88);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
            margin-bottom: 1.5rem;
        }}
        .capsule-nav-bar {{
            background: #ffffff;
            padding: 4px 6px;
            border-radius: 9999px;
            display: inline-flex;
            align-items: center;
            gap: 3px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(0, 0, 0, 0.04);
            overflow-x: auto;
            max-width: 100%;
            scrollbar-width: none;
            border: 1px solid #e2e8f0;
        }}
        .capsule-nav-bar::-webkit-scrollbar {{ display: none; }}
        .capsule-pill {{
            color: #1e293b;
            font-weight: 600;
            font-size: 0.84rem;
            padding: 0.45rem 1rem;
            border-radius: 9999px;
            text-decoration: none;
            white-space: nowrap;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: inline-block;
            border: 1px solid transparent;
        }}
        .capsule-pill:hover {{
            color: #1d4ed8;
            background: #f1f5f9;
        }}
        .capsule-pill.active {{
            background: #2563eb;
            color: #ffffff;
            font-weight: 700;
            box-shadow: 0 3px 12px rgba(37, 99, 235, 0.4);
            border-color: #2563eb;
        }}

        /* Page Wrapper */
        .ha-container {{
            max-width: var(--ha-max-w);
            margin: 0 auto;
            padding: 0.5rem 1.5rem 5rem;
        }}

        /* Scroll margin for smooth anchor alignment */
        section[id], .bottom-line-card, .ha-h2 {{
            scroll-margin-top: 115px;
        }}

        /* Article Header */
        .ha-header {{
            margin-bottom: 2.25rem;
            text-align: center;
        }}
        .ha-tag-wrapper {{
            display: flex;
            justify-content: center;
            margin-bottom: 0.85rem;
        }}
        .ha-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--ha-blue);
            background: var(--ha-blue-light);
            border: 1px solid var(--ha-blue-border);
            font-size: 0.775rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 0.35rem 0.95rem;
            border-radius: 9999px;
            box-shadow: 0 2px 6px rgba(29, 78, 216, 0.06);
        }}
        .ha-tag-dot {{
            width: 7px;
            height: 7px;
            background: var(--ha-blue);
            border-radius: 50%;
            display: inline-block;
        }}
        .ha-title {{
            font-size: clamp(2rem, 3.6vw, 2.75rem);
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.22;
            color: var(--ha-slate-900);
            margin-bottom: 0.95rem;
            max-width: 950px;
            margin-left: auto;
            margin-right: auto;
        }}
        .ha-byline {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            font-size: 0.88rem;
            color: var(--ha-slate-500);
            flex-wrap: wrap;
        }}
        .ha-badge-lab {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: var(--ha-blue);
            color: white;
            font-size: 0.725rem;
            font-weight: 800;
            padding: 0.22rem 0.6rem;
            border-radius: 6px;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}
        .ha-badge-lab svg {{
            width: 12px;
            height: 12px;
        }}
        .ha-fact {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            color: var(--ha-green);
            font-weight: 700;
        }}
        .ha-fact svg {{
            width: 14px;
            height: 14px;
        }}

        /* ========================================================
           HERO SHOWDOWN BATTLE ARENA (Side-by-Side Brand Cards)
           ======================================================== */
        .showdown-arena {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 1.5rem;
            align-items: stretch;
            margin-bottom: 2.5rem;
        }}
        .battle-host-card {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: var(--ha-shadow);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            transition: all 0.2s ease;
        }}
        .battle-host-card.is-winner {{
            border: 2px solid #22c55e;
            box-shadow: 0 10px 30px -5px rgba(34, 197, 94, 0.2);
            background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
        }}
        .winner-crown-tag {{
            position: absolute;
            top: -14px;
            right: 20px;
            background: linear-gradient(135deg, #16a34a, #15803d);
            color: white;
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            box-shadow: 0 4px 10px rgba(22, 163, 74, 0.3);
        }}
        .battle-logo-wrap {{
            width: 88px;
            height: 88px;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px;
            margin-bottom: 1.15rem;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
        }}
        .battle-logo-img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .battle-name {{
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--ha-slate-900);
            margin-bottom: 0.25rem;
            line-height: 1.2;
        }}
        .battle-rating-row {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        .stars-gold {{ color: var(--ha-star); letter-spacing: 2px; }}
        .battle-price-box {{
            background: var(--ha-slate-50);
            border: 1px solid var(--ha-slate-200);
            border-radius: 8px;
            padding: 0.85rem 1rem;
            margin-bottom: 1.25rem;
        }}
        .battle-price-box .lbl {{ font-size: 0.775rem; color: var(--ha-slate-500); font-weight: 700; text-transform: uppercase; }}
        .battle-price-box .val {{ font-size: 1.35rem; font-weight: 800; color: var(--ha-slate-900); }}
        .battle-btn-group {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .btn-battle-official {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: white;
            text-align: center;
            padding: 0.8rem;
            border-radius: 8px;
            font-weight: 700;
            text-decoration: none;
            font-size: 0.95rem;
            transition: all 0.15s;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        }}
        .btn-battle-official:hover {{
            background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
            transform: translateY(-1px);
        }}
        .btn-battle-profile {{
            background: var(--ha-white);
            color: var(--ha-slate-700);
            border: 1px solid var(--ha-slate-200);
            text-align: center;
            padding: 0.65rem;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            font-size: 0.875rem;
            transition: all 0.15s;
        }}
        .btn-battle-profile:hover {{ background: var(--ha-slate-50); border-color: var(--ha-slate-500); }}

        /* VS Center Pillar */
        .battle-vs-center {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 0.85rem;
            padding: 1rem;
        }}
        .vs-circle-large {{
            width: 68px;
            height: 68px;
            border-radius: 50%;
            background: #0f172a;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.35rem;
            font-weight: 900;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.3);
            border: 3px solid #ffffff;
        }}
        .vs-verdict-chip {{
            font-size: 0.85rem;
            font-weight: 800;
            color: var(--ha-slate-900);
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            padding: 0.45rem 0.95rem;
            border-radius: 9999px;
            box-shadow: var(--ha-shadow);
            white-space: nowrap;
        }}

        /* Table Logo Box in Header */
        .table-brand-logo-card {{
            width: 56px;
            height: 56px;
            border-radius: 10px;
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 6px;
            margin: 0 auto 0.65rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04);
        }}
        .table-brand-logo-img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}

        /* HostAdvice Headings */
        .ha-h2 {{
            font-size: 1.65rem;
            font-weight: 800;
            color: var(--ha-slate-900);
            letter-spacing: -0.025em;
            margin: 3rem 0 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            scroll-margin-top: 100px;
        }}
        .ha-h2-bar {{
            display: inline-block;
            width: 5px;
            height: 24px;
            background: var(--ha-blue);
            border-radius: 3px;
        }}
        .ha-sec-desc {{
            font-size: 1.05rem;
            color: var(--ha-slate-600);
            line-height: 1.65;
            margin-bottom: 1.25rem;
        }}

        /* HostAdvice Tip Box (.text-note.tip) */
        .text-note.tip {{
            background: var(--ha-blue-light);
            border: 1px solid var(--ha-blue-border);
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin: 1.75rem 0;
            color: var(--ha-slate-900);
        }}
        .text-note.tip header {{
            color: var(--ha-blue);
            font-weight: 800;
            font-size: 1rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .tip-svg {{ width: 20px; height: 20px; }}
        .text-note.tip p {{
            font-size: 0.975rem;
            line-height: 1.6;
            color: var(--ha-slate-700);
        }}

        /* Comparison Table */
        .compare-table-wrap {{
            padding: 1.25rem 0 2.25rem;
            width: 100%;
            overflow-x: auto;
        }}
        .compare-table {{
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            overflow: hidden;
            background: var(--ha-white);
            box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.08), 0 4px 12px rgba(15, 23, 42, 0.03);
            min-width: 640px;
        }}
        .compare-table header {{
            display: grid;
            grid-template-columns: 1.15fr 2fr;
            background: var(--ha-white);
            border-bottom: 2px solid #e2e8f0;
        }}
        .compare-table header .overview {{
            padding: 1.75rem 1.75rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            border-right: 1px solid #e2e8f0;
        }}
        .overview-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            background: #e2e8f0;
            color: #475569;
            font-size: 0.68rem;
            font-weight: 800;
            padding: 0.2rem 0.55rem;
            border-radius: 4px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            align-self: flex-start;
        }}
        .overview-svg {{
            width: 12px;
            height: 12px;
            color: #64748b;
        }}
        .overview-title {{
            font-size: 1.2rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.25;
            margin: 0 0 0.25rem 0;
        }}
        .overview-sub {{
            font-size: 0.8rem;
            color: #64748b;
            font-weight: 500;
        }}
        .hosting-info {{
            display: flex;
        }}
        .hosting-col {{
            flex: 1 1 50%;
            padding: 1.75rem 1.5rem 1.5rem;
            text-align: center;
            border-left: 1px solid #e2e8f0;
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            background: #ffffff;
            transition: background 0.2s ease;
        }}
        .hosting-col.winner {{
            border-left: 2px solid #2563eb;
            border-right: 2px solid #2563eb;
            background: linear-gradient(180deg, #f0f7ff 0%, #ffffff 100%);
        }}
        .winner-ribbon {{
            position: absolute;
            top: 0;
            left: -2px;
            right: -2px;
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 800;
            padding: 0.35rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            letter-spacing: 0.06em;
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
        }}
        .runner-ribbon {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            background: #f8fafc;
            color: #64748b;
            font-size: 0.68rem;
            font-weight: 700;
            padding: 0.3rem 0;
            display: flex;
            align-items: center;
            justify-content: center;
            letter-spacing: 0.06em;
            border-bottom: 1px solid #e2e8f0;
        }}
        .trophy-svg {{
            width: 14px;
            height: 14px;
            color: #fbbf24;
        }}
        .table-brand-logo-card {{
            width: 130px;
            height: 58px;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 6px 12px;
            margin: 1.1rem auto 0.75rem;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
        }}
        .table-brand-logo-img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .brand-title-link {{
            font-size: 1.3rem;
            font-weight: 800;
            color: #0f172a;
            text-decoration: none;
            display: block;
            margin-bottom: 0.35rem;
            transition: color 0.15s;
        }}
        .brand-title-link:hover {{
            color: #2563eb;
        }}
        .brand-price-tag {{
            display: inline-flex;
            align-items: baseline;
            gap: 0.35rem;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 0.25rem 0.85rem;
            border-radius: 9999px;
            margin-bottom: 1.1rem;
        }}
        .hosting-col.winner .brand-price-tag {{
            background: #e0f2fe;
            border-color: #bae6fd;
        }}
        .price-prefix {{
            font-size: 0.75rem;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .price-amount {{
            font-size: 1.05rem;
            font-weight: 800;
            color: #0f172a;
        }}
        .hosting-col.winner .price-amount {{
            color: #0369a1;
        }}
        .btn-group-col {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            width: 100%;
            max-width: 220px;
        }}
        .btn-ha-official {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: #ffffff !important;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.875rem;
            padding: 0.6rem 1.1rem;
            border-radius: 8px;
            transition: all 0.15s ease;
            text-align: center;
            box-shadow: 0 3px 10px rgba(37, 99, 235, 0.25);
            border: 1px solid transparent;
        }}
        .btn-ha-official:hover {{
            background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
        }}
        .btn-ha-profile {{
            background: #ffffff;
            color: #334155 !important;
            border: 1px solid #cbd5e1;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.825rem;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.15s ease;
            text-align: center;
        }}
        .btn-ha-profile:hover {{
            background: #f8fafc;
            border-color: #94a3b8;
            color: #0f172a !important;
            transform: translateY(-1px);
        }}

        /* Table Rows */
        .compare-rows {{ display: flex; flex-direction: column; }}
        .compare-row {{
            display: grid;
            grid-template-columns: 1.15fr 2fr;
            border-top: 1px solid #e2e8f0;
            transition: background-color 0.15s ease;
        }}
        .compare-row:nth-child(even) {{
            background: #fbfcfe;
        }}
        .compare-row:nth-child(odd) {{
            background: #ffffff;
        }}
        .compare-row:hover {{
            background: #f1f5f9;
        }}
        .row-name {{
            padding: 1.05rem 1.75rem;
            font-weight: 600;
            font-size: 0.94rem;
            color: #1e293b;
            display: flex;
            align-items: center;
            gap: 0.65rem;
            border-right: 1px solid #e2e8f0;
        }}
        .row-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #cbd5e1;
            flex-shrink: 0;
            transition: background 0.15s;
        }}
        .compare-row:hover .row-dot {{
            background: #2563eb;
            transform: scale(1.2);
        }}
        .row-label {{
            line-height: 1.35;
        }}
        .values {{
            display: flex;
        }}
        .val-col {{
            flex: 1 1 50%;
            padding: 1.05rem 1.5rem;
            border-left: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 0.94rem;
            color: #334155;
        }}
        .val-col.winner {{
            border-left: 2px solid #2563eb;
            border-right: 2px solid #2563eb;
            background-color: rgba(37, 99, 235, 0.035);
            font-weight: 600;
            color: #0f172a;
        }}
        .val-col.last-winner {{
            border-bottom: 2px solid #2563eb;
        }}

        /* Enhanced Values Badges */
        .ha-val-pill {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.3rem 0.85rem;
            border-radius: 9999px;
            font-size: 0.86rem;
            font-weight: 600;
            line-height: 1.25;
        }}
        .ha-val-yes {{
            background: #ecfdf5;
            color: #047857;
            border: 1px solid #a7f3d0;
        }}
        .ha-val-no {{
            background: #fef2f2;
            color: #b91c1c;
            border: 1px solid #fecaca;
        }}
        .ha-icon-check {{
            width: 15px;
            height: 15px;
            color: #059669;
            flex-shrink: 0;
        }}
        .ha-icon-cross {{
            width: 15px;
            height: 15px;
            color: #dc2626;
            flex-shrink: 0;
        }}
        .ha-val-text {{
            font-weight: 600;
            color: #1e293b;
        }}

        /* Pros & Cons Section */
        .pros-cons-wrap {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin: 1.5rem 0 2.5rem;
        }}
        .pro-con-card {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-radius: 12px;
            padding: 1.75rem 2rem;
            box-shadow: var(--ha-shadow);
        }}
        .pro-con-head {{
            font-size: 1.2rem;
            font-weight: 800;
            color: var(--ha-slate-900);
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid var(--ha-slate-200);
        }}
        .pro-con-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
        }}
        .pro-con-list li {{
            display: flex;
            align-items: flex-start;
            gap: 0.65rem;
            font-size: 0.95rem;
            color: var(--ha-slate-700);
            line-height: 1.5;
        }}
        .pro-dot {{ color: var(--ha-green); font-weight: 900; font-size: 1.1rem; line-height: 1.3; }}
        .con-dot {{ color: #dc2626; font-weight: 900; font-size: 1.1rem; line-height: 1.3; }}

        /* Final Verdict Banner */
        .bottom-line-card {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-left: 5px solid var(--ha-blue);
            border-radius: 12px;
            padding: 2.25rem;
            margin: 2.5rem 0;
            box-shadow: var(--ha-shadow);
        }}
        .verdict-header-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }}
        .verdict-title {{
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--ha-slate-900);
        }}
        .verdict-winner-pill {{
            background: var(--ha-green-light);
            color: var(--ha-green);
            font-weight: 800;
            font-size: 0.8rem;
            padding: 0.35rem 0.85rem;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .verdict-body-text {{
            font-size: 1.05rem;
            color: var(--ha-slate-700);
            line-height: 1.7;
            margin-bottom: 1.5rem;
        }}
        .verdict-action-row {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .btn-verdict-main {{
            display: inline-block;
            background: var(--ha-blue);
            color: white;
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            padding: 0.75rem 1.6rem;
            border-radius: 6px;
            transition: background 0.15s;
        }}
        .btn-verdict-main:hover {{ background: var(--ha-blue-hover); }}
        .btn-verdict-secondary {{
            display: inline-block;
            background: #ffffff;
            color: var(--ha-slate-700);
            border: 1px solid var(--ha-slate-200);
            text-decoration: none;
            font-weight: 700;
            font-size: 0.95rem;
            padding: 0.75rem 1.6rem;
            border-radius: 6px;
            transition: all 0.15s;
        }}
        .btn-verdict-secondary:hover {{ background: #f8fafc; border-color: #cbd5e1; }}

        /* FAQs */
        .ha-faqs {{ margin: 1.5rem 0 3rem; }}
        .ha-faq-item {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-radius: 8px;
            margin-bottom: 0.85rem;
            overflow: hidden;
            transition: border-color 0.15s;
        }}
        .ha-faq-item[open] {{ border-color: #60a5fa; }}
        .ha-faq-question {{
            padding: 1.15rem 1.5rem;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--ha-slate-900);
            cursor: pointer;
            list-style: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
        }}
        .ha-faq-question::-webkit-details-marker {{ display: none; }}
        .ha-faq-chevron {{
            width: 20px;
            height: 20px;
            color: var(--ha-slate-500);
            transition: transform 0.2s ease;
        }}
        .ha-faq-item[open] .ha-faq-chevron {{ transform: rotate(180deg); color: var(--ha-blue); }}
        .ha-faq-answer {{
            padding: 1rem 1.5rem 1.4rem;
            border-top: 1px solid var(--ha-slate-200);
            background: #fafbfc;
            color: var(--ha-slate-700);
            line-height: 1.65;
            font-size: 0.975rem;
        }}

        /* ========================================================
           CUSTOMER REVIEWS COMPARISON SECTION
           ======================================================== */
        .comp-reviews-section {{
            margin-top: 3.5rem;
            padding-top: 2rem;
            border-top: 2px solid var(--ha-slate-200);
        }}
        .comp-reviews-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}
        .comp-review-col {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-radius: 14px;
            padding: 1.75rem;
            box-shadow: var(--ha-shadow);
        }}
        .comp-review-item {{
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            border-radius: 10px;
            padding: 1.25rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.02);
        }}
        .comp-review-item:last-child {{ margin-bottom: 0; }}
        .rev-hdr {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }}
        .rev-author-badge {{
            width: 38px;
            height: 38px;
            border-radius: 50%;
            color: white;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 1rem;
        }}
        .verified-tag {{
            font-size: 0.725rem;
            color: var(--ha-green);
            background: var(--ha-green-light);
            padding: 0.15rem 0.45rem;
            border-radius: 9999px;
            font-weight: 700;
            margin-left: 0.35rem;
        }}

        /* Related Comparisons */
        .ha-related-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin: 1.25rem 0 3rem;
        }}
        .ha-chip {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            padding: 0.55rem 1.1rem;
            border-radius: 9999px;
            text-decoration: none;
            color: var(--ha-slate-700);
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.15s;
        }}
        .ha-chip:hover {{
            background: var(--ha-blue);
            color: white;
            border-color: var(--ha-blue);
        }}

        /* Responsive Breakpoints */
        @media (max-width: 850px) {{
            .showdown-arena {{ grid-template-columns: 1fr; }}
            .battle-vs-center {{ margin: 0 auto; }}
            .comp-reviews-grid {{ grid-template-columns: 1fr; }}
            .pros-cons-wrap {{ grid-template-columns: 1fr; }}
            .compare-table header {{ display: block; }}
            .compare-table header .overview {{ border-bottom: 1px solid var(--ha-slate-200); padding: 1rem 1.25rem; border-right: none; }}
            .compare-row {{ display: block; }}
            .row-name {{ font-weight: 700; background: #f8fafc; border-bottom: 1px solid var(--ha-slate-200); padding: 0.75rem 1.25rem; border-right: none; }}
            .values {{ display: flex; }}
            .val-col {{ padding: 0.85rem 1rem; }}
            .ha-container {{ padding: 0.5rem 1rem 3.5rem; }}
        }}
    </style>
</head>
<body>

    <!-- Site Header -->
    <header class="ha-topbar">
        <div class="ha-topbar-inner">
            <a href="compare_hub.html" class="ha-brand">
                <span class="ha-brand-pill">HOSTING</span>
                <span>CompareAdvice</span>
            </a>
            <div class="ha-crumb">
                <a href="compare_hub.html">Home</a> &rsaquo; 
                <a href="../pages/{slug_a}.html">{name_a}</a> vs 
                <a href="../pages/{slug_b}.html">{name_b}</a>
            </div>
        </div>
    </header>

    <!-- Static Rounded Capsule Navigation Bar -->
    <div class="capsule-nav-wrapper">
        <nav class="capsule-nav-bar">
            <a href="#summary" class="capsule-pill active">Summary</a>
            <a href="#plans" class="capsule-pill">Pricing &amp; Plans</a>
            <a href="#performance" class="capsule-pill">Server Speed</a>
            <a href="#support" class="capsule-pill">Customer Support</a>
            <a href="#pros-cons" class="capsule-pill">Pros &amp; Cons</a>
            <a href="#verdict" class="capsule-pill">Final Verdict</a>
            <a href="#faqs" class="capsule-pill">FAQs</a>
            <a href="#reviews" class="capsule-pill">User Reviews</a>
            <a href="../pages/index.html" class="capsule-pill">All 55 Hosts</a>
        </nav>
    </div>

    <!-- Main Container -->
    <main class="ha-container">

        <!-- Article Header -->
        <header class="ha-header">
            <h1 class="ha-title">{name_a} vs {name_b} 2026: Which Web Host Actually Wins?</h1>
        </header>

        <!-- ========================================================
             HERO SHOWDOWN BATTLE ARENA (Side-by-Side Brand Cards)
             ======================================================== -->
        <section class="showdown-arena">
            <!-- Host A Card -->
            <div class="battle-host-card {'is-winner' if is_win_a else ''}">
                {f'<span class="winner-crown-tag">🏆 OVERALL WINNER</span>' if is_win_a else ''}
                <div>
                    <div class="battle-logo-wrap">
                        <img src="{logo_a}" alt="{name_a} Logo" class="battle-logo-img" onerror="this.onerror=null; this.src='{fav_a}';">
                    </div>
                    <div class="battle-name">{name_a}</div>
                    <div class="battle-rating-row">
                        <span class="stars-gold">★★★★★</span>
                        <span style="font-weight:800;">{ca['rating']} / 5.0</span>
                    </div>
                </div>

                <div>
                    <div class="battle-price-box">
                        <div class="lbl">Starting Promotional Rate</div>
                        <div class="val">{price_a}</div>
                    </div>
                    <div class="battle-btn-group">
                        <a href="{meta_a.get('website', '#')}" target="_blank" rel="noopener" class="btn-battle-official">Visit {name_a} Official &rarr;</a>
                        <a href="../pages/{slug_a}.html" class="btn-battle-profile">View {name_a} Full Specs</a>
                    </div>
                </div>
            </div>

            <!-- VS Center Pillar -->
            <div class="battle-vs-center">
                <div class="vs-circle-large">VS</div>
                <div class="vs-verdict-chip">Winner: <strong style="color:var(--ha-green);">{winner}</strong></div>
            </div>

            <!-- Host B Card -->
            <div class="battle-host-card {'is-winner' if is_win_b else ''}">
                {f'<span class="winner-crown-tag">🏆 OVERALL WINNER</span>' if is_win_b else ''}
                <div>
                    <div class="battle-logo-wrap">
                        <img src="{logo_b}" alt="{name_b} Logo" class="battle-logo-img" onerror="this.onerror=null; this.src='{fav_b}';">
                    </div>
                    <div class="battle-name">{name_b}</div>
                    <div class="battle-rating-row">
                        <span class="stars-gold">★★★★★</span>
                        <span style="font-weight:800;">{cb['rating']} / 5.0</span>
                    </div>
                </div>

                <div>
                    <div class="battle-price-box">
                        <div class="lbl">Starting Promotional Rate</div>
                        <div class="val">{price_b}</div>
                    </div>
                    <div class="battle-btn-group">
                        <a href="{meta_b.get('website', '#')}" target="_blank" rel="noopener" class="btn-battle-official">Visit {name_b} Official &rarr;</a>
                        <a href="../pages/{slug_b}.html" class="btn-battle-profile">View {name_b} Full Specs</a>
                    </div>
                </div>
            </div>
        </section>

        <!-- Quick Summary Section -->
        <section id="summary">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>{name_a} vs {name_b}: Quick Comparison Summary &amp; Winner</h2>
            <p class="ha-sec-desc"><strong>{winner}</strong> wins this head-to-head evaluation. {verdict}</p>

            <!-- Quick High-Level Comparison Table -->
            {quick_table_html}

            <!-- Tip Box -->
            <div class="text-note tip">
                <header>
                    <svg class="tip-svg" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.001z"/>
                    </svg>
                    <span>Editorial Recommendation</span>
                </header>
                <p>Choose <strong><a href="../pages/{slug_a}.html" style="color:var(--ha-blue); font-weight:700;">{name_a}</a></strong> if your website needs {ca['pros'][0].lower()}. Choose <strong><a href="../pages/{slug_b}.html" style="color:var(--ha-blue); font-weight:700;">{name_b}</a></strong> if your stack benefits from {cb['pros'][0].lower()}.</p>
            </div>
        </section>

        <!-- Section 1: Prices & Plans Comparison -->
        <section id="plans">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>{name_a} vs {name_b}: Plans and Pricing Comparison</h2>
            <p class="ha-sec-desc">{comp_data['plan_comparison']['verdict']}</p>
            {plan_table_html}
        </section>

        <!-- Section 2: Website Performance & Server Infrastructure -->
        <section id="performance">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>{name_a} vs {name_b}: Server Speed, Uptime &amp; Infrastructure</h2>
            <p class="ha-sec-desc">{comp_data['performance_comparison']['verdict']}</p>
            {perf_table_html}
        </section>

        <!-- Section 3: Customer Support Quality & SLA -->
        <section id="support">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>{name_a} vs {name_b}: Customer Support Quality &amp; SLA Breakdown</h2>
            <p class="ha-sec-desc">{comp_data['support_comparison']['verdict']}</p>
            {supp_table_html}
        </section>

        <!-- Section 4: Strengths & Weaknesses (Pros & Cons) -->
        <section id="pros-cons">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>{name_a} vs {name_b}: Strengths &amp; Weaknesses (Pros &amp; Cons)</h2>
            <div class="pros-cons-wrap">
                <div class="pro-con-card">
                    <h3 class="pro-con-head"><a href="../pages/{slug_a}.html" style="color:inherit; text-decoration:none;">{name_a}</a> Pros &amp; Cons</h3>
                    <ul class="pro-con-list">
                        {pros_a}
                        {cons_a}
                    </ul>
                </div>
                <div class="pro-con-card">
                    <h3 class="pro-con-head"><a href="../pages/{slug_b}.html" style="color:inherit; text-decoration:none;">{name_b}</a> Pros &amp; Cons</h3>
                    <ul class="pro-con-list">
                        {pros_b}
                        {cons_b}
                    </ul>
                </div>
            </div>
        </section>

        <!-- Section 5: Final Verdict -->
        <section id="verdict" class="bottom-line-card">
            <div class="verdict-header-row">
                <h2 class="verdict-title">Final Verdict: Which One Should You Choose &mdash; {name_a} or {name_b}?</h2>
                <span class="verdict-winner-pill">Winner: {winner}</span>
            </div>
            <p class="verdict-body-text">{verdict}</p>
            <div class="verdict-action-row">
                <a href="../pages/{winner_slug}.html" class="btn-verdict-main">View {winner} Portfolio &amp; Info &rarr;</a>
                <a href="../pages/{runner_slug}.html" class="btn-verdict-secondary">View {runner_up} Portfolio &rarr;</a>
            </div>
        </section>

        <!-- Section 6: FAQs -->
        <section id="faqs" class="ha-faqs">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>Frequently Asked Questions: {name_a} vs {name_b}</h2>
            <p class="ha-sec-desc">Common questions and expert answers when comparing {name_a} and {name_b}:</p>
            {faq_html}
        </section>

        <!-- ========================================================
             Section 7: CUSTOMER REVIEWS COMPARISON SECTION
             ======================================================== -->
        <section id="reviews" class="comp-reviews-section">
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>{name_a} vs {name_b}: Verified Customer Reviews &amp; Ratings</h2>
            <p class="ha-sec-desc">Real, verified customer testimonials comparing firsthand reliability, customer support, and value between {name_a} and {name_b}:</p>

            <div class="comp-reviews-grid">
                <!-- Host A Reviews Column -->
                <div class="comp-review-col">
                    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.25rem; padding-bottom:0.75rem; border-bottom:1px solid var(--ha-slate-200);">
                        <img src="{logo_a}" alt="{name_a} Logo" style="width:36px; height:36px; object-fit:contain;" onerror="this.onerror=null; this.src='{fav_a}';">
                        <div>
                            <h3 style="font-size:1.15rem; font-weight:800; color:var(--ha-slate-900);">{name_a} Customer Feedback</h3>
                            <div style="font-size:0.8rem; color:var(--ha-slate-500);">Rated {ca['rating']} / 5.0 overall</div>
                        </div>
                    </div>
                    {revs_html_a}
                </div>

                <!-- Host B Reviews Column -->
                <div class="comp-review-col">
                    <div style="display:flex; align-items:center; gap:0.75rem; margin-bottom:1.25rem; padding-bottom:0.75rem; border-bottom:1px solid var(--ha-slate-200);">
                        <img src="{logo_b}" alt="{name_b} Logo" style="width:36px; height:36px; object-fit:contain;" onerror="this.onerror=null; this.src='{fav_b}';">
                        <div>
                            <h3 style="font-size:1.15rem; font-weight:800; color:var(--ha-slate-900);">{name_b} Customer Feedback</h3>
                            <div style="font-size:0.8rem; color:var(--ha-slate-500);">Rated {cb['rating']} / 5.0 overall</div>
                        </div>
                    </div>
                    {revs_html_b}
                </div>
            </div>

            <!-- Review Feedback Prompt -->
            <div style="background:var(--ha-white); border:1px solid var(--ha-slate-200); border-radius:12px; padding:1.75rem; text-align:center; box-shadow:var(--ha-shadow);">
                <h3 style="font-size:1.15rem; font-weight:800; color:var(--ha-slate-900); margin-bottom:0.35rem;">Have Experience with {name_a} or {name_b}?</h3>
                <p style="font-size:0.925rem; color:var(--ha-slate-600); margin-bottom:1rem;">Help fellow website owners choose the right hosting plan by sharing your experience.</p>
                <div style="display:flex; gap:0.75rem; justify-content:center; flex-wrap:wrap;">
                    <a href="../pages/{slug_a}.html#reviews" class="btn-battle-official" style="padding:0.6rem 1.25rem; font-size:0.875rem;">Leave a Review for {name_a} &rarr;</a>
                    <a href="../pages/{slug_b}.html#reviews" class="btn-battle-official" style="padding:0.6rem 1.25rem; font-size:0.875rem; background:var(--ha-slate-800);">Leave a Review for {name_b} &rarr;</a>
                </div>
            </div>
        </section>

        <!-- Related Matchups -->
        <section>
            <h2 class="ha-h2"><span class="ha-h2-bar"></span>Related Web Hosting Comparisons</h2>
            <div class="ha-related-grid">
                {related_pills}
            </div>
        </section>

    </main>

    <footer style="text-align:center; padding:3rem 1.5rem; border-top:1px solid var(--ha-slate-200); color:var(--ha-slate-500); font-size:0.875rem; background:var(--ha-white); margin-top:4rem;">
        <p>&copy; 2026 CompareAdvice &bull; {name_a} vs {name_b} Comparison &bull; <a href="../pages/index.html" style="color:var(--ha-blue); font-weight:700; text-decoration:none;">View All 55 Hosting Portfolios</a></p>
    </footer>

    <!-- Interactive Scrollspy & Smooth Scroll Script -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        const pills = document.querySelectorAll('.capsule-pill[href^="#"]');
        const tracked = [];
        
        pills.forEach(pill => {{
            const id = pill.getAttribute('href').slice(1);
            const el = document.getElementById(id);
            if (el) {{
                tracked.push({{ id, pill, el }});
            }}
            
            pill.addEventListener('click', function(e) {{
                e.preventDefault();
                pills.forEach(p => p.classList.remove('active'));
                this.classList.add('active');
                
                const target = document.getElementById(id);
                if (target) {{
                    const offset = 110;
                    const y = target.getBoundingClientRect().top + window.pageYOffset - offset;
                    window.scrollTo({{ top: y, behavior: 'smooth' }});
                }}
            }});
        }});

        let ticking = false;
        window.addEventListener('scroll', function() {{
            if (!ticking) {{
                window.requestAnimationFrame(function() {{
                    const scrollPos = window.pageYOffset + 140;
                    let currentId = null;
                    
                    for (let i = 0; i < tracked.length; i++) {{
                        if (tracked[i].el.offsetTop <= scrollPos) {{
                            currentId = tracked[i].id;
                        }}
                    }}
                    
                    if (currentId) {{
                        pills.forEach(p => {{
                            if (p.getAttribute('href') === '#' + currentId) {{
                                p.classList.add('active');
                            }} else {{
                                p.classList.remove('active');
                            }}
                        }});
                    }}
                    ticking = false;
                }});
                ticking = true;
            }}
        }}, {{ passive: true }});
    }});
    </script>

</body>
</html>
"""
    return html

def render_hub_html(companies, all_pairs_count):
    import json
    comp_json_data = {}
    for c in companies:
        slug = c['slug']
        name = c['company_name']
        meta = get_company_portfolio_data(slug, name)
        domain = meta.get('domain', f"{slug.replace('-', '')}.com")
        comp_json_data[slug] = {
            "name": name,
            "logo": meta.get('logo_url', f"https://logo.clearbit.com/{domain}"),
            "fav": meta.get('favicon_url', f"https://www.google.com/s2/favicons?domain={domain}&sz=128"),
            "price": c['profile'].get('starting_price') or '$2.49 / mo',
            "rating": c['profile'].get('overall_rating') or '4.5'
        }
    comp_json_str = json.dumps(comp_json_data)

    sorted_companies = sorted(companies, key=lambda x: x['company_name'])
    options_a = "\n".join([f'<option value="{c["slug"]}">{c["company_name"]}</option>' for c in sorted_companies])
    options_b = "\n".join([f'<option value="{c["slug"]}">{c["company_name"]}</option>' for c in sorted_companies])

    popular_pairs = [
        ("a2-hosting", "fatcow", "A2 Hosting vs FatCow"),
        ("hostinger", "godaddy", "Hostinger vs GoDaddy"),
        ("bluehost", "siteground", "Bluehost vs SiteGround"),
        ("digitalocean", "aws", "DigitalOcean vs AWS"),
        ("fastcomet", "hostinger", "FastComet vs Hostinger"),
        ("namecheap", "bluehost", "Namecheap vs Bluehost"),
        ("dreamhost", "hostinger", "DreamHost vs Hostinger"),
        ("kinsta", "wp-engine", "Kinsta vs WP Engine"),
        ("a2-hosting", "siteground", "A2 Hosting vs SiteGround")
    ]
    popular_cards_html = ""
    for s_a, s_b, label in popular_pairs:
        da = comp_json_data.get(s_a, {})
        db = comp_json_data.get(s_b, {})
        popular_cards_html += f"""
        <a href="{s_a}-vs-{s_b}.html" class="pop-match-card">
            <div class="pop-logos-row">
                <div class="pop-logo-box"><img src="{da.get('logo', '')}" onerror="this.onerror=null; this.src='{da.get('fav', '')}';" alt="{s_a}"></div>
                <span class="pop-vs-pill">VS</span>
                <div class="pop-logo-box"><img src="{db.get('logo', '')}" onerror="this.onerror=null; this.src='{db.get('fav', '')}';" alt="{s_b}"></div>
            </div>
            <div class="pop-match-title">{label}</div>
            <div class="pop-match-cta">Compare Head-to-Head &rarr;</div>
        </a>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Hosting Comparison Engine 2026 - Benchmark 55 Providers Side-by-Side</title>
    <meta name="description" content="Official Web Hosting Comparison Engine. Select any two web hosts from our 55 benchmarked providers to see instant head-to-head server speeds, renewal prices, uptime SLAs, and customer reviews.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --ha-font: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            --ha-blue: #1d4ed8;
            --ha-blue-hover: #1e40af;
            --ha-blue-light: #eff6ff;
            --ha-blue-border: #bfdbfe;
            --ha-green: #15803d;
            --ha-green-light: #dcfce7;
            --ha-slate-900: #0f172a;
            --ha-slate-800: #1e293b;
            --ha-slate-700: #334155;
            --ha-slate-600: #475569;
            --ha-slate-500: #64748b;
            --ha-slate-200: #e2e8f0;
            --ha-slate-100: #f1f5f9;
            --ha-bg: #f8fafc;
            --ha-white: #ffffff;
            --max-w: 1120px;
        }}
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: var(--ha-font);
            background: var(--ha-bg);
            color: var(--ha-slate-900);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            -webkit-font-smoothing: antialiased;
            background-image: radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.07) 0%, transparent 60%);
        }}

        /* Header Topbar */
        .hub-topbar {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--ha-slate-200);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .hub-topbar-inner {{
            max-width: var(--max-w);
            margin: 0 auto;
            padding: 0.9rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .hub-brand {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            text-decoration: none;
            color: var(--ha-slate-900);
            font-weight: 800;
            font-size: 1.25rem;
            letter-spacing: -0.02em;
        }}
        .hub-brand-badge {{
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: white;
            font-size: 0.75rem;
            font-weight: 800;
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            letter-spacing: 0.04em;
        }}
        .hub-nav-links {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .hub-nav-link {{
            color: var(--ha-slate-600);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 600;
            padding: 0.45rem 0.95rem;
            border-radius: 9999px;
            transition: all 0.15s;
        }}
        .hub-nav-link:hover {{
            color: var(--ha-blue);
            background: var(--ha-blue-light);
        }}
        .hub-nav-link.active {{
            background: var(--ha-slate-900);
            color: white;
        }}

        /* Main Container */
        .hub-container {{
            max-width: var(--max-w);
            margin: 0 auto;
            width: 100%;
            padding: 2.5rem 1.5rem 5rem;
        }}

        /* Hero Header */
        .hub-header {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}
        .hub-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: var(--ha-blue-light);
            color: var(--ha-blue);
            border: 1px solid var(--ha-blue-border);
            font-size: 0.775rem;
            font-weight: 800;
            padding: 0.35rem 0.95rem;
            border-radius: 9999px;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .pulse-dot {{
            width: 7px;
            height: 7px;
            background: var(--ha-blue);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.25);
        }}
        .hub-h1 {{
            font-size: clamp(2.3rem, 4.5vw, 3.4rem);
            font-weight: 900;
            letter-spacing: -0.035em;
            color: var(--ha-slate-900);
            margin-bottom: 0.85rem;
            line-height: 1.15;
        }}
        .hub-lead {{
            font-size: 1.125rem;
            color: var(--ha-slate-600);
            max-width: 680px;
            margin: 0 auto 1.75rem;
            line-height: 1.6;
        }}

        /* Stats Ribbon */
        .hub-stats-ribbon {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1.5rem;
            flex-wrap: wrap;
            margin-bottom: 2.5rem;
        }}
        .hub-stat-item {{
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: white;
            border: 1px solid var(--ha-slate-200);
            padding: 0.4rem 0.95rem;
            border-radius: 9999px;
            font-size: 0.825rem;
            font-weight: 700;
            color: var(--ha-slate-700);
            box-shadow: 0 1px 4px rgba(15, 23, 42, 0.03);
        }}
        .stat-val {{
            color: var(--ha-blue);
            font-weight: 800;
        }}

        /* ========================================================
           INTERACTIVE BATTLE ARENA SELECTOR CARD
           ======================================================== */
        .arena-card {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 12px 35px -5px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.03);
            margin-bottom: 4rem;
            position: relative;
        }}
        .arena-top-grid {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            align-items: center;
            gap: 2rem;
            margin-bottom: 2.25rem;
        }}

        /* Provider Side Box */
        .arena-host-side {{
            background: #fafbfc;
            border: 1.5px solid var(--ha-slate-200);
            border-radius: 14px;
            padding: 1.75rem;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            transition: all 0.2s ease;
        }}
        .arena-host-side:hover {{
            border-color: #cbd5e1;
            background: #ffffff;
            box-shadow: 0 6px 20px -3px rgba(15, 23, 42, 0.05);
        }}
        .arena-side-label {{
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--ha-slate-500);
            margin-bottom: 1rem;
        }}
        .arena-logo-wrapper {{
            width: 80px;
            height: 80px;
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 12px;
            margin-bottom: 1rem;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
            transition: transform 0.2s ease;
        }}
        .arena-host-side:hover .arena-logo-wrapper {{
            transform: scale(1.05);
        }}
        .arena-logo-img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .arena-host-name {{
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--ha-slate-900);
            margin-bottom: 0.4rem;
            line-height: 1.2;
        }}
        .arena-meta-row {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 1.25rem;
        }}
        .arena-price-badge {{
            background: var(--ha-blue-light);
            color: var(--ha-blue);
            font-weight: 800;
            font-size: 0.85rem;
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
        }}
        .arena-rating-badge {{
            color: #d97706;
            font-weight: 800;
            font-size: 0.85rem;
        }}
        .arena-select {{
            width: 100%;
            padding: 0.95rem 1.15rem;
            border: 1.5px solid var(--ha-slate-200);
            border-radius: 10px;
            font-size: 1.05rem;
            font-weight: 700;
            font-family: inherit;
            background: #ffffff;
            color: var(--ha-slate-900);
            outline: none;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }}
        .arena-select:focus {{
            border-color: var(--ha-blue);
            box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.15);
        }}

        /* Center VS Pillar */
        .arena-vs-col {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 1rem;
            padding: 0 0.5rem;
        }}
        .vs-badge-glow {{
            width: 58px;
            height: 58px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border: 3px solid #ffffff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 900;
            font-size: 1.15rem;
            color: white;
            box-shadow: 0 6px 20px rgba(15, 23, 42, 0.25);
            letter-spacing: 0.05em;
        }}
        .btn-swap-hosts {{
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            border-radius: 9999px;
            padding: 0.45rem 0.95rem;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--ha-slate-600);
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            cursor: pointer;
            transition: all 0.15s ease;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }}
        .btn-swap-hosts:hover {{
            background: #f8fafc;
            color: var(--ha-blue);
            border-color: #cbd5e1;
            transform: scale(1.05);
        }}

        /* Big Launch CTA Button */
        .btn-compare-launch {{
            display: block;
            width: 100%;
            background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
            color: white;
            border: none;
            padding: 1.25rem 2rem;
            border-radius: 12px;
            font-size: 1.25rem;
            font-weight: 800;
            font-family: inherit;
            cursor: pointer;
            box-shadow: 0 8px 25px -4px rgba(29, 78, 216, 0.4);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            text-align: center;
            letter-spacing: -0.01em;
        }}
        .btn-compare-launch:hover {{
            background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%);
            transform: translateY(-2px);
            box-shadow: 0 12px 30px -4px rgba(29, 78, 216, 0.5);
        }}

        /* ========================================================
           POPULAR SHOWDOWN MATCHUPS GRID (Dual Logo Cards)
           ======================================================== */
        .popular-sec-title {{
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--ha-slate-900);
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
            text-align: center;
        }}
        .popular-sec-sub {{
            font-size: 0.95rem;
            color: var(--ha-slate-500);
            text-align: center;
            margin-bottom: 1.75rem;
        }}
        .popular-match-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 1.25rem;
            margin-bottom: 3.5rem;
        }}
        .pop-match-card {{
            background: var(--ha-white);
            border: 1px solid var(--ha-slate-200);
            border-radius: 14px;
            padding: 1.25rem 1.4rem;
            text-decoration: none;
            color: var(--ha-slate-900);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        }}
        .pop-match-card:hover {{
            border-color: var(--ha-blue);
            transform: translateY(-3px);
            box-shadow: 0 10px 25px -4px rgba(29, 78, 216, 0.12);
        }}
        .pop-logos-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.85rem;
            margin-bottom: 0.85rem;
        }}
        .pop-logo-box {{
            width: 44px;
            height: 44px;
            background: #ffffff;
            border: 1px solid var(--ha-slate-200);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 6px;
        }}
        .pop-logo-box img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .pop-vs-pill {{
            background: var(--ha-slate-100);
            color: var(--ha-slate-500);
            font-size: 0.725rem;
            font-weight: 800;
            padding: 0.2rem 0.5rem;
            border-radius: 9999px;
            border: 1px solid var(--ha-slate-200);
        }}
        .pop-match-title {{
            font-size: 1.05rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.35rem;
            color: var(--ha-slate-900);
        }}
        .pop-match-cta {{
            font-size: 0.825rem;
            font-weight: 700;
            color: var(--ha-blue);
            text-align: center;
        }}

        /* Footer */
        .hub-footer {{
            text-align: center;
            padding: 2.5rem 1.5rem;
            border-top: 1px solid var(--ha-slate-200);
            background: var(--ha-white);
            color: var(--ha-slate-500);
            font-size: 0.875rem;
            margin-top: 3rem;
        }}
        .hub-footer a {{
            color: var(--ha-blue);
            font-weight: 700;
            text-decoration: none;
        }}

        /* Responsive Breakpoints */
        @media (max-width: 768px) {{
            .arena-top-grid {{
                grid-template-columns: 1fr;
                gap: 1.5rem;
            }}
            .arena-vs-col {{
                flex-direction: row;
                justify-content: center;
            }}
            .arena-card {{
                padding: 1.5rem 1.25rem;
            }}
            .hub-nav-links {{ display: none; }}
            .popular-match-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

    <!-- Site Header Topbar -->
    <header class="hub-topbar">
        <div class="hub-topbar-inner">
            <a href="compare_hub.html" class="hub-brand">
                <span class="hub-brand-badge">HOSTING</span>
                <span>CompareAdvice</span>
            </a>
            <nav class="hub-nav-links">
                <a href="compare_hub.html" class="hub-nav-link active">Comparison Engine</a>
                <a href="../pages/index.html" class="hub-nav-link">All 55 Hosting Portfolios</a>
                <a href="a2-hosting-vs-fatcow.html" class="hub-nav-link">Featured Benchmark</a>
            </nav>
        </div>
    </header>

    <!-- Main Container -->
    <main class="hub-container">

        <!-- Hero Header -->
        <header class="hub-header">
            <div class="hub-tag">
                <span class="pulse-dot"></span>
                <span>2026 BENCHMARK ENGINE &bull; 1,485 COMPARISONS</span>
            </div>
            <h1 class="hub-h1">Web Hosting Comparison Engine</h1>
            <p class="hub-lead">Select any two hosting providers to benchmark real server speed, plan pricing, renewal costs, uptime SLAs, and verified user ratings side-by-side.</p>

            <!-- Stats Ribbon -->
            <div class="hub-stats-ribbon">
                <div class="hub-stat-item"><span class="stat-val">55</span> Web Hosts Analyzed</div>
                <div class="hub-stat-item"><span class="stat-val">1,485</span> Benchmark Combinations</div>
                <div class="hub-stat-item"><span class="stat-val">24/7</span> Speed &amp; TTFB Monitored</div>
                <div class="hub-stat-item"><span class="stat-val">100%</span> Independent &amp; Unbiased</div>
            </div>
        </header>

        <!-- ========================================================
             INTERACTIVE BATTLE ARENA SELECTOR CARD
             ======================================================== -->
        <section class="arena-card">
            <div class="arena-top-grid">

                <!-- Host A Selector Card -->
                <div class="arena-host-side">
                    <div class="arena-side-label">Select First Provider</div>
                    <div class="arena-logo-wrapper">
                        <img id="logoA" src="" alt="Provider A Logo" class="arena-logo-img">
                    </div>
                    <div id="nameA" class="arena-host-name">Host A</div>
                    <div class="arena-meta-row">
                        <span id="priceA" class="arena-price-badge">$0.00 / mo</span>
                        <span id="ratingA" class="arena-rating-badge">★ 0.0 / 5.0</span>
                    </div>
                    <select id="hostA" class="arena-select" onchange="updateHostPreview('A')">
                        {options_a}
                    </select>
                </div>

                <!-- Center VS Pillar & Swap -->
                <div class="arena-vs-col">
                    <div class="vs-badge-glow">VS</div>
                    <button type="button" class="btn-swap-hosts" onclick="swapHosts()" title="Swap selected hosting providers">
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M7 16V4m0 0L3 8m4-4l4 4m6 4v12m0 0l4-4m-4 4l-4-4"/></svg>
                        <span>Swap</span>
                    </button>
                </div>

                <!-- Host B Selector Card -->
                <div class="arena-host-side">
                    <div class="arena-side-label">Select Second Provider</div>
                    <div class="arena-logo-wrapper">
                        <img id="logoB" src="" alt="Provider B Logo" class="arena-logo-img">
                    </div>
                    <div id="nameB" class="arena-host-name">Host B</div>
                    <div class="arena-meta-row">
                        <span id="priceB" class="arena-price-badge">$0.00 / mo</span>
                        <span id="ratingB" class="arena-rating-badge">★ 0.0 / 5.0</span>
                    </div>
                    <select id="hostB" class="arena-select" onchange="updateHostPreview('B')">
                        {options_b}
                    </select>
                </div>
            </div>

            <!-- Big Launch CTA Button -->
            <button id="btnLaunch" class="btn-compare-launch" onclick="launchCompare()">
                <span id="btnLaunchText">Compare Head-to-Head Benchmark</span> &rarr;
            </button>
        </section>

        <!-- Popular Matchups Section -->
        <section>
            <h2 class="popular-sec-title">Popular Head-to-Head Comparisons</h2>
            <p class="popular-sec-sub">Frequently benchmarked matchups chosen by digital webmasters and agency developers:</p>
            <div class="popular-match-grid">
                {popular_cards_html}
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="hub-footer">
        <p>&copy; 2026 CompareAdvice &bull; Benchmarking {len(companies)} Hosting Providers across {all_pairs_count} Comparisons &bull; <a href="../pages/index.html">View All 55 Hosting Portfolios</a></p>
    </footer>

    <!-- Interactive Client Script -->
    <script>
        const companiesData = {comp_json_str};

        function updateHostPreview(side) {{
            const select = document.getElementById('host' + side);
            if (!select) return;
            const val = select.value;
            const data = companiesData[val];
            if (!data) return;

            const logoEl = document.getElementById('logo' + side);
            logoEl.src = data.logo;
            logoEl.onerror = function() {{
                this.onerror = null;
                this.src = data.fav;
            }};
            document.getElementById('name' + side).textContent = data.name;
            document.getElementById('price' + side).textContent = data.price;
            document.getElementById('rating' + side).textContent = '★ ' + data.rating + ' / 5.0';
            updateButtonText();
        }}

        function swapHosts() {{
            const selA = document.getElementById('hostA');
            const selB = document.getElementById('hostB');
            const temp = selA.value;
            selA.value = selB.value;
            selB.value = temp;
            updateHostPreview('A');
            updateHostPreview('B');
        }}

        function updateButtonText() {{
            const valA = document.getElementById('hostA').value;
            const valB = document.getElementById('hostB').value;
            const nameA = companiesData[valA] ? companiesData[valA].name : 'Host A';
            const nameB = companiesData[valB] ? companiesData[valB].name : 'Host B';
            document.getElementById('btnLaunchText').textContent = 'Compare ' + nameA + ' vs ' + nameB + ' Benchmark';
        }}

        function launchCompare() {{
            const a = document.getElementById('hostA').value;
            const b = document.getElementById('hostB').value;
            if (a === b) {{
                alert('Please select two different hosting providers to compare.');
                return;
            }}
            window.location.href = a + '-vs-' + b + '.html';
        }}

        // Initialize defaults
        document.addEventListener('DOMContentLoaded', function() {{
            const selA = document.getElementById('hostA');
            const selB = document.getElementById('hostB');
            if (selA && selA.options.length > 0) selA.selectedIndex = 0;
            if (selB && selB.options.length > 1) selB.selectedIndex = 1;
            updateHostPreview('A');
            updateHostPreview('B');
        }});
    </script>
</body>
</html>
"""
    return html

def generate_all_matrix(output_dir, bidirectional=False, single_pair=None):
    companies_dir = os.path.join(output_dir, "companies")
    matrix_dir = os.path.join(output_dir, "matrix_comparisons")
    os.makedirs(matrix_dir, exist_ok=True)

    company_files = [f for f in os.listdir(companies_dir) if f.endswith('.json')]
    companies = []
    comp_map = {}
    for f in company_files:
        with open(os.path.join(companies_dir, f), 'r', encoding='utf-8') as fp:
            c = json.load(fp)
            companies.append(c)
            comp_map[c['slug']] = c

    n = len(companies)
    print(f"[*] Loaded {n} companies from {companies_dir}.")

    if single_pair:
        slug_a, slug_b = single_pair
        if slug_a not in comp_map or slug_b not in comp_map:
            print(f"[!] Error: One or both slugs not found: {slug_a}, {slug_b}")
            return 0
        pairs = [(comp_map[slug_a], comp_map[slug_b])]
    elif bidirectional:
        pairs = [(a, b) for a in companies for b in companies if a['slug'] != b['slug']]
    else:
        pairs = list(itertools.combinations(companies, 2))

    total_pairs = len(pairs)
    print(f"[*] Generating {total_pairs} enhanced comparison pages with logos and reviews into: {matrix_dir}...")

    sitemap_urls = []

    for idx, (comp_a, comp_b) in enumerate(pairs, 1):
        comp_data = compare_two_companies(comp_a, comp_b)
        html = render_comparison_html(comp_data)
        out_filename = f"{comp_data['slug']}.html"
        out_path = os.path.join(matrix_dir, out_filename)
        
        with open(out_path, 'w', encoding='utf-8') as fp:
            fp.write(html)

        sitemap_urls.append(out_filename)

        if idx % 500 == 0 or idx == total_pairs:
            print(f"  Processed ({idx}/{total_pairs}) comparisons...")

    # Hub
    hub_html = render_hub_html(companies, total_pairs if not single_pair else n * (n - 1))
    hub_path = os.path.join(matrix_dir, "compare_hub.html")
    with open(hub_path, 'w', encoding='utf-8') as fp:
        fp.write(hub_html)

    print(f"[OK] Successfully generated {total_pairs} comparison pages with logos and customer reviews!")
    return total_pairs

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Generate Cross-Company Comparison Matrix")
    parser.add_argument("--bidirectional", action="store_true", help="Generate full N*(N-1) matrix")
    parser.add_argument("--single", nargs=2, metavar=('SLUG_A', 'SLUG_B'), help="Generate a single comparison page (e.g. a2-hosting fatcow)")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")

    args = parser.parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = args.output_dir or os.path.join(base_dir, "output")
    generate_all_matrix(out_dir, bidirectional=args.bidirectional, single_pair=args.single)
