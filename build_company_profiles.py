"""
Company Profile JSON Builder
Aggregates scraped HostAdvice comparison data into dedicated per-company JSON files.
"""

import os
import json
import re
from collections import defaultdict

# Canonical mapping for normalizing company names
NORMALIZATION_MAP = {
    'blue-host': 'Bluehost',
    'blue host': 'Bluehost',
    'bluehost': 'Bluehost',
    'godaddy': 'GoDaddy',
    'godaddy logo': 'GoDaddy',
    'digital-ocean': 'DigitalOcean',
    'digital ocean': 'DigitalOcean',
    'digitalocean': 'DigitalOcean',
    'amazon web services': 'AWS',
    'amazon-web-services': 'AWS',
    'amazon web services (aws)': 'AWS',
    'aws': 'AWS',
    'google cloud platform': 'Google Cloud Platform',
    'google-cloud-platform': 'Google Cloud Platform',
    'gcp': 'Google Cloud Platform',
    'microsoft azure': 'Microsoft Azure',
    'microsoft-azure': 'Microsoft Azure',
    'azure': 'Microsoft Azure',
    'siteground': 'SiteGround',
    'ionos': 'IONOS',
    'fastcomet': 'FastComet',
    'hostgator': 'HostGator',
    'inmotion': 'InMotion Hosting',
    'inmotion hosting': 'InMotion Hosting',
    'wordpress': 'WordPress.com',
    'wordpress.com': 'WordPress.com',
    'wordpress com': 'WordPress.com',
    'wix com': 'Wix',
    'wix': 'Wix',
    'wix.com': 'Wix',
    'ovh': 'OVHcloud',
    'ovhcloud': 'OVHcloud',
    'hetzner': 'Hetzner',
    'linode': 'Linode',
    'vultr': 'Vultr',
    'tmdhosting': 'TMDHosting',
    'interserver': 'InterServer',
    'namecheap': 'Namecheap',
    'cloudways': 'Cloudways',
    'hostarmada': 'HostArmada',
    'hosting.com': 'A2 Hosting',
    'a2 hosting': 'A2 Hosting',
    'a2-hosting': 'A2 Hosting',
    'contabo': 'Contabo',
    'enom': 'eNom',
    'smarterasp.net': 'SmarterASP.NET',
    'smarterasp-net': 'SmarterASP.NET',
    'host4asp.net': 'Host4ASP.NET',
    'host4asp-net': 'Host4ASP.NET',
    'infinityfree': 'InfinityFree',
    'arvixe': 'Arvixe',
    'squarespace': 'Squarespace'
}

def normalize_name(name):
    if not name:
        return ""
    clean = re.sub(r'\s*Logo$', '', name, flags=re.I).strip().lower()
    return NORMALIZATION_MAP.get(clean, name.strip())

def make_slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def build_company_profiles(comparisons_data_path, output_dir):
    """Parses comparisons_data.json and builds individual company JSONs."""
    if not os.path.exists(comparisons_data_path):
        raise FileNotFoundError(f"Input file not found: {comparisons_data_path}")

    with open(comparisons_data_path, 'r', encoding='utf-8') as f:
        root_data = json.load(f)

    comparisons = root_data.get('data', [])
    print(f"[*] Processing {len(comparisons)} comparisons for company aggregation...")

    companies_data = defaultdict(lambda: {
        'company_name': '',
        'slug': '',
        'profile': {
            'overall_rating': None,
            'review_count': None,
            'starting_price': None,
            'deals_promos': set(),
            'key_features': set()
        },
        'stats': {
            'total_comparisons': 0,
            'wins': 0,
            'losses': 0,
            'ties': 0,
            'win_rate_percentage': 0.0
        },
        'head_to_head': [],
        'specifications': {},
        'faqs': []
    })

    # First pass: map and aggregate comparisons
    for comp in comparisons:
        comp_url = comp.get('url', '')
        comp_name = comp.get('comparison_name', '')
        raw_winner = normalize_name(comp.get('winner', ''))
        raw_companies = [normalize_name(c) for c in comp.get('companies', []) if c]
        
        # Deduplicate companies in comparison
        current_companies = []
        for c in raw_companies:
            if c and c not in current_companies:
                current_companies.append(c)

        if not current_companies:
            continue

        template_type = comp.get('template_type', '')
        comp_specs = comp.get('comparison_specs', {})
        comp_faqs = comp.get('faqs', [])
        comp_details = comp.get('company_details', {})

        # Process each company involved in this comparison
        for company in current_companies:
            c_data = companies_data[company]
            c_data['company_name'] = company
            c_data['slug'] = make_slug(company)
            c_data['stats']['total_comparisons'] += 1

            # Determine opponents
            opponents = [o for o in current_companies if o != company]

            # Determine Win / Loss / Tie
            is_win = (company.lower() == raw_winner.lower())
            is_loss = (raw_winner and not is_win and raw_winner in current_companies)
            
            if is_win:
                result = "Win"
                c_data['stats']['wins'] += 1
            elif is_loss:
                result = "Loss"
                c_data['stats']['losses'] += 1
            else:
                result = "Tie / Inconclusive"
                c_data['stats']['ties'] += 1

            # Head to head entry
            h2h_entry = {
                'comparison_title': comp_name,
                'opponents': opponents,
                'result': result,
                'declared_winner': raw_winner,
                'comparison_url': comp_url,
                'template_type': template_type
            }
            c_data['head_to_head'].append(h2h_entry)

            # Profile data from comp_details
            for raw_b_name, b_info in comp_details.items():
                if normalize_name(raw_b_name) == company:
                    if b_info.get('rating') and not c_data['profile']['overall_rating']:
                        c_data['profile']['overall_rating'] = b_info.get('rating')
                    if b_info.get('reviews') and not c_data['profile']['review_count']:
                        c_data['profile']['review_count'] = b_info.get('reviews')
                    if b_info.get('deal_promo'):
                        c_data['profile']['deals_promos'].add(b_info.get('deal_promo'))
                    for f in b_info.get('features', []):
                        if f:
                            c_data['profile']['key_features'].add(f)

            # Extract specs for this company
            for spec_key, spec_vals in comp_specs.items():
                if isinstance(spec_vals, dict):
                    # Check matching company in dict
                    for b_name, b_spec in spec_vals.items():
                        if normalize_name(b_name) == company:
                            val = b_spec.get('value', '').strip()
                            if val and spec_key not in c_data['specifications']:
                                c_data['specifications'][spec_key] = val
                                if 'price' in spec_key.lower() and not c_data['profile']['starting_price']:
                                    c_data['profile']['starting_price'] = val

            # Append relevant FAQs
            for faq in comp_faqs:
                q = faq.get('question', '')
                a = faq.get('answer', '')
                # include if company name appears in question or answer
                if company.lower() in q.lower() or company.lower() in a.lower():
                    # check duplicate question
                    if not any(f['question'] == q for f in c_data['faqs']):
                        c_data['faqs'].append({
                            'question': q,
                            'answer': a,
                            'source_comparison': comp_name
                        })

    # Calculate final stats and save per-company JSON
    companies_dir = os.path.join(output_dir, "companies")
    os.makedirs(companies_dir, exist_ok=True)
    index_catalog = []

    for company, c_data in companies_data.items():
        total = c_data['stats']['total_comparisons']
        wins = c_data['stats']['wins']
        c_data['stats']['win_rate_percentage'] = round((wins / total) * 100, 1) if total > 0 else 0.0

        # Convert sets to sorted lists for JSON serialization
        c_data['profile']['deals_promos'] = sorted(list(c_data['profile']['deals_promos']))
        c_data['profile']['key_features'] = sorted(list(c_data['profile']['key_features']))

        company_file = os.path.join(companies_dir, f"{c_data['slug']}.json")
        with open(company_file, 'w', encoding='utf-8') as f:
            json.dump(c_data, f, indent=2, ensure_ascii=False)

        index_catalog.append({
            'company_name': company,
            'slug': c_data['slug'],
            'total_comparisons': total,
            'wins': wins,
            'losses': c_data['stats']['losses'],
            'win_rate': f"{c_data['stats']['win_rate_percentage']}%",
            'rating': c_data['profile']['overall_rating'],
            'starting_price': c_data['profile']['starting_price'],
            'json_file': f"companies/{c_data['slug']}.json"
        })

    # Save master company index
    index_catalog.sort(key=lambda x: x['total_comparisons'], reverse=True)
    catalog_path = os.path.join(output_dir, "companies_catalog.json")
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_companies': len(index_catalog),
            'companies': index_catalog
        }, f, indent=2, ensure_ascii=False)

    print(f"[OK] Generated {len(companies_data)} company profiles in: {companies_dir}")
    print(f"[OK] Master company catalog saved to: {catalog_path}")
    return index_catalog

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_json = os.path.join(base_dir, "output", "comparisons_data.json")
    out_dir = os.path.join(base_dir, "output")
    build_company_profiles(input_json, out_dir)
