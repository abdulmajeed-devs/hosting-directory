"""
HostAdvice Comparison Page Parser
Handles both modern editorial comparison layouts and legacy spec-grid comparison layouts,
supporting 2-way and 3-way hosting comparisons.
"""

import re
from bs4 import BeautifulSoup


def clean_text(text):
    if not text:
        return ""
    # normalize spaces and non-breaking spaces
    text = text.replace('\xa0', ' ').replace('\u200b', '')
    return re.sub(r'\s+', ' ', text).strip()


def extract_static_elements(soup, html):
    """Detects and audits presence of standard static template components."""
    return {
        'has_header': bool(soup.find('header') or soup.find(class_=lambda c: c and 'header' in c)),
        'has_footer': bool(soup.find('footer') or soup.find(class_=lambda c: c and 'footer' in c)),
        'has_breadcrumbs': bool(soup.find(class_=lambda c: c and 'breadcrumb' in c)),
        'has_sticky_bar': bool(soup.find(class_=lambda c: c and 'sticky' in c)),
        'has_compare_table': bool(soup.find(class_=lambda c: c and 'compare-table' in c)),
        'has_comparison_boxes': bool(soup.find(class_=lambda c: c and 'comparison-boxes' in c)),
        'has_sidebar': bool(soup.find(class_=lambda c: c and ('brands-sidebar' in c or 'sidebar-wrap' in c))),
        'has_faq_section': bool(soup.find(class_=lambda c: c and 'faq' in c)),
        'has_popular_comparisons': bool(soup.find(class_=lambda c: c and 'most-popular-comparisons' in c)),
        'has_hosting_owner_cta': bool("Are You a Hosting Owner?" in html),
        'has_selling_buying_cta': bool("Selling or Buying a Hosting Business?" in html),
        'has_footer_ma_cta': bool(soup.find(class_=lambda c: c and 'footer-ma-cta' in c)),
    }


def parse_comparison_page(html, url=""):
    """
    Parses a single HostAdvice comparison page.
    Returns structured dictionary with companies, ratings, winner, specs, FAQs, and static elements.
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Page Title & Clean Title
    h1 = soup.find('h1')
    page_title = clean_text(h1.get_text() if h1 else (soup.title.get_text() if soup.title else ''))
    
    m = re.match(r'^(.*?)\s*(\(\d{4}\s*Comparison\)|\d{4}:)', page_title, re.IGNORECASE)
    comparison_name = clean_text(m.group(1)) if m else clean_text(page_title.split(':')[0])
    
    # 2. Template Detection
    has_editorial_table = bool(soup.find(class_='compare-table'))
    has_faq = bool(soup.find(class_='faq-section'))
    template_type = 'editorial' if (has_editorial_table or has_faq) else 'spec_grid'
    
    companies = []
    company_details = {}
    winner = None
    comparison_specs = {}
    faqs = []
    summary_text = ""
    
    # 3. Static Elements Audit
    static_elements = extract_static_elements(soup, html)
    
    # =========================================================================
    # A. EDITORIAL LAYOUT PARSING
    # =========================================================================
    if template_type == 'editorial':
        # Hero summary & brand cards
        hero_section = soup.find(class_=re.compile(r'comparison-boxes|hero|header-comparison', re.I))
        cards = hero_section.find_all(class_='shadow-card') if hero_section else soup.find_all(class_='shadow-card')
        
        for c in cards:
            logo_a = c.find('a', class_=re.compile(r'logo|brand', re.I)) or c.find('a')
            brand_name = None
            if logo_a:
                brand_name = logo_a.get('title')
                if not brand_name and logo_a.find('img'):
                    brand_name = logo_a.find('img').get('alt')
            
            # Clean brand name
            if brand_name:
                brand_name = re.sub(r'\s*Logo$', '', brand_name, flags=re.I).strip()
            
            if not brand_name:
                continue
                
            score_tag = c.find(class_=re.compile(r'score|rating', re.I))
            score = clean_text(score_tag.get_text()) if score_tag else None
            
            is_win = bool(c.find(class_=re.compile(r'winner|best-overall', re.I)) or 'BEST OVERALL' in c.get_text())
            
            deal_tag = c.find(class_=re.compile(r'deal|promo|coupon', re.I))
            deal_text = clean_text(deal_tag.get_text()) if deal_tag else None
            
            features = [clean_text(li.get_text()) for li in c.find_all('li') if clean_text(li.get_text())]
            
            if brand_name not in company_details:
                companies.append(brand_name)
                company_details[brand_name] = {
                    'name': brand_name,
                    'rating': score,
                    'is_winner': is_win,
                    'deal_promo': deal_text,
                    'features': features
                }
                if is_win and not winner:
                    winner = brand_name
        
        # If companies not found from cards, extract from URL slug
        if not companies and url:
            slug = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
            parts = slug.split('-vs-')
            companies = [p.replace('-', ' ').title() for p in parts]
            for comp in companies:
                company_details[comp] = {'name': comp, 'rating': None, 'is_winner': False, 'features': []}

        # Compare Table & Column mapping
        comp_table = soup.find(class_='compare-table')
        if comp_table:
            # Header column mapping
            table_hdr = comp_table.find('header')
            table_brands = []
            if table_hdr:
                for h_div in table_hdr.find_all('div', class_=re.compile(r'hosting_\d+')):
                    b_logo = h_div.find('a', class_='logo') or h_div.find('a')
                    b_title = b_logo.get('title') if b_logo else None
                    if not b_title and b_logo:
                        b_title = b_logo.get('data-slug', '').replace('-', ' ').title()
                    if b_title:
                        b_title = re.sub(r'\s*Logo$', '', b_title, flags=re.I).strip()
                        table_brands.append(b_title)
                        if 'winner' in h_div.get('class', []) and not winner:
                            winner = b_title
                            if b_title in company_details:
                                company_details[b_title]['is_winner'] = True

            if not table_brands:
                table_brands = companies

            # Parse Table Rows
            for r in comp_table.find_all(class_='compare-row'):
                name_div = r.find(class_='row-name')
                vals_div = r.find(class_='values')
                if name_div and vals_div:
                    feat_title = clean_text(name_div.get_text())
                    val_items = vals_div.find_all(['div', 'span'], recursive=False)
                    row_vals = {}
                    for idx, v in enumerate(val_items):
                        b_name = table_brands[idx] if idx < len(table_brands) else f"Company_{idx+1}"
                        val_txt = clean_text(v.get_text())
                        is_val_win = 'winner' in v.get('class', [])
                        row_vals[b_name] = {
                            'value': val_txt,
                            'is_winner': is_val_win
                        }
                    comparison_specs[feat_title] = row_vals

        # FAQs extraction
        faq_sec = soup.find(class_='faq-section')
        if faq_sec:
            for d in faq_sec.find_all('details'):
                sum_tag = d.find('summary')
                q = clean_text(sum_tag.get_text()) if sum_tag else ''
                # Clone or strip question to get answer text cleanly
                ans_text = clean_text(" ".join(p.get_text() for p in d.find_all(['p', 'div'])))
                if not ans_text:
                    full_txt = clean_text(d.get_text())
                    ans_text = clean_text(full_txt.replace(q, ''))
                if q:
                    faqs.append({'question': q, 'answer': ans_text})

        # Verdict / Bottom line summary
        verdict_h = soup.find(lambda t: t.name in ['h2', 'h3'] and ('the bottom line' in t.get_text().lower() or 'summary' in t.get_text().lower() or 'verdict' in t.get_text().lower()))
        if verdict_h:
            p = verdict_h.find_next_sibling('p')
            if p:
                summary_text = clean_text(p.get_text())

    # =========================================================================
    # B. SPEC GRID LAYOUT PARSING (Supports 2-way and 3-way comparisons)
    # =========================================================================
    else:
        # Header roles: 'winner', 'second', 'third'
        header_containers = soup.find_all('div', class_=lambda c: c and 'hosting' in c and ('second' in c or 'winner' in c or 'first' in c or 'third' in c))
        role_brand_map = {} # role -> BrandName
        
        for h in header_containers:
            logo = h.find('a', class_='logo')
            if logo:
                title = logo.get('title') or logo.get('data-slug', '').replace('-', ' ').title()
                title = re.sub(r'\s*Logo$', '', title, flags=re.I).strip()
                
                # Determine role
                role = 'second'
                for r in ['winner', 'third', 'second', 'first']:
                    if r in h.get('class', []):
                        role = r
                        break
                
                # Rating & reviews
                rating_tag = h.find(class_=re.compile(r'rating|score', re.I))
                raw_rating = clean_text(rating_tag.get_text()) if rating_tag else clean_text(h.get_text())
                
                # Split rating and reviews (e.g., "4.5 621 reviews")
                rating_match = re.search(r'(\d+\.\d+|\d+)', raw_rating)
                rating_val = rating_match.group(1) if rating_match else None
                reviews_match = re.search(r'(\d+[\d,]*\s*reviews?)', raw_rating, re.I)
                reviews_val = reviews_match.group(1) if reviews_match else None
                
                if role not in role_brand_map:
                    role_brand_map[role] = title
                    if title not in companies:
                        companies.append(title)
                    company_details[title] = {
                        'name': title,
                        'role': role,
                        'rating': rating_val,
                        'reviews': reviews_val,
                        'is_winner': (role == 'winner')
                    }
                    if role == 'winner' and not winner:
                        winner = title

        # Extract rows from cells-wrap
        cells_wraps = soup.find_all('div', class_='cells-wrap')
        for cw in cells_wraps:
            title_cell = cw.find('div', class_='cell-title')
            if title_cell:
                feat_name = clean_text(title_cell.get_text())
                row_specs = {}
                for role, b_name in role_brand_map.items():
                    c = cw.find('div', class_=lambda cl: cl and 'cell' in cl and role in cl)
                    val = clean_text(c.get_text()) if c else ''
                    row_specs[b_name] = {
                        'value': val,
                        'is_winner': (role == 'winner')
                    }
                comparison_specs[feat_name] = row_specs

    return {
        'url': url,
        'page_title': page_title,
        'comparison_name': comparison_name,
        'template_type': template_type,
        'winner': winner or "Inconclusive / Neutral",
        'companies': companies,
        'company_details': company_details,
        'comparison_specs': comparison_specs,
        'faqs': faqs,
        'summary': summary_text,
        'static_elements': static_elements
    }
