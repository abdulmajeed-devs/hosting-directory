"""
HostAdvice Scraper & Page Builder Pipeline
One-command script to:
1. Scrape comparison pages from HostAdvice
2. Build per-company structured JSON files
3. Generate standalone HTML company comparison pages & index dashboard
"""

import os
import sys
import argparse
from scraper import extract_comparison_urls_from_sitemap, scrape_single_page, save_results
from build_company_profiles import build_company_profiles
from generate_pages import generate_all_pages
from generate_matrix_pages import generate_all_matrix
from config import DEFAULT_OUTPUT_DIR, DEFAULT_CONCURRENCY
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def run_pipeline(limit=None, concurrency=DEFAULT_CONCURRENCY, output_dir=DEFAULT_OUTPUT_DIR, skip_scrape=False, build_matrix=False, bidirectional=False):
    comparisons_json = os.path.join(output_dir, "comparisons_data.json")

    # Step 1: Scraping
    if not skip_scrape or not os.path.exists(comparisons_json):
        print("\n=======================================================")
        print("STEP 1: Scraping Comparison Pages from HostAdvice")
        print("=======================================================")
        urls = extract_comparison_urls_from_sitemap()
        if limit and limit > 0:
            urls = urls[:limit]
            print(f"[*] Limiting run to {len(urls)} pages.")

        start_time = time.time()
        results = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_url = {executor.submit(scrape_single_page, u): u for u in urls}
            done = 0
            for future in as_completed(future_to_url):
                done += 1
                res = future.result()
                results.append(res)
                status_str = "[SUCCESS]" if res.get('status') == 'success' else "[FAILED]"
                name = res.get('comparison_name', res.get('url', ''))[:35]
                print(f"  ({done}/{len(urls)}) {status_str} {name}")

        print(f"[+] Scraping completed in {time.time() - start_time:.2f}s.")
        save_results(results, output_dir=output_dir)
    else:
        print("\n[*] Skipping scraping. Using existing comparisons_data.json.")

    # Step 2: Build Company Profiles
    print("\n=======================================================")
    print("STEP 2: Aggregating Per-Company JSON Profiles")
    print("=======================================================")
    build_company_profiles(comparisons_json, output_dir)

    # Step 3: Generate Company Profile HTML Pages
    print("\n=======================================================")
    print("STEP 3: Generating Responsive Company Pages & Directory")
    print("=======================================================")
    generate_all_pages(output_dir)

    # Step 4: Generate Comparison Matrix Pages
    if build_matrix:
        print("\n=======================================================")
        print("STEP 4: Generating Cross-Company Comparison Matrix Pages")
        print("=======================================================")
        generate_all_matrix(output_dir, bidirectional=bidirectional)

    print("\n=======================================================")
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print(f" - Company JSONs:   {os.path.join(output_dir, 'companies')}")
    print(f" - Profile Pages:   {os.path.join(output_dir, 'pages')}")
    print(f" - Comparison Hub:  {os.path.join(output_dir, 'matrix_comparisons', 'compare_hub.html')}")
    print(f" - Matchup Matrix:  {os.path.join(output_dir, 'matrix_comparisons')}")
    print("=======================================================\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="HostAdvice Scraping and Page Generation Pipeline")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of pages to scrape")
    parser.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY, help="Number of concurrent threads")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Output directory")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip scraping and use existing comparisons_data.json")
    parser.add_argument("--matrix", action="store_true", help="Generate full comparison matrix pages")
    parser.add_argument("--bidirectional", action="store_true", help="Generate bidirectional pairs (2,970 pages)")

    args = parser.parse_args()
    run_pipeline(
        limit=args.limit,
        concurrency=args.concurrency,
        output_dir=args.output_dir,
        skip_scrape=args.skip_scrape,
        build_matrix=args.matrix,
        bidirectional=args.bidirectional
    )
