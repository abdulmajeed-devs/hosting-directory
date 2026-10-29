/**
 * HostCompare Vendor Business Portal - Dynamic Interactive Controller
 */

// State Management
let currentSlug = "hostinger";
let currentCompany = null;
let hasUnsavedChanges = false;
let currentFAQs = [];

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initCompanySelector();
  initNavigation();
  initFormChangeListeners();
  loadCompany(currentSlug);
});

/**
 * Populate Company Switcher with 55 Providers
 */
function initCompanySelector() {
  const select = document.getElementById("companySelector");
  if (!select || typeof HOSTING_COMPANIES_DATA === "undefined") return;

  select.innerHTML = "";
  const slugs = Object.keys(HOSTING_COMPANIES_DATA).sort();

  slugs.forEach((slug) => {
    const comp = HOSTING_COMPANIES_DATA[slug];
    const opt = document.createElement("option");
    opt.value = slug;
    opt.textContent = `${comp.company_name} - ${comp.rating}/5.0`;
    if (slug === currentSlug) opt.selected = true;
    select.appendChild(opt);
  });

  select.addEventListener("change", (e) => {
    if (hasUnsavedChanges) {
      if (!confirm("You have unsaved changes. Switch company anyway?")) {
        select.value = currentSlug;
        return;
      }
    }
    loadCompany(e.target.value);
  });
}

/**
 * Tab Navigation Controller
 */
function initNavigation() {
  const navLinks = document.querySelectorAll(".nav-link[data-tab]");
  navLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const tabId = link.getAttribute("data-tab");
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  // Update nav links
  document.querySelectorAll(".nav-link[data-tab]").forEach((l) => {
    l.classList.remove("active");
    if (l.getAttribute("data-tab") === tabId) l.classList.add("active");
  });

  // Update tab panes
  document.querySelectorAll(".tab-pane").forEach((pane) => {
    pane.classList.remove("active");
  });

  const targetPane = document.getElementById(`tab-${tabId}`);
  if (targetPane) targetPane.classList.add("active");

  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * Load Company Data into UI
 */
function loadCompany(slug) {
  if (!HOSTING_COMPANIES_DATA[slug]) return;

  currentSlug = slug;
  currentCompany = JSON.parse(JSON.stringify(HOSTING_COMPANIES_DATA[slug]));
  hasUnsavedChanges = false;
  updateUnsavedStatus(false);

  // Set Top Header Data
  document.getElementById("companyNameHeader").textContent = currentCompany.company_name;
  document.getElementById("userAvatarLetter").textContent = currentCompany.company_name.charAt(0);

  // Set Profile Tab Fields
  setInputValue("profileName", currentCompany.company_name);
  setInputValue("profileSlug", currentCompany.slug);
  setInputValue("profileTagline", currentCompany.tagline);
  setInputValue("profileFounded", currentCompany.founded);
  setInputValue("profileHq", currentCompany.headquarters);
  setInputValue("profileCeo", currentCompany.ceo_founder);
  setInputValue("profileWebsite", currentCompany.website);
  setInputValue("profileAbout", currentCompany.about);

  // Logo Preview
  const logoUrl = getCompanyLogoUrl(currentCompany);
  const logoImg = document.getElementById("logoPreviewImg");
  if (logoImg) {
    logoImg.onerror = () => handleLogoError(logoImg);
    logoImg.src = logoUrl;
  }

  // Set Pricing & Deals Fields
  setInputValue("pricingStarting", currentCompany.pricing_details?.starting_price || currentCompany.price);
  setInputValue("pricingRenewal", currentCompany.pricing_details?.renewal_price || "$ 5.99 / mo");
  setInputValue("pricingDiscountBadge", currentCompany.pricing_details?.discount_badge || "Special Deal");
  setInputValue("pricingCoupon", currentCompany.pricing_details?.coupon_code || "HOSTCOMPARE2026");
  setInputValue("pricingMoneyBack", currentCompany.pricing_details?.money_back_days || 30);
  setInputValue("pricingAffiliate", currentCompany.affiliate_url);

  // Set Services Toggles
  const services = currentCompany.services || {};
  setCheckboxValue("serviceShared", services.shared);
  setCheckboxValue("serviceWordpress", services.wordpress);
  setCheckboxValue("serviceVps", services.vps);
  setCheckboxValue("serviceCloud", services.cloud);
  setCheckboxValue("serviceDedicated", services.dedicated);
  setCheckboxValue("serviceReseller", services.reseller);

  // Set Features Toggles
  const features = currentCompany.features || {};
  setCheckboxValue("featSsl", features.free_ssl);
  setCheckboxValue("featDomain", features.free_domain);
  setCheckboxValue("featNvme", features.nvme_storage);
  setCheckboxValue("featBackups", features.daily_backups);
  setCheckboxValue("featCpanel", features.cpanel);
  setCheckboxValue("featChat", features.live_chat);
  setCheckboxValue("featDdos", features.ddos_protection);
  setCheckboxValue("featMigration", features.free_migration);
  setCheckboxValue("featStaging", features.staging_tool);

  // Set Datacenter & Tech Specs
  setInputValue("techDatacenters", currentCompany.datacenters);
  setInputValue("techUptime", currentCompany.specs?.uptime || "99.9%");
  setInputValue("techWebServer", currentCompany.specs?.web_server || "LiteSpeed / Nginx");

  // Set Reputation & Trust
  setInputValue("repTrustpilotScore", currentCompany.specs?.trustpilot_score || "4.7");
  setInputValue("repTrustpilotUrl", currentCompany.specs?.trustpilot_url || "");
  setInputValue("repUserRating", currentCompany.rating);
  setInputValue("repReviewsCount", currentCompany.reviews_count);
  setInputValue("repPros", (currentCompany.pros || []).join("\n"));
  setInputValue("repCons", (currentCompany.cons || []).join("\n"));

  // Set Support & Billing
  setInputValue("supEmail", currentCompany.support_email);
  setInputValue("supPhone", currentCompany.support_phone);
  setInputValue("supChatUrl", `${currentCompany.website}/support/live-chat`);

  // Set Social Links
  const social = currentCompany.social || {};
  setInputValue("socTwitter", social.twitter || "");
  setInputValue("socFacebook", social.facebook || "");
  setInputValue("socLinkedin", social.linkedin || "");
  setInputValue("socYoutube", social.youtube || "");

  // Load FAQs
  currentFAQs = JSON.parse(JSON.stringify(currentCompany.faqs || []));
  renderFAQs();

  // Update Overview Stats
  updateOverviewStats();
}

/**
 * Helpers for inputs
 */
function setInputValue(id, val) {
  const el = document.getElementById(id);
  if (el) el.value = val !== undefined && val !== null ? val : "";
}

function setCheckboxValue(id, val) {
  const el = document.getElementById(id);
  if (el) el.checked = Boolean(val);
}

function getCompanyDomain(comp) {
  if (comp && comp.website) {
    try {
      const u = new URL(comp.website);
      return u.hostname.replace(/^www\./, "");
    } catch (e) {}
  }
  if (!comp || !comp.slug) return "hostinger.com";
  let s = comp.slug.replace("-hosting", "").replace("-", "");
  return s + ".com";
}

function createBrandSvgAvatar(name, bgColor = "#2563eb") {
  const initial = (name || "H").charAt(0).toUpperCase();
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
    <defs>
      <linearGradient id="brandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${bgColor}"/>
        <stop offset="100%" stop-color="#0f172a"/>
      </linearGradient>
    </defs>
    <rect width="128" height="128" rx="24" fill="url(#brandGrad)"/>
    <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="64" font-weight="800">${initial}</text>
  </svg>`;
  return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}

function getCompanyLogoUrl(comp) {
  if (comp && comp.custom_logo) {
    return comp.custom_logo;
  }
  const domain = getCompanyDomain(comp);
  return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`;
}

function handleLogoError(imgEl) {
  if (!imgEl) return;
  const name = currentCompany?.company_name || "Host";
  const brandColors = {
    hostinger: "#673ab7",
    bluehost: "#1967d2",
    siteground: "#1e824c",
    "a2-hosting": "#e65100",
    ionos: "#001a70",
    godaddy: "#00838c",
    namecheap: "#de3723",
    kinsta: "#5333ed"
  };
  const color = brandColors[currentSlug] || "#2563eb";
  imgEl.onerror = null;
  imgEl.src = createBrandSvgAvatar(name, color);
}

function handleLogoFileUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const dataUrl = e.target.result;
    const logoImg = document.getElementById("logoPreviewImg");
    if (logoImg) logoImg.src = dataUrl;
    if (currentCompany) currentCompany.custom_logo = dataUrl;
    markChanged();
    showToast("Logo uploaded and updated successfully!");
  };
  reader.readAsDataURL(file);
}

/**
 * Render FAQ List
 */
function renderFAQs() {
  const container = document.getElementById("faqListContainer");
  if (!container) return;

  container.innerHTML = "";
  if (currentFAQs.length === 0) {
    container.innerHTML = `<p style="color: #64748b; font-size: 13px; font-style: italic;">No FAQs added yet. Click "+ Add New FAQ" to create one.</p>`;
    return;
  }

  currentFAQs.forEach((faq, index) => {
    const card = document.createElement("div");
    card.className = "faq-item-card";
    card.innerHTML = `
      <div class="faq-top-bar">
        <span class="faq-num">Question #${index + 1}</span>
        <button type="button" class="btn-remove-faq" onclick="removeFAQ(${index})" title="Remove FAQ">
          ✕
        </button>
      </div>
      <div class="form-group">
        <input type="text" class="form-control" value="${escapeHtml(faq.q)}" placeholder="e.g. Is ${currentCompany?.company_name} suitable for beginners?" oninput="updateFAQQuestion(${index}, this.value)" />
      </div>
      <div class="form-group">
        <textarea class="form-control" placeholder="Detailed answer..." oninput="updateFAQAnswer(${index}, this.value)">${escapeHtml(faq.a)}</textarea>
      </div>
    `;
    container.appendChild(card);
  });
}

function addFAQ() {
  currentFAQs.push({
    q: `What are the advantages of ${currentCompany?.company_name}?`,
    a: "Provides top-tier performance, 24/7 technical assistance, and money-back guarantee."
  });
  renderFAQs();
  markChanged();
}

function removeFAQ(index) {
  currentFAQs.splice(index, 1);
  renderFAQs();
  markChanged();
}

function updateFAQQuestion(index, val) {
  if (currentFAQs[index]) currentFAQs[index].q = val;
  markChanged();
}

function updateFAQAnswer(index, val) {
  if (currentFAQs[index]) currentFAQs[index].a = val;
  markChanged();
}

function escapeHtml(str) {
  return (str || "").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/**
 * Change Listener for Unsaved Indicator
 */
function initFormChangeListeners() {
  document.addEventListener("input", (e) => {
    if (e.target.matches(".form-control, .form-check-input, input[type='checkbox']")) {
      markChanged();
    }
  });
}

function markChanged() {
  hasUnsavedChanges = true;
  updateUnsavedStatus(true);
}

function updateUnsavedStatus(changed) {
  const bar = document.getElementById("floatingSaveBar");
  if (bar) {
    if (changed) bar.classList.add("show");
    else bar.classList.remove("show");
  }
}

/**
 * Save Changes
 */
function saveAllChanges() {
  if (!currentCompany) return;

  // Capture current form inputs
  currentCompany.company_name = document.getElementById("profileName").value;
  currentCompany.tagline = document.getElementById("profileTagline").value;
  currentCompany.founded = document.getElementById("profileFounded").value;
  currentCompany.headquarters = document.getElementById("profileHq").value;
  currentCompany.ceo_founder = document.getElementById("profileCeo").value;
  currentCompany.website = document.getElementById("profileWebsite").value;
  currentCompany.about = document.getElementById("profileAbout").value;

  currentCompany.pricing_details = {
    starting_price: document.getElementById("pricingStarting").value,
    renewal_price: document.getElementById("pricingRenewal").value,
    discount_badge: document.getElementById("pricingDiscountBadge").value,
    coupon_code: document.getElementById("pricingCoupon").value,
    money_back_days: parseInt(document.getElementById("pricingMoneyBack").value, 10) || 30
  };
  currentCompany.affiliate_url = document.getElementById("pricingAffiliate").value;

  currentCompany.services = {
    shared: document.getElementById("serviceShared").checked,
    wordpress: document.getElementById("serviceWordpress").checked,
    vps: document.getElementById("serviceVps").checked,
    cloud: document.getElementById("serviceCloud").checked,
    dedicated: document.getElementById("serviceDedicated").checked,
    reseller: document.getElementById("serviceReseller").checked
  };

  currentCompany.features = {
    free_ssl: document.getElementById("featSsl").checked,
    free_domain: document.getElementById("featDomain").checked,
    nvme_storage: document.getElementById("featNvme").checked,
    daily_backups: document.getElementById("featBackups").checked,
    cpanel: document.getElementById("featCpanel").checked,
    live_chat: document.getElementById("featChat").checked,
    ddos_protection: document.getElementById("featDdos").checked,
    free_migration: document.getElementById("featMigration").checked,
    staging_tool: document.getElementById("featStaging").checked
  };

  currentCompany.datacenters = document.getElementById("techDatacenters").value;
  currentCompany.specs = currentCompany.specs || {};
  currentCompany.specs.uptime = document.getElementById("techUptime").value;
  currentCompany.specs.web_server = document.getElementById("techWebServer").value;
  currentCompany.specs.trustpilot_score = document.getElementById("repTrustpilotScore").value;
  currentCompany.specs.trustpilot_url = document.getElementById("repTrustpilotUrl").value;

  currentCompany.pros = document.getElementById("repPros").value.split("\n").filter(Boolean);
  currentCompany.cons = document.getElementById("repCons").value.split("\n").filter(Boolean);
  currentCompany.faqs = currentFAQs;

  // Persist into memory and local state
  HOSTING_COMPANIES_DATA[currentSlug] = JSON.parse(JSON.stringify(currentCompany));
  hasUnsavedChanges = false;
  updateUnsavedStatus(false);

  // Update header text in case name changed
  document.getElementById("companyNameHeader").textContent = currentCompany.company_name;

  showToast("Listing details updated and saved successfully!");
  updateOverviewStats();
}

function discardChanges() {
  if (confirm("Discard all changes and restore original details?")) {
    loadCompany(currentSlug);
    showToast("Changes discarded.");
  }
}

/**
 * Toast Notification
 */
function showToast(msg) {
  const toast = document.getElementById("toastNotification");
  const msgEl = document.getElementById("toastMessage");
  if (!toast || !msgEl) return;

  msgEl.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3500);
}

/**
 * Overview Stats Generator
 */
function updateOverviewStats() {
  if (!currentCompany) return;

  const views = Math.floor(35000 + (currentCompany.company_name.length * 1420));
  const clicks = Math.floor(views * 0.078);
  const conv = "7.8%";

  document.getElementById("statViews").textContent = views.toLocaleString();
  document.getElementById("statClicks").textContent = clicks.toLocaleString();
  document.getElementById("statCtr").textContent = conv;
  document.getElementById("statRating").textContent = `${currentCompany.rating} / 5.0`;
}

/**
 * Live Preview Modal
 */
function openLivePreview() {
  const modal = document.getElementById("previewModal");
  if (!modal || !currentCompany) return;

  const logoUrl = getCompanyLogoUrl(currentCompany);
  const price = document.getElementById("pricingStarting")?.value || currentCompany.price;
  const discount = document.getElementById("pricingDiscountBadge")?.value || "Special Offer";
  const tagline = document.getElementById("profileTagline")?.value || currentCompany.tagline;
  const rating = currentCompany.rating || "4.6";

  const prevContent = document.getElementById("previewModalContent");
  prevContent.innerHTML = `
    <div class="preview-card">
      <div class="prev-hero">
        <div class="prev-brand">
          <img src="${logoUrl}" onerror="this.src='https://placehold.co/80x80?text=${encodeURIComponent(currentCompany.company_name)}'" class="prev-logo" alt="${currentCompany.company_name} logo">
          <div>
            <h2>${escapeHtml(currentCompany.company_name)}</h2>
            <p>${escapeHtml(tagline)}</p>
          </div>
        </div>
        <div class="prev-rating">
          <div class="prev-score">${rating} / 5.0</div>
          <div style="font-size: 11px; color: #64748b;">${currentCompany.reviews_count || '1,200 reviews'}</div>
        </div>
      </div>

      <div class="prev-price-box">
        <div>
          <span style="display:inline-block; background: #15803d; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; margin-bottom: 4px;">
            ${escapeHtml(discount)}
          </span>
          <div class="prev-price-title">Starting at only</div>
          <div class="prev-price-val">${escapeHtml(price)}</div>
        </div>
        <a href="${escapeHtml(currentCompany.affiliate_url || '#')}" target="_blank" class="btn btn-primary" style="padding: 10px 22px; font-weight: 700;">
          Visit Official Site
        </a>
      </div>

      <div style="margin-bottom: 20px;">
        <h4 style="font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 8px;">Key Provider Highlights</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          ${(currentCompany.pros || []).slice(0, 3).map(p => `
            <span style="background: #eff6ff; color: #1d4ed8; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; border: 1px solid #bfdbfe;">
              ${escapeHtml(p)}
            </span>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  modal.classList.add("open");
}

function closeLivePreview() {
  const modal = document.getElementById("previewModal");
  if (modal) modal.classList.remove("open");
}
