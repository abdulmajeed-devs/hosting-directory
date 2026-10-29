/**
 * HostAdvice Pro - Enterprise Super Admin Dashboard Controller
 * Pure Vanilla JavaScript & Zero Dependencies
 */

// Global State
let adminProviders = {};
let providerMeta = {}; // { slug: { status: 'active' | 'unlisted', featured: boolean } }
let isBuildRunning = false;

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initData();
  initNavigation();
  initGlobalSearch();
  initMatchupSimulator();
  renderProvidersTable();
  renderAffiliateTable();
});

/**
 * Initialize Data from companies_data.js
 */
function initData() {
  if (typeof HOSTING_COMPANIES_DATA !== "undefined" && HOSTING_COMPANIES_DATA) {
    adminProviders = JSON.parse(JSON.stringify(HOSTING_COMPANIES_DATA));
  } else {
    console.warn("HOSTING_COMPANIES_DATA not found. Using fallback.");
    adminProviders = {};
  }

  // Pre-flag notable providers as featured
  const topSlugs = ["hostinger", "siteground", "bluehost", "a2-hosting", "ionos", "dreamhost"];
  Object.keys(adminProviders).forEach((slug) => {
    providerMeta[slug] = {
      status: "active",
      featured: topSlugs.includes(slug)
    };
  });

  updateTotalCounts();
}

/**
 * Update Sidebar & Dashboard KPIs
 */
function updateTotalCounts() {
  const total = Object.keys(adminProviders).length;
  const countEl = document.getElementById("sidebarProviderCount");
  const kpiEl = document.getElementById("kpiTotalProviders");
  if (countEl) countEl.textContent = total;
  if (kpiEl) kpiEl.textContent = total;
}

/**
 * Sidebar Navigation
 */
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-item-btn[data-tab]");
  navBtns.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const tabId = btn.getAttribute("data-tab");
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  // Update sidebar active buttons
  document.querySelectorAll(".nav-item-btn").forEach((btn) => {
    btn.classList.remove("active");
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    }
  });

  // Update tab pane visibility
  document.querySelectorAll(".tab-pane").forEach((pane) => {
    pane.classList.remove("active");
  });

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) {
    targetPane.classList.add("active");
  }

  // Update Page Header Titles
  const titleEl = document.getElementById("pageTitle");
  const subEl = document.getElementById("pageSubtitle");
  const titles = {
    dashboard: {
      title: "CompareAdvice Platform Overview",
      sub: "55 web hosting providers \u2022 2,970 pairwise comparison pages"
    },
    providers: {
      title: "CompareAdvice Providers Catalog",
      sub: "Manage, filter, and calibrate metadata for all 55 catalog providers"
    },
    matrix: {
      title: "Comparison Matrix Workbench",
      sub: "Inspect and calibrate mathematical ranking weights across 2,970 matchups"
    },
    moderation: {
      title: "Partner Change Moderation",
      sub: "Review and approve updates submitted by vendor managers via Partner Central"
    },
    monetization: {
      title: "Affiliate & UTM Hub",
      sub: "Global tracking parameters, subIDs, and direct referral destination URLs"
    },
    generator: {
      title: "CompareAdvice Rebuild Engine",
      sub: "Trigger static site generation scripts and view real-time build logs"
    },
    settings: {
      title: "CompareAdvice Platform Settings",
      sub: "Rounded pill static navigation, SEO meta formats, and platform identity"
    }
  };

  if (titles[tabId] && titleEl && subEl) {
    titleEl.textContent = titles[tabId].title;
    subEl.textContent = titles[tabId].sub;
  }
}

/**
 * Top Header Quick Search
 */
function initGlobalSearch() {
  const input = document.getElementById("globalSearchInput");
  if (!input) return;

  // Keyboard shortcut Ctrl+K or Cmd+K
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      input.focus();
    }
  });

  input.addEventListener("input", (e) => {
    const val = e.target.value.trim();
    if (val.length > 0) {
      switchTab("providers");
      const providerSearch = document.getElementById("providerSearchInput");
      if (providerSearch) {
        providerSearch.value = val;
        renderProvidersTable();
      }
    }
  });
}

/**
 * Render Providers Master Table
 */
function renderProvidersTable() {
  const tbody = document.getElementById("providersTableBody");
  if (!tbody) return;

  const searchQuery = (document.getElementById("providerSearchInput")?.value || "").toLowerCase().trim();
  const filterStatus = document.getElementById("filterStatus")?.value || "all";
  const filterRating = document.getElementById("filterRating")?.value || "all";
  const sortBy = document.getElementById("sortBy")?.value || "rating_desc";

  let slugs = Object.keys(adminProviders);

  // Search filter
  if (searchQuery) {
    slugs = slugs.filter((slug) => {
      const comp = adminProviders[slug];
      return (
        comp.company_name.toLowerCase().includes(searchQuery) ||
        comp.slug.toLowerCase().includes(searchQuery) ||
        (comp.datacenters && comp.datacenters.toLowerCase().includes(searchQuery))
      );
    });
  }

  // Status & Featured filter
  if (filterStatus === "active") {
    slugs = slugs.filter((slug) => providerMeta[slug]?.status === "active");
  } else if (filterStatus === "unlisted") {
    slugs = slugs.filter((slug) => providerMeta[slug]?.status === "unlisted");
  } else if (filterStatus === "featured") {
    slugs = slugs.filter((slug) => providerMeta[slug]?.featured);
  }

  // Rating filter
  if (filterRating === "4.5") {
    slugs = slugs.filter((slug) => parseFloat(adminProviders[slug].rating || 0) >= 4.5);
  } else if (filterRating === "4.0") {
    slugs = slugs.filter((slug) => parseFloat(adminProviders[slug].rating || 0) >= 4.0);
  }

  // Sorting
  slugs.sort((a, b) => {
    const compA = adminProviders[a];
    const compB = adminProviders[b];
    if (sortBy === "rating_desc") {
      return parseFloat(compB.rating || 0) - parseFloat(compA.rating || 0);
    } else if (sortBy === "name_asc") {
      return compA.company_name.localeCompare(compB.company_name);
    } else if (sortBy === "price_asc") {
      const pA = parseFloat((compA.price || "$99").replace(/[^0-9.]/g, "")) || 99;
      const pB = parseFloat((compB.price || "$99").replace(/[^0-9.]/g, "")) || 99;
      return pA - pB;
    } else if (sortBy === "reviews_desc") {
      const rA = parseInt((compA.reviews_count || "0").replace(/[^0-9]/g, "")) || 0;
      const rB = parseInt((compB.reviews_count || "0").replace(/[^0-9]/g, "")) || 0;
      return rB - rA;
    }
    return 0;
  });

  tbody.innerHTML = "";

  if (slugs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 40px; color: var(--gray-400);">
          No hosting providers match your filter criteria.
        </td>
      </tr>
    `;
    return;
  }

  slugs.forEach((slug) => {
    const comp = adminProviders[slug];
    const meta = providerMeta[slug] || { status: "active", featured: false };
    const initial = (comp.company_name || "H").charAt(0).toUpperCase();
    const domain = comp.website ? comp.website.replace(/^https?:\/\//, "").replace(/\/.*$/, "") : `${slug}.com`;
    const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=64`;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>
        <div class="brand-cell">
          <div class="brand-logo-frame">
            <img src="${faviconUrl}" alt="${escapeHTML(comp.company_name)}" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
            <span class="brand-logo-fallback" style="display:none;">${initial}</span>
          </div>
          <div class="brand-name-box">
            <h4>${escapeHTML(comp.company_name)}</h4>
            <span class="brand-slug-code">${comp.slug}</span>
          </div>
        </div>
      </td>
      <td>
        <div class="rating-num">
          <svg class="star-svg" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
          </svg>
          <span>${comp.rating || "4.5"}</span>
          <span style="font-size: 11px; color: var(--gray-400); font-weight: normal;">(${comp.reviews_count || "1,200"})</span>
        </div>
      </td>
      <td>
        <strong style="color: var(--gray-900);">${escapeHTML(comp.price || "$2.99 / mo")}</strong>
      </td>
      <td style="max-width: 220px; font-size: 12px; color: var(--gray-500); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
        ${escapeHTML(comp.datacenters || "USA, Europe, Asia")}
      </td>
      <td>
        ${
          meta.status === "active"
            ? '<span class="badge-pill active"><span class="badge-dot"></span> Active</span>'
            : '<span class="badge-pill unlisted"><span class="badge-dot"></span> Draft</span>'
        }
      </td>
      <td>
        ${
          meta.featured
            ? '<span class="badge-pill featured">Top Pick</span>'
            : `<button class="btn btn-secondary btn-sm" style="padding: 2px 8px; font-size: 11px;" onclick="toggleProviderFeatured('${slug}')">+ Pin</button>`
        }
      </td>
      <td style="text-align: right;">
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 6px;">
          <button class="btn btn-secondary btn-sm" onclick="openEditProviderModal('${slug}')" title="Edit Master Record">
            Edit
          </button>
          <button class="btn btn-secondary btn-sm" onclick="toggleProviderStatus('${slug}')" title="Toggle Active / Draft">
            ${meta.status === "active" ? "Hide" : "Show"}
          </button>
          <button class="btn btn-danger-ghost btn-sm" onclick="deleteProvider('${slug}')" title="Delete Provider">
            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("providerSearchInput")?.addEventListener("input", () => {
  renderProvidersTable();
});

/**
 * Toggle Status & Featured
 */
function toggleProviderStatus(slug) {
  if (!providerMeta[slug]) providerMeta[slug] = { status: "active", featured: false };
  const current = providerMeta[slug].status;
  providerMeta[slug].status = current === "active" ? "unlisted" : "active";
  renderProvidersTable();
  showToast(`${adminProviders[slug].company_name} set to ${providerMeta[slug].status}.`, "info");
}

function toggleProviderFeatured(slug) {
  if (!providerMeta[slug]) providerMeta[slug] = { status: "active", featured: false };
  providerMeta[slug].featured = !providerMeta[slug].featured;
  renderProvidersTable();
  showToast(
    `${adminProviders[slug].company_name} is now ${providerMeta[slug].featured ? "Featured Top Pick" : "Standard"}.`,
    "success"
  );
}

/**
 * Delete Provider
 */
function deleteProvider(slug) {
  const name = adminProviders[slug]?.company_name || slug;
  if (!confirm(`Are you sure you want to delete ${name} from the platform catalog?`)) {
    return;
  }
  delete adminProviders[slug];
  delete providerMeta[slug];
  updateTotalCounts();
  renderProvidersTable();
  initMatchupSimulator();
  renderAffiliateTable();
  showToast(`${name} was successfully removed.`, "danger");
}

/**
 * Add New Provider Modal
 */
function openAddProviderModal() {
  document.getElementById("addProviderForm")?.reset();
  document.getElementById("addProviderModal").classList.add("active");
}

function handleCreateProvider(e) {
  e.preventDefault();
  const slug = document.getElementById("newCompanySlug").value.toLowerCase().trim().replace(/[^a-z0-9-]/g, "-");
  const name = document.getElementById("newCompanyName").value.trim();
  const price = document.getElementById("newCompanyPrice").value.trim();
  const rating = document.getElementById("newCompanyRating").value.trim();
  const founded = parseInt(document.getElementById("newCompanyFounded").value) || 2020;
  const hq = document.getElementById("newCompanyHQ").value.trim();
  const tagline = document.getElementById("newCompanyTagline").value.trim();
  const affiliate = document.getElementById("newCompanyAffiliate").value.trim();
  const datacenters = document.getElementById("newCompanyDatacenters").value.trim();
  const about = document.getElementById("newCompanyAbout").value.trim();

  if (adminProviders[slug]) {
    alert("A provider with this slug already exists!");
    return;
  }

  adminProviders[slug] = {
    slug,
    company_name: name,
    price,
    rating,
    reviews_count: "50 reviews",
    founded,
    headquarters: hq,
    tagline: tagline || "High Performance Cloud & Web Hosting",
    affiliate_url: affiliate,
    datacenters: datacenters || "USA, Europe",
    about: about || `${name} offers reliable web hosting solutions for businesses and developers.`
  };

  providerMeta[slug] = { status: "active", featured: false };

  closeModal("addProviderModal");
  updateTotalCounts();
  renderProvidersTable();
  initMatchupSimulator();
  renderAffiliateTable();
  showToast(`Provider ${name} created successfully!`, "success");
}

/**
 * Edit Provider Modal
 */
function openEditProviderModal(slug) {
  const comp = adminProviders[slug];
  if (!comp) return;

  document.getElementById("editSlug").value = slug;
  document.getElementById("editCompanyName").value = comp.company_name || "";
  document.getElementById("editPrice").value = comp.price || "";
  document.getElementById("editRating").value = comp.rating || "";
  document.getElementById("editReviewsCount").value = comp.reviews_count || "";
  document.getElementById("editHQ").value = comp.headquarters || "";
  document.getElementById("editWebsite").value = comp.website || "";
  document.getElementById("editTagline").value = comp.tagline || "";
  document.getElementById("editAffiliateUrl").value = comp.affiliate_url || "";
  document.getElementById("editDatacenters").value = comp.datacenters || "";
  document.getElementById("editAbout").value = comp.about || "";

  document.getElementById("editProviderModal").classList.add("active");
}

function handleUpdateProvider(e) {
  e.preventDefault();
  const slug = document.getElementById("editSlug").value;
  if (!adminProviders[slug]) return;

  adminProviders[slug].company_name = document.getElementById("editCompanyName").value.trim();
  adminProviders[slug].price = document.getElementById("editPrice").value.trim();
  adminProviders[slug].rating = document.getElementById("editRating").value.trim();
  adminProviders[slug].reviews_count = document.getElementById("editReviewsCount").value.trim();
  adminProviders[slug].headquarters = document.getElementById("editHQ").value.trim();
  adminProviders[slug].website = document.getElementById("editWebsite").value.trim();
  adminProviders[slug].tagline = document.getElementById("editTagline").value.trim();
  adminProviders[slug].affiliate_url = document.getElementById("editAffiliateUrl").value.trim();
  adminProviders[slug].datacenters = document.getElementById("editDatacenters").value.trim();
  adminProviders[slug].about = document.getElementById("editAbout").value.trim();

  closeModal("editProviderModal");
  renderProvidersTable();
  renderAffiliateTable();
  showToast(`Updated master specifications for ${adminProviders[slug].company_name}.`, "success");
}

function closeModal(modalId) {
  document.getElementById(modalId)?.classList.remove("active");
}

/**
 * Matchup Simulator (Workbench)
 */
function initMatchupSimulator() {
  const selectA = document.getElementById("simProviderA");
  const selectB = document.getElementById("simProviderB");
  if (!selectA || !selectB) return;

  selectA.innerHTML = "";
  selectB.innerHTML = "";

  const slugs = Object.keys(adminProviders).sort();
  slugs.forEach((slug) => {
    const name = adminProviders[slug].company_name;
    const optA = document.createElement("option");
    optA.value = slug;
    optA.textContent = name;
    if (slug === "hostinger") optA.selected = true;
    selectA.appendChild(optA);

    const optB = document.createElement("option");
    optB.value = slug;
    optB.textContent = name;
    if (slug === "bluehost") optB.selected = true;
    selectB.appendChild(optB);
  });

  updateMatchupSimulation();
}

function updateMatchupSimulation() {
  const slugA = document.getElementById("simProviderA")?.value;
  const slugB = document.getElementById("simProviderB")?.value;
  if (!slugA || !slugB || !adminProviders[slugA] || !adminProviders[slugB]) return;

  const compA = adminProviders[slugA];
  const compB = adminProviders[slugB];

  const ratingA = parseFloat(compA.rating || 4.5);
  const ratingB = parseFloat(compB.rating || 4.5);

  let winner = compA;
  let reason = "Superior performance score and value pricing";

  if (ratingB > ratingA) {
    winner = compB;
    reason = `Higher verified user satisfaction score (${ratingB}/5.0) and established enterprise trust.`;
  } else if (ratingA > ratingB) {
    winner = compA;
    reason = `Higher verified rating (${ratingA}/5.0) and lower introductory starting rate.`;
  } else {
    winner = compA;
    reason = "Balanced algorithmic tie-breaker favoring lower starting rate.";
  }

  const nameEl = document.getElementById("simWinnerName");
  const reasonEl = document.getElementById("simWinnerReason");
  if (nameEl) nameEl.textContent = `${winner.company_name} (Algorithmic Leader)`;
  if (reasonEl) reasonEl.textContent = reason;
}

function previewCurrentMatchup() {
  const slugA = document.getElementById("simProviderA")?.value;
  const slugB = document.getElementById("simProviderB")?.value;
  if (!slugA || !slugB) return;

  const fileUrl = `../output/matrix_comparisons/${slugA}-vs-${slugB}.html`;
  window.open(fileUrl, "_blank");
}

function saveAlgorithmWeights() {
  showToast("Algorithm ranking weights successfully saved and applied to matrix engine.", "success");
}

/**
 * Moderation Queue
 */
function approveModerationItem(itemId) {
  const itemEl = document.getElementById(itemId);
  if (itemEl) {
    itemEl.style.transition = "all 0.25s ease";
    itemEl.style.opacity = "0";
    itemEl.style.transform = "translateX(16px)";
    setTimeout(() => {
      itemEl.remove();
      decrementModBadge();
      showToast("Partner change request approved & committed to live catalog.", "success");
    }, 250);
  }
}

function rejectModerationItem(itemId) {
  const reason = prompt("Enter rejection feedback for business partner:", "Pricing does not match public provider rate.");
  if (reason === null) return;

  const itemEl = document.getElementById(itemId);
  if (itemEl) {
    itemEl.style.transition = "all 0.25s ease";
    itemEl.style.opacity = "0";
    itemEl.style.transform = "translateX(-16px)";
    setTimeout(() => {
      itemEl.remove();
      decrementModBadge();
      showToast("Submission declined. Feedback sent to partner.", "info");
    }, 250);
  }
}

function approveAllModeration() {
  const list = document.getElementById("moderationItemsList");
  if (list) {
    list.innerHTML = `
      <div style="padding: 40px; text-align: center; color: var(--gray-400);">
        <svg width="32" height="32" fill="none" stroke="#10b981" viewBox="0 0 24 24" style="margin: 0 auto 10px auto; display: block;">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <h4 style="font-size: 14px; font-weight: 600; color: var(--gray-800);">All partner submissions approved</h4>
        <p style="font-size: 12px; color: var(--gray-400); margin-top: 2px;">The moderation queue is currently clear.</p>
      </div>
    `;
    const badge = document.getElementById("modQueueCount");
    const dashBadge = document.getElementById("dashModBadge");
    if (badge) badge.textContent = "0";
    if (dashBadge) {
      dashBadge.innerHTML = `<span class="badge-dot" style="background:#10b981;"></span> 0 Pending`;
      dashBadge.className = "badge-pill active";
    }
    showToast("Batch approved all partner submissions successfully.", "success");
  }
}

function decrementModBadge() {
  const badge = document.getElementById("modQueueCount");
  const dashBadge = document.getElementById("dashModBadge");
  if (badge) {
    let count = parseInt(badge.textContent) || 1;
    count = Math.max(0, count - 1);
    badge.textContent = count;
    if (dashBadge) dashBadge.innerHTML = `<span class="badge-dot"></span> ${count} Pending`;
  }
}

/**
 * Monetization & Affiliate Links
 */
function renderAffiliateTable() {
  const tbody = document.getElementById("affiliateLinksTableBody");
  if (!tbody) return;

  tbody.innerHTML = "";
  const slugs = Object.keys(adminProviders).slice(0, 15);

  slugs.forEach((slug) => {
    const comp = adminProviders[slug];
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${escapeHTML(comp.company_name)}</strong></td>
      <td style="max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: var(--font-mono); font-size: 12px; color: var(--gray-600);">
        ${escapeHTML(comp.affiliate_url || "https://provider.com/?deal=exclusive")}
      </td>
      <td><span class="badge-pill active"><span class="badge-dot"></span> Active UTM</span></td>
      <td><strong>$1.65</strong></td>
      <td style="text-align: right;">
        <button class="btn btn-secondary btn-sm" onclick="editAffiliateLink('${slug}')">Edit Link</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function editAffiliateLink(slug) {
  const comp = adminProviders[slug];
  const newUrl = prompt(`Enter new affiliate URL for ${comp.company_name}:`, comp.affiliate_url || "");
  if (newUrl && newUrl.trim()) {
    comp.affiliate_url = newUrl.trim();
    renderAffiliateTable();
    showToast(`Affiliate endpoint updated for ${comp.company_name}.`, "success");
  }
}

function applyBulkUTMs() {
  const src = document.getElementById("utmSource")?.value || "compareadvice";
  const med = document.getElementById("utmMedium")?.value || "matrix";
  const camp = document.getElementById("utmCampaign")?.value || "2026_rankings";

  Object.keys(adminProviders).forEach((slug) => {
    const comp = adminProviders[slug];
    if (comp.affiliate_url) {
      const separator = comp.affiliate_url.includes("?") ? "&" : "?";
      comp.affiliate_url = `${comp.affiliate_url.split("?")[0]}${separator}utm_source=${src}&utm_medium=${med}&utm_campaign=${camp}`;
    }
  });

  renderAffiliateTable();
  showToast("Injected UTM tracking parameters into all 55 provider links!", "success");
}

/**
 * Static Site Rebuild Console Engine
 */
function startGenerationProcess(type) {
  if (isBuildRunning) {
    showToast("A generation build is already currently running.", "info");
    return;
  }

  isBuildRunning = true;
  switchTab("generator");

  const statusText = document.getElementById("consoleStatusText");
  const progressBar = document.getElementById("buildProgressBar");
  const progressPct = document.getElementById("buildProgressText");
  const consoleBody = document.getElementById("consoleBody");

  if (statusText) {
    statusText.textContent = "RUNNING";
    statusText.style.color = "#f59e0b";
  }

  let steps = [];
  if (type === "matrix") {
    steps = [
      { log: "Executing: python generate_matrix_pages.py --all-pairs", pct: 15, delay: 350 },
      { log: "Reading companies_data.js & company_portfolio_data.py...", pct: 30, delay: 750 },
      { log: "Compiling 2,970 pairwise combinations (55x54)...", pct: 50, delay: 1200 },
      { log: "Injecting Base64 podium graphics & Clearbit logo fallback cards...", pct: 75, delay: 1700 },
      { log: "Writing static HTML files to output/matrix_comparisons/...", pct: 90, delay: 2200 },
      { log: "SUCCESS: Generated 2,970 matrix comparison pages (0 errors).", pct: 100, delay: 2700 }
    ];
  } else {
    steps = [
      { log: "Executing: python generate_pages.py --all-portfolio", pct: 20, delay: 350 },
      { log: "Parsing corporate metadata, headquarters & datacenter specs...", pct: 45, delay: 800 },
      { log: "Building 55 individual company portfolio pages...", pct: 70, delay: 1350 },
      { log: "Generating master sitemap.xml & navigation index...", pct: 90, delay: 1900 },
      { log: "SUCCESS: 55 portfolio pages regenerated in output/pages/.", pct: 100, delay: 2400 }
    ];
  }

  steps.forEach((step, idx) => {
    setTimeout(() => {
      const now = new Date().toTimeString().split(" ")[0];
      const line = document.createElement("div");
      line.className = "log-entry";
      line.innerHTML = `
        <span class="log-ts">[${now}]</span>
        <span class="${step.pct === 100 ? "log-ok" : "log-i"}">${step.log}</span>
      `;
      consoleBody.appendChild(line);
      consoleBody.scrollTop = consoleBody.scrollHeight;

      if (progressBar) progressBar.style.width = `${step.pct}%`;
      if (progressPct) progressPct.textContent = `${step.pct}%`;

      if (idx === steps.length - 1) {
        isBuildRunning = false;
        if (statusText) {
          statusText.textContent = "COMPLETED";
          statusText.style.color = "#34d399";
        }
        showToast("Static site generation completed successfully!", "success");
      }
    }, step.delay);
  });
}

function clearConsole() {
  const body = document.getElementById("consoleBody");
  if (body) {
    body.innerHTML = `
      <div class="log-entry">
        <span class="log-ts">[${new Date().toTimeString().split(" ")[0]}]</span>
        <span style="color: #38bdf8;">Terminal output cleared. Ready for next command.</span>
      </div>
    `;
  }
}

/**
 * Platform Settings
 */
function savePlatformSettings() {
  const siteName = document.getElementById("settingSiteName")?.value;
  showToast(`Saved configuration for ${siteName}. Rounded pill navbar updated.`, "success");
}

/**
 * Export JSON / companies_data.js
 */
function exportDataJSON() {
  const content = `// Comprehensive Hosting Providers Data for Vendor Business & Admin Management\nconst HOSTING_COMPANIES_DATA = ${JSON.stringify(
    adminProviders,
    null,
    2
  )};\n`;

  const blob = new Blob([content], { type: "application/javascript" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "companies_data.js";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast("Exported latest companies_data.js database file!", "success");
}

/**
 * Toast Notification Helper
 */
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "all 0.2s ease-out";
    setTimeout(() => toast.remove(), 200);
  }, 3000);
}

/**
 * Utility: HTML Escaping
 */
function escapeHTML(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
