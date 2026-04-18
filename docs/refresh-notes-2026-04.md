# 8140 Refresh Notes — 2026-04

## Source location change

**Planned URL (from spec):** `https://public.cyber.mil/wid/cwmp/dod-cyber-workforce-qualifications-matrices-management/`

**Observed behavior:** The planned URL redirects via HTTP 302 to `https://www.cyber.mil/wid/cwmp/dod-cyber-workforce-qualifications-matrices-management/`, which then redirects into a SAML authentication flow at `www.cyber.mil/vforcesite/saml/authn-request.jsp` (`hacc.experience.crmforce.mil` identity provider — Salesforce Communities). The old deep link no longer resolves to public content.

**New public URL (found via search):** `https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices`

HTTP status on the new URL: 200 OK. Content-Type: `text/html; charset=utf-8`. Size: ~135 KB.

## Format — major change

The DoD Cyber Exchange has been migrated onto Salesforce infrastructure. Evidence:

- Response headers and HTML reference Salesforce Lightning Design System (`assets/styles/salesforce-lightning-design-system.min.css`), Salesforce Experience Cloud styles (`dxp-site-spacing-styling-hooks.min.css`, `dxp-slds-extensions.min.css`), and Salesforce CMS delivery paths (`sfsites/c/cms/delivery/media/...`).
- The redirect chain from the old URL points at `hacc.experience.crmforce.mil` — a Salesforce Experience Cloud identity provider.
- The served HTML is an SPA shell; page content is loaded client-side via JavaScript. Raw curl returns the app shell with no inline content tables or artifact links beyond the shell's preloaded media assets.
- `grep` for keywords in the raw HTML returns only 7 occurrences of "Qualification", 3 of "Download", 1 of "Matrix" — confirming the actual matrix content is not in the server-rendered HTML.
- The former download CDN `dl.dod.cyber.mil` does not resolve (DNS lookup fails). Artifact URLs previously hosted there (e.g., `dl.dod.cyber.mil/wp-content/uploads/8140/pdf/...`) are no longer reachable.

## Content version — material change since Jan 2025

Per DoD 8140 Change Management Bulletin referenced in search results: **DoD 8140 Foundational Qualification Matrix Version 2.1, effective 19 September 2025** has been distributed to the DoD cyber workforce.

The Jan 2025 spreadsheet in our hands predates this version 2.1. A material content delta is expected. Jeff already anticipated this ("there was some late 2025 edits to source material") — the exact source of that suspicion is confirmed.

## Extraction approach — BLOCKED pending decision

The plan's assumed extraction approach (fetch HTML, parse inline tables with BeautifulSoup) does not work against the new Salesforce SPA. Options Jeff needs to choose from:

**(A) Headless browser automation.** Use Playwright or similar to render the Salesforce page, wait for content to load, then extract the rendered DOM. Feasible but brittle: Salesforce SPAs can have anti-automation signals, dynamic loading patterns that are fragile to version changes, and we'd be scraping a rendered view of what is authoritatively a structured dataset somewhere upstream.

**(B) Reverse-engineer the Salesforce CMS REST endpoints.** The SPA fetches content from Salesforce's Content Delivery APIs. Inspect network traffic (DevTools → Network) while the page loads, identify the JSON/GraphQL endpoints that deliver the matrix data, and hit those directly. Cleaner data once reverse-engineered, and more stable than DOM scraping, but higher initial investigation cost and may require auth tokens/cookies.

**(C) Manual download from the new page.** Once a human loads the page in a browser, the page may offer an authoritative xlsx/PDF download. Jeff downloads manually, saves to the repo's `8140/sources/` folder, and we extract from the downloaded artifact. Fastest path if the download exists and is authoritative. Doesn't scale for automated future refreshes but is a reasonable v1 compromise.

**(D) DoD CWMP direct contact.** Reach out to DoD Cyber Workforce Management Program (`cyber.mil/knowledge-base/e-mail-cyber-workforce-management-program/`) and request the authoritative data file. Works for one-time refresh but not a scalable pipeline.

**(E) Ship Jan 2025 content as-is with a visible "source migrated, refresh pending" banner.** Defers the refresh entirely. Acceptable for a repo that's initially private and getting polished behind the scenes; not acceptable for public publication.

## Sibling URLs worth noting

Search also surfaced these — all appear to also be Salesforce-backed and require the same resolution approach:

- `https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices` — the qualifications matrices landing
- `https://www.cyber.mil/dod-workforce-innovation-directorate/dod-cyber-workforce-framework` — the DCWF framework overview
- `https://public.cyber.mil/wid/dod8140/` — 8140 home (redirect expected)
- `https://public.cyber.mil/wid/dod8140/documents-library/` — the old-style documents library (also redirects)

## Recommendation for Jeff's review

Recommend **(C) — manual download** for v1 if the new page offers an authoritative xlsx/PDF download behind a visible button (check once logged in to a browser session). If no such download exists, fall back to **(A) — headless browser automation** using Playwright; the automation cost is a one-time investment that benefits the v2 "automated refresh pipeline" we've already queued for future work.

Against this recommendation: **do not** pursue (E) silently — it contradicts the design's stated goal of shipping current content, and the credibility risk of publishing a known-stale matrix as "reference" is exactly the failure mode we outlined in the design risks.

## What has been completed under the current Phase 1 scope

- Verified old URL is unreachable (redirects into SAML).
- Verified new URL is reachable (HTTP 200) but Salesforce SPA.
- Confirmed version 2.1 (Sept 2025) is the current authoritative content.
- Captured page snapshot to `data/new-source-page.html` locally (gitignored; not pushed).

## What is blocked

- Task 2.3 (`scripts/extract_official_matrix.py`) — cannot be implemented until Jeff selects an extraction path above.

## What remains safe to proceed on

- Tasks 2.1, 2.2, 2.4, 2.5 — all format-agnostic. They operate on the canonical JSON representation and work on the Jan 2025 xlsx input regardless of how we later obtain the "new" side for comparison.

## Unblock — 2026-04-18 update

Jeff successfully downloaded the V2.1 xlsx from the new www.cyber.mil page on a second attempt (first attempt failed due to what looked like a transient Salesforce hiccup). File: `8140/sources/dod8140-matrix-v2.1-20250919.xlsx` (277 KB, 10 sheets). A V2.0 companion file is also preserved at `8140/sources/unclass-dod8140qualmatrix.xlsx`.

**Format for extraction:** the V2.1 `Certification Repository` sheet is a flat table — columns `WRC | Work Role Title | Element | Acronym | Proficiency | Vendor`, 428 rows covering all certification options across every V2.1 work role. This is materially easier to parse than the old HTML tables — no scraping, no DOM rendering, just openpyxl on a column-stable sheet.

## Locked decisions (2026-04-18)

**Source of truth:** V2.1 `Certification Repository` sheet. Other sheets (DoD Training Repository, Matrix Tool - Approved, Reference) are context, not extraction sources.

**Scope: certification path only.** V2.1 formalizes four foundational qualification paths (Education / DoD Military Training / Commercial Training / Personnel Certification) plus an Experience alternative. This repo stays bounded to the **certification path** — in practice the route 99% of people take when they don't already have the degree, and the original focus of Jeff's spreadsheet.

**Role scope: all V2.1 roles.** Every work role that appears in the V2.1 Certification Repository (spanning Cyber Effects, Intel, IT, Cybersecurity, Cyber Enablers). Expands beyond the ~35 Jan 2025 scope. Source data is cheap, matrix scales naturally, avoids the "why isn't role X here?" question.

**Refresh strategy: build a fresh xlsx, not patch Jan 2025.** The V2.1 structure differs from Jan 2025 enough that cell-by-cell patching produces a misaligned hybrid. Instead, we generate a clean xlsx from V2.1 data using Jan 2025 as the **visual template** (same tab structure — Explanation, per-role summary, pivot view — same column/row layout, same styling). Jan 2025 xlsx remains input only for the informational CHANGELOG diff.

**DoD Training Repository: skip.** Out of scope for this repo's audience.

**Explanation tab: Jeff rewrites.** V2.1 paradigm (four qualification paths, new CPD requirements, expanded role universe) calls for a voice Jeff owns rather than a mechanical regeneration.

## Implication for the Phase 2/3 pipeline

The plan's original `apply_changelog.py` (cell-patch the Jan 2025 xlsx) becomes obsolete. Replaced by `build_refreshed_xlsx.py` (generate fresh xlsx from V2.1 data + visual template). The extract/normalize/diff/changelog chain survives — diff produces an **informational CHANGELOG** showing "what's changed since your Jan 2025 view," useful for readers who want provenance but not driving the build step.
