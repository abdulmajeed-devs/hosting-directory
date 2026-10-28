"""
HostAdvice Comparison Pages Scraper
Extracts structured comparison data, company ratings, winners, side-by-side specifications,
FAQs, and static element signatures from HostAdvice comparison pages.
"""

import os
import sys
import json
import csv
import time
import argparse
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Local imports
from config import DEFAULT_SITEMAP_URL, DEFAULT_HEADERS, DEFAULT_OUTPUT_DIR, DEFAULT_CONCURRENCY, DEFAULT_TIMEOUT, DEFAULT_REQUEST_DELAY
from parser import parse_comparison_page


def fetch_url(url, headers=None, timeout=DEFAULT_TIMEOUT, max_retries=2):
    """Fetches URL content with retry logic and custom headers."""
    hdrs = headers or DEFAULT_HEADERS
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    return resp.read().decode('utf-8', errors='ignore')
        except Exception as e:
            if attempt == max_retries:
                print(f"[ERROR] Failed to fetch {url}: {e}")
                return None
            time.sleep(0.5)
    return None


def extract_comparison_urls_from_sitemap(sitemap_url=DEFAULT_SITEMAP_URL):
    """
    Extracts all company comparison URLs listed under the Human Sitemap page.
    Includes the Top 50 host comparisons and navigation comparisons.
    """
    print(f"[*] Fetching sitemap from: {sitemap_url}")
    html = fetch_url(sitemap_url)
    if not html:
        print("[!] Could not fetch human sitemap page.")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    extracted_urls = []
    seen = set()

    # 1. Section: Top 50 host vs host comparisons
    for h in soup.find_all(['h1', 'h2']):
        if 'Top 50 host vs host comparisons' in h.get_text():
            ul = h.find_next_sibling('ul')
            if ul:
                for a in ul.find_all('a'):
                    href = a.get('href', '').strip()
                    if href and href not in seen and '/tools/web-hosting-comparison/' in href:
                        seen.add(href)
                        extracted_urls.append(href)

    # 2. Additional navigation comparison links
    for a in soup.find_all('a'):
        href = a.get('href', '').strip()
        if '/tools/web-hosting-comparison/' in href:
            if not href.startswith('http'):
                href = urllib.parse.urljoin(sitemap_url, href)
            if href.rstrip('/') != 'https://hostadvice.com/tools/web-hosting-comparison' and href not in seen:
                seen.add(href)
                extracted_urls.append(href)

    print(f"[+] Found {len(extracted_urls)} comparison page URLs from sitemap.")
    return extracted_urls


def scrape_single_page(url):
    """Worker task to scrape and parse a single comparison page."""
    html = fetch_url(url)
    if not html:
        return {'url': url, 'status': 'failed', 'error': 'Fetch error'}
    
    try:
        data = parse_comparison_page(html, url=url)
        data['status'] = 'success'
        return data
    except Exception as e:
        return {'url': url, 'status': 'failed', 'error': str(e)}


def save_results(results, output_dir=DEFAULT_OUTPUT_DIR):
    """Saves scraping results to JSON and multiple CSV formats."""
    os.makedirs(output_dir, exist_ok=True)
    
    successful = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') != 'success']

    # 1. Full JSON export
    json_path = os.path.join(output_dir, "comparisons_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total_scraped': len(results),
            'successful_count': len(successful),
            'failed_count': len(failed),
            'data': successful,
            'failed': failed
        }, f, indent=2, ensure_ascii=False)
    print(f"[OK] Full structured JSON saved to: {json_path}")

    # 2. Main Summary CSV
    summary_csv = os.path.join(output_dir, "comparisons_summary.csv")
    with open(summary_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'URL', 'Comparison_Name', 'Template_Type', 'Winner',
            'Companies', 'Companies_Count', 'Specs_Count', 'FAQs_Count',
            'Verdict_Summary'
        ])
        for r in successful:
            writer.writerow([
                r['url'],
                r.get('comparison_name', ''),
                r.get('template_type', ''),
                r.get('winner', ''),
                " vs ".join(r.get('companies', [])),
                len(r.get('companies', [])),
                len(r.get('comparison_specs', {})),
                len(r.get('faqs', [])),
                r.get('summary', '')[:200]
            ])
    print(f"[OK] Summary CSV saved to: {summary_csv}")

    # 3. Flat Specifications CSV (Long Format)
    specs_csv = os.path.join(output_dir, "comparison_specs.csv")
    with open(specs_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Comparison_Name', 'Feature_Attribute', 'Company', 'Value', 'Is_Winner', 'URL'])
        for r in successful:
            comp_name = r.get('comparison_name', '')
            url = r.get('url', '')
            for feat, comp_vals in r.get('comparison_specs', {}).items():
                if isinstance(comp_vals, dict):
                    for b_name, b_data in comp_vals.items():
                        writer.writerow([
                            comp_name,
                            feat,
                            b_name,
                            b_data.get('value', ''),
                            b_data.get('is_winner', False),
                            url
                        ])
    print(f"[OK] Comparison Specs CSV saved to: {specs_csv}")

    # 4. Static Elements Audit CSV
    audit_csv = os.path.join(output_dir, "static_elements_audit.csv")
    with open(audit_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        header = ['URL', 'Template_Type']
        sample_el = successful[0].get('static_elements', {}) if successful else {}
        el_keys = list(sample_el.keys())
        writer.writerow(header + el_keys)
        for r in successful:
            row = [r['url'], r.get('template_type', '')]
            se = r.get('static_elements', {})
            for k in el_keys:
                row.append(se.get(k, False))
            writer.writerow(row)
    print(f"[OK] Static Elements Audit CSV saved to: {audit_csv}")


def main():
    parser = argparse.ArgumentParser(description="HostAdvice Comparison Pages Scraper")
    parser.add_argument("--urls-file", type=str, help="Optional path to a JSON or text file containing comparison URLs")
    parser.add_argument("--url", type=str, help="Single comparison URL to scrape")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pages to scrape (e.g. 5 for testing)")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, help=f"Number of concurrent threads (default: {DEFAULT_CONCURRENCY})")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR, help=f"Directory to save output files (default: {DEFAULT_OUTPUT_DIR})")
    
    args = parser.parse_args()

    # Determine URLs
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls_file:
        with open(args.urls_file, 'r', encoding='utf-8') as f:
            if args.urls_file.endswith('.json'):
                urls = json.load(f)
            else:
                urls = [line.strip() for line in f if line.strip()]
    else:
        # Default: auto-discover from human sitemap
        urls = extract_comparison_urls_from_sitemap()

    if not urls:
        print("[!] No URLs found to scrape.")
        sys.exit(1)

    if args.limit and args.limit > 0:
        urls = urls[:args.limit]
        print(f"[*] Limiting run to {len(urls)} URLs.")

    print(f"[*] Beginning scrape of {len(urls)} comparison pages with concurrency={args.concurrency}...")
    start_time = time.time()
    
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        future_to_url = {executor.submit(scrape_single_page, u): u for u in urls}
        completed_count = 0
        for future in as_completed(future_to_url):
            completed_count += 1
            res = future.result()
            results.append(res)
            status_str = f"[{res.get('status').upper()}]" if res.get('status') == 'success' else f"[FAILED]"
            title_preview = res.get('comparison_name', res.get('url', ''))[:40]
            print(f"  ({completed_count}/{len(urls)}) {status_str} {title_preview}")

    elapsed = time.time() - start_time
    print(f"\n[+] Finished scraping {len(results)} pages in {elapsed:.2f} seconds.")
    
    save_results(results, output_dir=args.output_dir)


if __name__ == '__main__':
    main()
