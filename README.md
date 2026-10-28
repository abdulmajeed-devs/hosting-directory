# HostAdvice Comparison Scraper & Company Page Generator

A complete end-to-end data pipeline that:
1. **Scrapes** all hosting comparison pages from the [HostAdvice Human Sitemap](https://hostadvice.com/human-sitemap/).
2. **Aggregates** the data into individual, structured **per-company JSON profiles** (with win/loss records, ratings, aggregated specs, and FAQs).
3. **Generates** modern, responsive **HTML company profile pages** and an interactive **master directory dashboard**.

---

## Quick Start (One Command)

To run the entire pipeline end-to-end (Scrape &rarr; Company JSONs &rarr; HTML Pages):

```bash
cd C:\Users\786\.gemini\antigravity\scratch\hostadvice_scraper

# Run full pipeline
python pipeline.py

# Or if you already have the scraped data and just want to rebuild JSONs and HTML pages:
python pipeline.py --skip-scrape
```

---

## Pipeline Workflow

```
[HostAdvice Sitemap]
         │
         ▼ (scraper.py)
[output/comparisons_data.json] ──► 55 Comparison Pages
         │
         ▼ (build_company_profiles.py)
[output/companies/*.json] ───────► 31 Company JSON Profiles + Catalog Index
         │
         ▼ (generate_pages.py)
[output/pages/*.html] ───────────► 31 Responsive Company Pages + index.html Portal
```

---

## 1. How Each Company JSON Is Structured

Located in: `output/companies/<company-slug>.json` (e.g. `godaddy.json`, `bluehost.json`, `hostinger.json`).

```json
{
  "company_name": "GoDaddy",
  "slug": "godaddy",
  "profile": {
    "overall_rating": "4.5",
    "review_count": "621 reviews",
    "starting_price": "$ 0.99 / month",
    "deals_promos": [],
    "key_features": []
  },
  "stats": {
    "total_comparisons": 17,
    "wins": 8,
    "losses": 7,
    "ties": 2,
    "win_rate_percentage": 47.1
  },
  "head_to_head": [
    {
      "comparison_title": "Wix vs GoDaddy",
      "opponents": ["Wix"],
      "result": "Loss",
      "declared_winner": "Wix",
      "comparison_url": "https://hostadvice.com/tools/web-hosting-comparison/godaddy-vs-wix-com/",
      "template_type": "editorial"
    },
    {
      "comparison_title": "Microsoft Azure vs GoDaddy",
      "opponents": ["Microsoft Azure"],
      "result": "Win",
      "declared_winner": "GoDaddy",
      "comparison_url": "https://hostadvice.com/tools/web-hosting-comparison/godaddy-vs-microsoft-azure/",
      "template_type": "spec_grid"
    }
  ],
  "specifications": {
    "Starting price": "$ 0.99 / month",
    "Free domain": "Yes",
    "Coupons": "Coupons18",
    "User Friendly": "4.5",
    "Support": "4.5",
    "Features": "4.5",
    "Reliability": "4.5"
  },
  "faqs": [
    {
      "question": "Can I migrate from GoDaddy to Google Cloud Platform easily?",
      "answer": "Yes, but it requires manual database and file transfer...",
      "source_comparison": "GoDaddy vs Google Cloud Platform"
    }
  ]
}
```

---

## 2. Integrating Company Data into Pages

### Method A: Use the Built-in Page Generator (Static HTML)
Run:
```bash
python generate_pages.py
```
This generates:
* **[output/pages/index.html](output/pages/index.html)**: Searchable dashboard listing all 31 companies with their ratings, comparison counts, win rates, and starting prices.
* **[output/pages/<slug>.html](output/pages/)**: Standalone, responsive profile pages with head-to-head matchup tables, spec matrices, and FAQ accordions.

### Method B: Client-Side Integration (Vanilla JavaScript / Fetch)
If integrating into an existing HTML website:

```html
<div id="company-card"></div>

<script>
async function loadCompany(slug) {
    const res = await fetch(`companies/${slug}.json`);
    const data = await res.json();
    
    document.getElementById('company-card').innerHTML = `
        <h2>${data.company_name}</h2>
        <p>Rating: <strong>${data.profile.overall_rating || 'N/A'}/5</strong> (${data.profile.review_count || ''})</p>
        <p>Record: <strong>${data.stats.wins}W - ${data.stats.losses}L</strong> (${data.stats.win_rate_percentage}% Win Rate)</p>
        <h3>Head-to-Head Matches:</h3>
        <ul>
            ${data.head_to_head.map(m => `
                <li>vs ${m.opponents.join(', ')}: <strong>${m.result}</strong> (<a href="${m.comparison_url}" target="_blank">View</a>)</li>
            `).join('')}
        </ul>
    `;
}

// Load GoDaddy data
loadCompany('godaddy');
</script>
```

### Method C: Modern Static Site Generators (Next.js / Astro / 11ty)
Load the company JSONs directly during build time:

```javascript
// Example in Astro (pages/[company].astro) or Next.js (getStaticProps)
import fs from 'fs';
import path from 'path';

export async function getStaticPaths() {
    const dir = path.join(process.cwd(), 'output/companies');
    const files = fs.readdirSync(dir);
    return files.map(file => ({
        params: { company: file.replace('.json', '') },
        props: { data: JSON.parse(fs.readFileSync(path.join(dir, file), 'utf-8')) }
    }));
}
```

---

## Individual Script Reference

| Script | Purpose | Command |
|---|---|---|
| `pipeline.py` | Runs all 3 steps end-to-end | `python pipeline.py` |
| `scraper.py` | Scrapes comparison pages | `python scraper.py --limit 10` |
| `build_company_profiles.py` | Aggregates per-company JSONs | `python build_company_profiles.py` |
| `generate_pages.py` | Generates HTML pages & dashboard | `python generate_pages.py` |
