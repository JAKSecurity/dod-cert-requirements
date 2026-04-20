# 8140 Certification Analysis — Locked Visual Specification (v1.0)

**Status:** Approved 2026-04-19 after Jeff review of iterations v1–v8.
**Canonical output:** [`8140/8140-cert-requirements.xlsx`](../8140/8140-cert-requirements.xlsx)
**Builder:** [`scripts/build_refreshed_xlsx.py`](../scripts/build_refreshed_xlsx.py)
**Spec data:** [`scripts/visual_spec.py`](../scripts/visual_spec.py)

The Python builder is the authoritative spec. This document summarizes design decisions for future readers / refreshers.

## Sheets

**One consolidated sheet: `Certification Analysis`.** Matrix occupies the top;
explanation block sits directly below the pending-review footnote on the same
sheet so the PDF export renders as a single 11x17 landscape page.

Earlier iterations had separate `Explanation` and `Certification Requirements`
sheets — both removed after Jeff's v1.1 consolidation direction:
- `Explanation` content embedded below the matrix (see EXPLANATION_LINES in the builder).
- `Certification Requirements` (per-role list view) dropped entirely — the pivot view already encodes the same data more compactly.

## Certification Analysis layout

### Columns

- **Column A (width 47):** work role labels, `(WRC) Name` format.
- **Columns B–BI (width 3.5 each):** one column per certification, grouped by vendor, sorted within vendor by ascending average proficiency level.
- **Column BJ (width 47):** right-side "Work Role" echo, duplicating column A for readability on wide rows.

### Rows

- **Row 1 (h=17):** merged banner "DoD 8140.03 Foundational Qualification: Personal Certification" across columns A:BJ, dark blue banner fill.
- **Row 2 (h=17):** vendor group headers. Each vendor's cert columns are merged and fill-colored per `VENDOR_PALETTE[v]["base"]`. Per-vendor font size override: RCCE 7pt, CertNexus 9pt, default 11pt.
- **Row 3 (h=40):** cert acronym headers, rotated 90°. Each cert has its own color walking from light (easy end) to dark (hard end) within its vendor's hue band.
- **Rows 4 to last-data-row:** one row per work role (sorted by WRC numerically, ascending). Alternating rows get light-gray banding on the label columns.
- **Repeat-header row:** combined proficiency legend (column A) + cert acronym headers repeat (cols B–BI) + "darker shades cover more work roles" note (echo column BJ).
- **Totals row:** column A label "Total Positions Covered"; cert cols hold `=COUNT(range)` formulas; heat-map fill walks light-pink → dark-red by magnitude; echo col repeats label.
- **Points row:** column A label `Total "Points" (proficiency levels × positions)`; cert cols hold `=SUM(range)` formulas; heat-map fill walks light-green → dark-green by magnitude.
- **Footnote row (directly below points):** "Note: The following work roles exist in DoD 8140 V2.1 but have no published certification options (pending DoD review): (462) Control Systems Security Specialist, (731) Cyber Legal Advisor, (901) Executive Cyber Leader." Italic, merged A:BJ, wrap.

### Framing

- **Per-vendor thin outer box** from row 2 (vendor header) through repeat-header row, spanning each vendor's cert columns.
- **Outer thin box around the whole structured matrix** from A1 to BJ <points row>. The footnote sits outside this frame.

## Color model

Each cert column has **one color**, applied to both its header and every data cell in that column. The cell VALUE (1 / 2 / 3) communicates the proficiency level — color does not encode level.

- Cell fill lightness walks 0.78 → 0.20 across a vendor's certs (easier cert = lighter, harder = darker).
- Header fill lightness walks 0.42 → 0.14 (headers always darker than their column's cells).
- Text color auto-picks: white on fills with lightness < 0.55, black otherwise.
- Vendor hue bands are defined in `VENDOR_HUE_SPEC` (CompTIA grayscale, EC-Council blue → indigo, GIAC pink → purple, etc.).

## Sorting rules

- **Roles:** strict numerical ascending by WRC. Pending-review roles (462, 731, 901) omitted entirely. No CY 101 separator (was considered, rejected for the numerical layout).
- **Certs within vendor:** ascending by average proficiency level across all roles that require them (ties broken by cert name lowercase). Entry-level certs land left, advanced right.
- **Vendors (left-to-right):** explicit list in `VENDOR_ORDER`. RCCE sits between CompTIA and EC-Council per Jeff's v7 placement.

## Special treatments

- **(451) System Admin row** gets a red fill (`FFFF0000`) with white bold text — flags elevated criticality ("req'd for admin access").
- **"Compiled by Jeff Krueger"** appears only on the Explanation tab. No email, no URL anywhere else per the authorship/exposure decision.

## Known name translations

| DoD V2.1 source | Output short form |
|-----------------|-------------------|
| Network+ | Net+ |
| Security+ | Sec+ |
| PenTest+ | PenTest |
| SecurityX / CASP+ | SecX |
| CCNP Security | CCNP-S |
| CCNP Enterprise | CCNP-E |
| CGRC/CAP | CGRC |
| CISSP-ISSAP / ISSEP / ISSMP | ISSAP / ISSEP / ISSMP |
| DAWIA LCL Foundational / Advanced | LCL-F / LCL-A |
| DAWIA PM Practioner / Advanced | PM-P / PM-A |
| RCCE Level 1 | RCCE-1 |

## Refresh cadence

Re-run end-to-end when DoD publishes a matrix update:

```bash
.venv/Scripts/python -m scripts.extract_official_matrix
.venv/Scripts/python -m scripts.normalize_jan2025_xlsx    # only if comparing to Jan 2025 again
.venv/Scripts/python -m scripts.diff_matrices             # informational CHANGELOG only
.venv/Scripts/python -m scripts.render_changelog
.venv/Scripts/python -m scripts.build_refreshed_xlsx
.venv/Scripts/python -m scripts.render_8140_pdf
```

Source xlsx manually downloaded into `8140/sources/` (Salesforce-backed page; no stable API). See [refresh-notes-2026-04.md](refresh-notes-2026-04.md) for the recon story.
