# DoD Cybersecurity Cert Requirements — Reference

A public reference compilation of DoD cybersecurity workforce qualification material. Compiled by Jeff Krueger. **Unaffiliated with any firm, agency, or contracting office. Not legal advice.**

This repo preserves two things that are useful for navigating the DoD cyber workforce qualification landscape but are awkward to find in one place from official sources:

1. A **one-page view of the current DoD 8140 certification-path qualification matrix** — all work roles vs. all approved certs on a single landscape sheet. Easier to scan than the 10-tab official workbook when you're answering questions like *"what roles am I qualified for with my current certs?"* or *"which cert gives me the most coverage?"*.
2. A **reference copy of the retired DoD 8570 Approved Baseline Certifications list** — the list that's still named in many active federal contracts, but which DoD removed from public.cyber.mil during the 8140 transition.

## Downloads

| File | What it is |
|------|-----------|
| [**`8140/8140-cert-requirements.xlsx`**](8140/8140-cert-requirements.xlsx) | Current 8140 certification-path matrix — all 45 work roles × all 60 approved certs on one landscape sheet, grouped by vendor. Compiled from the DoD 8140 Foundational Qualification Matrix V2.1 (effective 19 Sep 2025). Summary rows show which certs cover the most roles. |
| [**`8140/8140-cert-requirements.pdf`**](8140/8140-cert-requirements.pdf) | Same content, PDF. Single 11×17 landscape page with matrix + explanatory narrative. |
| [**`8570/8570-baseline-reference.pdf`**](8570/8570-baseline-reference.pdf) | The retired DoD 8570.01-M Approved Baseline Certifications list, reconstructed from the last publicly-archived version of the cyber.mil page (snapshot 30 Jan 2024) before DoD removed it. Two pages. |

## Why the 8570 list is still preserved here

DoDM 8140.03 replaced DoD 8570.01-M as DoD *policy* in February 2023, and at some point in early 2024 DoD removed the 8570 approved-baseline certifications page from public.cyber.mil.

But contracts written against 8570 by name did not automatically update. As of the most recent revision (10 Nov 2025), **DFARS 252.239-7001** — the contract clause that governs DoD contractor cyber workforce qualification — still references DoD 8570.01-M by name, not 8140. And many active contracts have copy-pasted the 8570 cert list directly into their statements of work, independent of the DFARS clause.

A contractor, Contracting Officer, COR, or compliance reviewer managing such a contract still needs to be able to cite the authoritative 8570 baseline list. This repo is that reference.

See [`far-context/far-dfars-cert-clauses.md`](far-context/far-dfars-cert-clauses.md) for the detailed DFARS citation and framing of the DoD-policy-vs-contract-language gap. **Not legal advice.**

## Why the 8140 matrix is presented this way

DoD publishes the V2.1 qualification matrix as a 10-tab Excel workbook. The authoritative form is comprehensive but inverted for a common planning question: *"What roles am I qualified for with my current certs? What cert should I pursue next to broaden my coverage?"*

The official matrix is organized by role (for each role, here are your cert options). This repo's matrix is organized by cert-across-roles on a single page — the inverse pivot. It's derived from the DoD source and carries no different information; it's just easier to scan when the question is about cert breadth or planning.

Source data lives in [`8140/sources/`](8140/sources/). The matrix shown here is built programmatically from that source via [`scripts/build_refreshed_xlsx.py`](scripts/build_refreshed_xlsx.py). When DoD publishes a V2.2, re-running the build regenerates the output.

## Scope

This matrix covers the **Personnel Certification** qualification path only. DoD 8140 actually offers four foundational qualification paths — Education, DoD/Military Training, Commercial Training, and Personnel Certification — plus an Experience alternative for eligible personnel. In practice the certification path is the most common route for contractors and for anyone without an applicable degree or military schooling; the other paths are shown in the official DoD matrix linked below.

Out of scope for this repo:
- Education, DoD Training, Commercial Training, and Experience paths (see the official DoD matrix)
- Legal opinion on DFARS 252.239-7001 or contract clauses (this is not legal advice)
- Cert vendor cost, exam difficulty, or training path recommendations

## Canonical DoD sources (for currency)

- **Policy:** [DoDM 8140.03 "Cyberspace Workforce Qualification and Management Program"](https://dodcio.defense.gov/Portals/0/Documents/Library/DoDM-8140-03.pdf) (15 Feb 2023)
- **Current qualification matrix:** [DoD 8140 Qualification Matrices on cyber.mil](https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices) (V2.1, effective 19 Sep 2025 at time of this repo's most recent refresh)
- **DoD Cyber Workforce Framework (DCWF):** [cyber.mil/dod-cyber-workforce-framework](https://www.cyber.mil/dod-workforce-innovation-directorate/dod-cyber-workforce-framework)
- **Cyber 101 (40-hour course satisfying all Cyber Enabler work-role qualification requirements):** [cyber.mil/training/cyber-101](https://www.cyber.mil/training/cyber-101)

If DoD publishes a newer matrix than what this repo reflects, prefer the DoD source. This repo is a derived convenience view, not the authoritative record.

## Corrections welcome

Spot an error — a mismatched cert, an outdated footnote, a broken link, a missing work role? **Please [open an issue](../../issues/new).** Pull requests with factual corrections and citations are also welcome.

Reporting a correction via Issues creates a public record of the fix, which over time is more valuable for readers than a silently-updated document.

## Licensing

- **Scripts** (`scripts/`, build pipeline, renderers): MIT License ([`LICENSE-CODE`](LICENSE-CODE))
- **Documents** (xlsx, PDFs, markdown reference material): Creative Commons Attribution 4.0 International ([`LICENSE-DOCS`](LICENSE-DOCS))

Both licenses permit reuse with attribution.

## Version

This repo uses date-tagged releases (e.g., `v2026.04`) marking each substantive refresh. See the [Releases](../../releases) page for version history and attached artifact downloads.

---

Compiled by Jeff Krueger. Unaffiliated with any firm, agency, or contracting office. Not legal advice.
