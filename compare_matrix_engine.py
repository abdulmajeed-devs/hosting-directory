"""
HostAdvice Matrix Comparison Engine - Enterprise Grade
Computes head-to-head metrics, category score breakdowns (out of 10),
side-by-side Pros & Cons, feature matrix, and dynamic FAQs.
"""

import os
import re
import json

BRAND_META = {
    "hostinger": {
        "color": "#673ab7",
        "badge_color": "#7c3aed",
        "pros": ["Ultra-affordable pricing with free domain included", "LiteSpeed servers with built-in LSCache", "Intuitive custom hPanel control panel", "8 global data centers (US, EU, Asia, Brazil)"],
        "cons": ["No dedicated telephone support", "Higher renewal pricing on 1-month terms"]
    },
    "bluehost": {
        "color": "#1967d2",
        "badge_color": "#2563eb",
        "pros": ["Official WordPress.org recommended host", "Free domain & SSL certificate for 1st year", "24/7 toll-free phone support included", "Beginner-friendly WordPress onboarding portal"],
        "cons": ["Aggressive checkout upsell offers", "Renewal pricing increases significantly"]
    },
    "siteground": {
        "color": "#1e824c",
        "badge_color": "#059669",
        "pros": ["Industry-leading 99.99% Google Cloud uptime", "Ultra-fast SuperCacher and PHP optimization", "Top-rated 24/7 instant live chat support (<1 min wait)", "Free automated daily backups & staging tool"],
        "cons": ["Strict storage space limits on entry plans", "Premium renewal prices"]
    },
    "godaddy": {
        "color": "#008289",
        "badge_color": "#0d9488",
        "pros": ["Complete domain, email & hosting ecosystem", "24/7 worldwide direct phone support in local languages", "Fast NVMe storage on all newer tiers", "Well-established industry reliability"],
        "cons": ["SSL not free indefinitely on basic plans", "Renewal rates can be steep"]
    },
    "digitalocean": {
        "color": "#0080ff",
        "badge_color": "#0284c7",
        "pros": ["Full root access and complete developer control", "Fast NVMe SSD cloud droplets from $4.00/mo", "Predictable hourly/monthly billing", "15 global enterprise data centers"],
        "cons": ["Unmanaged infrastructure (sysadmin required)", "No standard phone support"]
    },
    "aws": {
        "color": "#ff9900",
        "badge_color": "#d97706",
        "pros": ["World's most scalable cloud infrastructure", "Lightsail VPS starting at only $3.50/mo", "Massive global CloudFront CDN edge network", "Pay-as-you-go elastic resources"],
        "cons": ["Steep learning curve for non-developers", "Technical ticket support requires paid plan"]
    },
    "a2-hosting": {
        "color": "#f05a28",
        "badge_color": "#ea580c",
        "pros": ["Turbo servers up to 20x faster with LiteSpeed", "Anytime money-back guarantee (pro-rated)", "24/7 Guru Crew phone & chat support", "Generous 100 GB SSD storage on starter plan"],
        "cons": ["Turbo LiteSpeed features reserved for higher tiers", "Renewal pricing increases"]
    },
    "fastcomet": {
        "color": "#206095",
        "badge_color": "#1d4ed8",
        "pros": ["100% pure NVMe cloud SSD storage", "45-day money-back guarantee", "11 global server data center locations", "Free automated daily backups on all tiers"],
        "cons": ["Resource caps on entry FastCloud tier"]
    },
    "dreamhost": {
        "color": "#0073ec",
        "badge_color": "#2563eb",
        "pros": ["Unmatched 97-day money-back guarantee", "100% uptime guarantee with compensation", "WordPress.org recommended hosting provider", "Generous 50 GB SSD storage on starter plan"],
        "cons": ["Professional email is a paid add-on", "Callback phone support only"]
    },
    "kinsta": {
        "color": "#5333ed",
        "badge_color": "#6366f1",
        "pros": ["Enterprise Google Cloud C2/C3D VMs", "Cloudflare Enterprise CDN included for free", "24/7 support by senior WordPress engineers", "Custom MyKinsta developer dashboard"],
        "cons": ["Premium pricing ($30+/mo)", "WordPress hosting only"]
    },
    "wp-engine": {
        "color": "#0ecad4",
        "badge_color": "#0891b2",
        "pros": ["Industry-standard managed WordPress hosting", "EverCache proprietary caching technology", "24/7 phone & chat support on all plans", "60-day money-back guarantee"],
        "cons": ["Higher monthly investment", "Strict plugin disallow list"]
    },
    "cloudways": {
        "color": "#2c3e50",
        "badge_color": "#334155",
        "pros": ["Deploy on DigitalOcean, AWS, or Google Cloud", "ThunderStack caching with Redis and Varnish", "Pay-as-you-go billing with no contracts", "Unlimited sites per cloud server"],
        "cons": ["No cPanel (custom cloud console)", "Email hosting requires add-on"]
    }
}

DEFAULT_PROS_CONS = {
    "pros": [
        "Competitive entry pricing with starter promo",
        "24/7 customer support via ticketing & chat",
        "Free SSL security certificate included",
        "Standard 30-day money-back guarantee"
    ],
    "cons": [
        "Standard renewal prices apply after initial term",
        "Advanced caching features on higher tiers"
    ]
}

def parse_price_val(price_str):
    if not price_str:
        return 999.0
    m = re.search(r'\$\s*(\d+(?:\.\d+)?)', str(price_str))
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return 999.0

def parse_rating_val(rating_str):
    if not rating_str:
        return 4.3
    m = re.search(r'(\d+(?:\.\d+)?)', str(rating_str))
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return 4.3

def get_brand_meta(slug, name):
    if slug in BRAND_META:
        return BRAND_META[slug]
    return {
        "color": "#2563eb",
        "badge_color": "#1d4ed8",
        "pros": [
            f"Reliable starter tier for {name}",
            "24/7 customer support channels available",
            "Free SSL security certificate included",
            "Industry-standard 30-day money-back guarantee"
        ],
        "cons": [
            "Renewal prices increase after promotional term",
            "Advanced server add-ons require upgraded plans"
        ]
    }

def compare_two_companies(comp_a, comp_b):
    name_a = comp_a['company_name']
    name_b = comp_b['company_name']
    slug_a = comp_a['slug']
    slug_b = comp_b['slug']

    prof_a = comp_a.get('profile', {})
    prof_b = comp_b.get('profile', {})

    rating_a = parse_rating_val(prof_a.get('overall_rating'))
    rating_b = parse_rating_val(prof_b.get('overall_rating'))

    price_str_a = prof_a.get('starting_price') or "Check website"
    price_str_b = prof_b.get('starting_price') or "Check website"
    price_num_a = parse_price_val(price_str_a)
    price_num_b = parse_price_val(price_str_b)

    meta_a = get_brand_meta(slug_a, name_a)
    meta_b = get_brand_meta(slug_b, name_b)

    # 1. SECTION 1: PLAN COMPARISON
    plan_a = comp_a.get('plan_comparison', {})
    plan_b = comp_b.get('plan_comparison', {})
    all_plan_keys = [
        "Starter Plan Name",
        "Promotional Price",
        "Standard Renewal Price",
        "Websites Allowed",
        "Storage Space",
        "Bandwidth / Traffic",
        "Free Domain",
        "Free SSL Certificate",
        "Money-Back Guarantee",
        "Email Accounts"
    ]
    plan_rows = []
    for k in all_plan_keys:
        plan_rows.append({
            "attribute": k,
            "raw_key": k,
            name_a: plan_a.get(k, "Included"),
            name_b: plan_b.get(k, "Included")
        })

    # Plan winner
    if price_num_a < price_num_b and price_num_a < 900:
        plan_winner = name_a
        plan_verdict = f"{name_a} offers significantly better entry pricing starting at {price_str_a} vs {price_str_b} for {name_b}."
    elif price_num_b < price_num_a and price_num_b < 900:
        plan_winner = name_b
        plan_verdict = f"{name_b} offers a more economical starter package at {price_str_b} vs {price_str_a} for {name_a}."
    else:
        plan_winner = "Tie"
        plan_verdict = f"Both providers feature closely matched starting pricing plans ({price_str_a} vs {price_str_b})."

    # 2. SECTION 2: PERFORMANCE & INFRASTRUCTURE COMPARISON
    perf_a = comp_a.get('performance_comparison', {})
    perf_b = comp_b.get('performance_comparison', {})
    all_perf_keys = [
        "Uptime Guarantee / SLA",
        "Web Server Software",
        "Caching Technology",
        "Global Server Locations",
        "CDN Integration",
        "Storage Technology",
        "Automated Backups",
        "PHP & Protocol"
    ]
    perf_rows = []
    for k in all_perf_keys:
        perf_rows.append({
            "attribute": k,
            "raw_key": k,
            name_a: perf_a.get(k, "Standard Tier-3 Server"),
            name_b: perf_b.get(k, "Standard Tier-3 Server")
        })

    is_a_litespeed = 'litespeed' in str(perf_a.get('Web Server Software', '')).lower() or 'nvme' in str(perf_a.get('Storage Technology', '')).lower()
    is_b_litespeed = 'litespeed' in str(perf_b.get('Web Server Software', '')).lower() or 'nvme' in str(perf_b.get('Storage Technology', '')).lower()
    if is_a_litespeed and not is_b_litespeed:
        perf_winner = name_a
        perf_verdict = f"{name_a} holds the server speed advantage powered by high-concurrency architecture and NVMe storage."
    elif is_b_litespeed and not is_a_litespeed:
        perf_winner = name_b
        perf_verdict = f"{name_b} delivers superior server throughput with optimized web server caching and fast NVMe hardware."
    else:
        perf_winner = name_a if rating_a >= rating_b else name_b
        perf_verdict = f"{perf_winner} maintains enterprise-grade reliability and redundant global server infrastructure."

    # 3. SECTION 3: CUSTOMER SUPPORT & SERVICE COMPARISON
    supp_a = comp_a.get('support_comparison', {})
    supp_b = comp_b.get('support_comparison', {})
    all_supp_keys = [
        "24/7 Live Chat",
        "Phone Support",
        "Ticket / Email Support",
        "Free Website Migration",
        "Knowledge Base",
        "HostAdvice Support Rating",
        "Ease of Use Score"
    ]
    supp_rows = []
    for k in all_supp_keys:
        supp_rows.append({
            "attribute": k,
            "raw_key": k,
            name_a: supp_a.get(k, "Available 24/7"),
            name_b: supp_b.get(k, "Available 24/7")
        })

    supp_score_a = parse_rating_val(supp_a.get('HostAdvice Support Rating'))
    supp_score_b = parse_rating_val(supp_b.get('HostAdvice Support Rating'))
    if supp_score_a > supp_score_b:
        supp_winner = name_a
        supp_verdict = f"{name_a} rates higher for customer satisfaction ({supp_score_a}/5 vs {supp_score_b}/5)."
    elif supp_score_b > supp_score_a:
        supp_winner = name_b
        supp_verdict = f"{name_b} achieves superior user feedback for fast resolution times ({supp_score_b}/5 vs {supp_score_a}/5)."
    else:
        supp_winner = "Tie"
        supp_verdict = f"Both {name_a} and {name_b} deliver dependable 24/7 support coverage."

    # Compute Normalized 10-point Category Breakdown Scores for Progress Bars
    # Value for Money Score (1.0 - 10.0)
    score_val_a = min(9.8, max(6.5, round(10.0 - (price_num_a / 12.0) * 3.0, 1))) if price_num_a < 900 else 7.5
    score_val_b = min(9.8, max(6.5, round(10.0 - (price_num_b / 12.0) * 3.0, 1))) if price_num_b < 900 else 7.5

    # Speed & Performance Score
    score_perf_a = 9.6 if is_a_litespeed else (9.1 if rating_a >= 4.5 else 8.5)
    score_perf_b = 9.6 if is_b_litespeed else (9.1 if rating_b >= 4.5 else 8.5)

    # Support Score
    score_supp_a = round(supp_score_a * 2.0, 1)
    score_supp_b = round(supp_score_b * 2.0, 1)

    # Ease of Use Score
    score_ease_a = 9.5 if 'cPanel' in str(supp_a.get('Ease of Use Score')) or 'hPanel' in str(supp_a.get('Ease of Use Score')) else 8.8
    score_ease_b = 9.5 if 'cPanel' in str(supp_b.get('Ease of Use Score')) or 'hPanel' in str(supp_b.get('Ease of Use Score')) else 8.8

    # Overall Combined Score
    overall_score_a = round((score_val_a + score_perf_a + score_supp_a + score_ease_a) / 4.0, 1)
    overall_score_b = round((score_val_b + score_perf_b + score_supp_b + score_ease_b) / 4.0, 1)

    if overall_score_a > overall_score_b:
        overall_winner = name_a
        verdict = f"{name_a} wins this head-to-head showdown with an overall benchmark score of {overall_score_a}/10 (vs {overall_score_b}/10 for {name_b}). {name_a} excels with stronger value across its entry tiers, solid server responsiveness, and high verified customer satisfaction."
    elif overall_score_b > overall_score_a:
        overall_winner = name_b
        verdict = f"{name_b} wins this matchup with an overall benchmark score of {overall_score_b}/10 (vs {overall_score_a}/10 for {name_a}). {name_b} delivers competitive plan inclusions, robust server hardware, and superior user support ratings."
    else:
        overall_winner = "Tie / Depends on Use Case"
        verdict = f"Both {name_a} and {name_b} are exceptional hosting platforms tied at {overall_score_a}/10. Choose {name_a} for budget entry workflows, or {name_b} if your stack requires their specific server features."

    # Dynamic FAQs
    faqs = [
        {
            "question": f"Which is cheaper: {name_a} or {name_b}?",
            "answer": f"{name_a} entry tier starts at {price_str_a}, while {name_b} starts at {price_str_b}. {plan_verdict}"
        },
        {
            "question": f"Does {name_a} or {name_b} offer faster server speed and uptime?",
            "answer": f"{name_a} delivers {perf_a.get('Uptime Guarantee / SLA', '99.9% uptime')} on {perf_a.get('Web Server Software', 'optimized servers')}. Meanwhile, {name_b} offers {perf_b.get('Uptime Guarantee / SLA', '99.9% uptime')} on {perf_b.get('Web Server Software', 'optimized servers')}."
        },
        {
            "question": f"How does customer support compare between {name_a} and {name_b}?",
            "answer": f"{name_a} has an official support rating of {supp_score_a or rating_a}/5.0 with {supp_a.get('24/7 Live Chat', 'Live Chat')}. {name_b} has an official support rating of {supp_score_b or rating_b}/5.0 with {supp_b.get('24/7 Live Chat', 'Live Chat')}."
        },
        {
            "question": f"Can I get free website migration between {name_a} and {name_b}?",
            "answer": f"{name_a} provides {supp_a.get('Free Website Migration', 'migration assistance')}, while {name_b} offers {supp_b.get('Free Website Migration', 'migration assistance')}."
        }
    ]

    return {
        "comparison_title": f"{name_a} vs {name_b}",
        "slug": f"{slug_a}-vs-{slug_b}",
        "company_a": {
            "name": name_a,
            "slug": slug_a,
            "rating": rating_a,
            "price": price_str_a,
            "overall_score": overall_score_a,
            "color": meta_a["color"],
            "badge_color": meta_a["badge_color"],
            "pros": meta_a["pros"],
            "cons": meta_a["cons"],
            "scores": {
                "val": score_val_a,
                "perf": score_perf_a,
                "supp": score_supp_a,
                "ease": score_ease_a
            },
            "is_winner": (overall_winner == name_a)
        },
        "company_b": {
            "name": name_b,
            "slug": slug_b,
            "rating": rating_b,
            "price": price_str_b,
            "overall_score": overall_score_b,
            "color": meta_b["color"],
            "badge_color": meta_b["badge_color"],
            "pros": meta_b["pros"],
            "cons": meta_b["cons"],
            "scores": {
                "val": score_val_b,
                "perf": score_perf_b,
                "supp": score_supp_b,
                "ease": score_ease_b
            },
            "is_winner": (overall_winner == name_b)
        },
        "overall_winner": overall_winner,
        "verdict": verdict,
        "plan_comparison": {
            "winner": plan_winner,
            "verdict": plan_verdict,
            "rows": plan_rows
        },
        "performance_comparison": {
            "winner": perf_winner,
            "verdict": perf_verdict,
            "rows": perf_rows
        },
        "support_comparison": {
            "winner": supp_winner,
            "verdict": supp_verdict,
            "rows": supp_rows
        },
        "faqs": faqs
    }
