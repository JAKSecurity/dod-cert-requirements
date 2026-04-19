"""Build the refreshed 8140 xlsx from V2.1 source data.

The Jan 2025 xlsx is Jeff's **visual template** — its tab layout and the
style of the pivot view we recreate. It is NOT patched; we build a fresh
workbook from V2.1's Certification Repository.

Output structure:
  - 'Explanation'              placeholder narrative (Jeff rewrites)
  - 'Certification Requirements' per-role cert list at each proficiency level
  - 'Certification Analysis'   inverted pivot: roles x certs, with 1/2/3 cells
                               + Total Positions / Total Points summary rows
"""
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

SHEET_NAME = "Certification Repository"
HEADER_ROW = 2
COL_WRC = 0
COL_ROLE_NAME = 1
COL_ELEMENT = 2
COL_ACRONYM = 3
COL_PROFICIENCY = 4
COL_VENDOR = 5

PROFICIENCY_LEVEL = {"basic": 1, "intermediate": 2, "advanced": 3}
LEVEL_LABEL = {1: "Basic", 2: "Intermediate", 3: "Advanced"}

# Work roles in V2.1 role universe but with no published cert options.
# Surfaced as a footnote/note in the output xlsx rather than matrix rows.
PENDING_REVIEW_ROLES = {
    "462": "Control Systems Security Specialist",
    "731": "Cyber Legal Advisor",
    "901": "Executive Cyber Leader",
}


# ----------------------------------------------------------------------------
# Data extraction helpers
# ----------------------------------------------------------------------------

def read_v21_certification_rows(xlsx_path: str | Path) -> list[dict]:
    """Read the V2.1 Certification Repository sheet into a list of dicts."""
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb[SHEET_NAME]
    rows: list[dict] = []
    for row in ws.iter_rows(min_row=HEADER_ROW + 1, values_only=True):
        if row[COL_WRC] is None or row[COL_ACRONYM] is None:
            continue
        proficiency = (
            str(row[COL_PROFICIENCY]).strip().lower()
            if row[COL_PROFICIENCY] else ""
        )
        if proficiency not in PROFICIENCY_LEVEL:
            continue
        rows.append({
            "wrc": str(row[COL_WRC]).strip(),
            "work_role_name": str(row[COL_ROLE_NAME]).strip() if row[COL_ROLE_NAME] else "",
            "element": str(row[COL_ELEMENT]).strip() if row[COL_ELEMENT] else "",
            "acronym": str(row[COL_ACRONYM]).strip(),
            "proficiency": proficiency,
            "vendor": str(row[COL_VENDOR]).strip() if row[COL_VENDOR] else "",
        })
    wb.close()
    return rows


def build_role_catalog(rows: list[dict]) -> dict[str, dict]:
    """role_code -> {name, element}, deduped."""
    catalog: dict[str, dict] = {}
    for r in rows:
        code = r["wrc"]
        if code not in catalog:
            catalog[code] = {"name": r["work_role_name"], "element": r["element"]}
    return catalog


def build_vendor_cert_map(rows: list[dict]) -> dict[str, list[str]]:
    """vendor -> sorted list of cert acronyms."""
    vendor_sets: dict[str, set] = defaultdict(set)
    for r in rows:
        vendor_sets[r["vendor"]].add(r["acronym"])
    return {v: sorted(certs) for v, certs in vendor_sets.items()}


def build_pivot_cells(rows: list[dict]) -> dict[tuple[str, str], int]:
    """(role_code, cert_acronym) -> highest proficiency_level as int 1/2/3."""
    cells: dict[tuple[str, str], int] = {}
    for r in rows:
        key = (r["wrc"], r["acronym"])
        level = PROFICIENCY_LEVEL[r["proficiency"]]
        if key not in cells or cells[key] < level:
            cells[key] = level
    return cells


def build_per_role_by_level(rows: list[dict]) -> dict[str, dict[str, list[str]]]:
    """role_code -> {basic: [certs], intermediate: [certs], advanced: [certs]}"""
    result: dict[str, dict[str, set]] = defaultdict(
        lambda: {"basic": set(), "intermediate": set(), "advanced": set()}
    )
    for r in rows:
        result[r["wrc"]][r["proficiency"]].add(r["acronym"])
    return {
        code: {level: sorted(certs) for level, certs in by_level.items()}
        for code, by_level in result.items()
    }


# ----------------------------------------------------------------------------
# Sheet writers
# ----------------------------------------------------------------------------

HEADER_FILL = PatternFill("solid", start_color="FF1F4E79", end_color="FF1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFFFF")
VENDOR_GROUP_FILL = PatternFill("solid", start_color="FFDCE6F1", end_color="FFDCE6F1")
VENDOR_GROUP_FONT = Font(bold=True)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_WRAP = Alignment(horizontal="left", vertical="center", wrap_text=True)


def write_explanation_sheet(wb: Workbook) -> None:
    ws = wb.create_sheet("Explanation")
    lines = [
        "DoD 8140 Cybersecurity Workforce Qualification — Personal Certification Path",
        "",
        "[PLACEHOLDER — narrative to be rewritten by Jeff]",
        "",
        "This workbook presents the certification-path options from DoDM 8140.03, "
        "sourced from the DoD 8140 Foundational Qualification Matrix V2.1 "
        "(effective 2025-09-19). Other qualification paths in the DoD 8140 "
        "paradigm (education, DoD training, commercial training, experience) "
        "are intentionally out of scope for this reference.",
        "",
        "Tabs:",
        "  - 'Certification Requirements' — per-role summary: for each work role, "
        "the approved certification options at Basic / Intermediate / Advanced levels.",
        "  - 'Certification Analysis' — inverted pivot view: all certs across all "
        "work roles on one page. Cells contain the highest proficiency level "
        "(1 = Basic, 2 = Intermediate, 3 = Advanced) at which that cert "
        "qualifies a person for that role. Summary rows at the bottom.",
        "",
        "Work roles with no certification data (pending DoD review):",
    ]
    for code, name in PENDING_REVIEW_ROLES.items():
        lines.append(f"  - ({code}) {name}")
    lines.append("")
    lines.append(
        "These roles exist in the DoD 8140 V2.1 role universe but have no published "
        "certification options. Omitted from the matrix; will be added when DoD publishes data."
    )
    lines.append("")
    lines.append("Authoritative source: DoD 8140 Foundational Qualification Matrix V2.1")
    lines.append("URL at time of refresh: www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices")
    lines.append("")
    lines.append("Compiled by Jeff Krueger.")
    for line in lines:
        ws.append([line])
    ws.column_dimensions["A"].width = 120


def write_summary_sheet(wb: Workbook, role_catalog: dict, per_role: dict) -> None:
    ws = wb.create_sheet("Certification Requirements")

    # Row 1: banner
    ws["A1"] = "Certification Path Qualification Options (DoD 8140.03)"
    ws["A1"].font = Font(bold=True, size=12)

    # Row 2: headers
    headers = ["Work Role", "Basic", "Intermediate", "Advanced"]
    for col_idx, h in enumerate(headers, start=1):
        cell = ws.cell(row=2, column=col_idx, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER

    # Data rows sorted by WRC numerically
    row_num = 3
    for code in sorted(role_catalog.keys(), key=lambda c: int(c)):
        name = role_catalog[code]["name"]
        ws.cell(row=row_num, column=1, value=f"({code}) {name}").alignment = LEFT_WRAP
        levels = per_role.get(code, {"basic": [], "intermediate": [], "advanced": []})
        ws.cell(row=row_num, column=2, value=", ".join(levels["basic"]) or None).alignment = LEFT_WRAP
        ws.cell(row=row_num, column=3, value=", ".join(levels["intermediate"]) or None).alignment = LEFT_WRAP
        ws.cell(row=row_num, column=4, value=", ".join(levels["advanced"]) or None).alignment = LEFT_WRAP
        row_num += 1

    # Column widths
    ws.column_dimensions["A"].width = 50
    for col in ("B", "C", "D"):
        ws.column_dimensions[col].width = 40

    # Footnote
    ws.cell(
        row=row_num + 1, column=1,
        value=(
            "Note: The following work roles exist in DoD 8140 V2.1 but have no "
            "published cert options (pending DoD review): "
            + ", ".join(f"({c}) {n}" for c, n in PENDING_REVIEW_ROLES.items())
            + "."
        ),
    ).font = Font(italic=True)

    ws.freeze_panes = "A3"


def write_pivot_sheet(
    wb: Workbook,
    role_catalog: dict,
    vendor_cert_map: dict,
    pivot_cells: dict,
) -> None:
    ws = wb.create_sheet("Certification Analysis")

    # Ordered vendors (alphabetical for v1; can revisit later)
    vendors = sorted(vendor_cert_map.keys())
    # Ordered list of (cert_acronym, vendor) — cert columns in output
    cert_columns: list[tuple[str, str]] = []
    for v in vendors:
        for cert in vendor_cert_map[v]:
            cert_columns.append((cert, v))

    first_cert_col = 2  # column B onwards

    # Row 1: banner
    ws["A1"] = "DoD 8140 Certification Analysis — Inverted View"
    ws["A1"].font = Font(bold=True, size=12)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=first_cert_col + len(cert_columns) - 1)

    # Row 2: vendor group header row (merge across each vendor's cert columns)
    col_cursor = first_cert_col
    for v in vendors:
        span = len(vendor_cert_map[v])
        cell = ws.cell(row=2, column=col_cursor, value=v)
        cell.alignment = CENTER
        cell.font = VENDOR_GROUP_FONT
        cell.fill = VENDOR_GROUP_FILL
        if span > 1:
            ws.merge_cells(
                start_row=2, start_column=col_cursor,
                end_row=2, end_column=col_cursor + span - 1,
            )
        col_cursor += span

    # Row 3: cert-acronym column headers
    ws.cell(row=3, column=1, value="Work Role").font = HEADER_FONT
    ws.cell(row=3, column=1).fill = HEADER_FILL
    ws.cell(row=3, column=1).alignment = CENTER
    for i, (cert, _vendor) in enumerate(cert_columns):
        cell = ws.cell(row=3, column=first_cert_col + i, value=cert)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER

    # Row 4+: one row per work role
    role_codes_sorted = sorted(role_catalog.keys(), key=lambda c: int(c))
    row_num = 4
    for code in role_codes_sorted:
        name = role_catalog[code]["name"]
        ws.cell(row=row_num, column=1, value=f"({code}) {name}").alignment = LEFT_WRAP
        for i, (cert, _vendor) in enumerate(cert_columns):
            level = pivot_cells.get((code, cert))
            if level is not None:
                ws.cell(row=row_num, column=first_cert_col + i, value=level).alignment = CENTER
        row_num += 1

    # Summary rows
    legend_row = row_num + 1
    ws.cell(row=legend_row, column=1, value="Proficiency: 1 = Basic, 2 = Intermediate, 3 = Advanced").font = Font(italic=True)

    totals_row = legend_row + 2
    points_row = totals_row + 1
    ws.cell(row=totals_row, column=1, value="Total Positions Covered").font = Font(bold=True)
    ws.cell(row=points_row, column=1, value="Total Points (levels x positions)").font = Font(bold=True)

    # Compute totals per cert column
    for i, (cert, _vendor) in enumerate(cert_columns):
        # Count how many roles reference this cert (any level)
        positions = sum(1 for code in role_codes_sorted if (code, cert) in pivot_cells)
        points = sum(
            pivot_cells[(code, cert)]
            for code in role_codes_sorted
            if (code, cert) in pivot_cells
        )
        ws.cell(row=totals_row, column=first_cert_col + i, value=positions).alignment = CENTER
        ws.cell(row=points_row, column=first_cert_col + i, value=points).alignment = CENTER

    # Footnote
    footer_row = points_row + 2
    ws.cell(
        row=footer_row, column=1,
        value=(
            "Note: The following work roles exist in DoD 8140 V2.1 but have no "
            "published cert options (pending DoD review): "
            + ", ".join(f"({c}) {n}" for c, n in PENDING_REVIEW_ROLES.items())
            + "."
        ),
    ).font = Font(italic=True)

    # Column widths and freeze panes
    ws.column_dimensions["A"].width = 45
    for i in range(len(cert_columns)):
        col_letter = get_column_letter(first_cert_col + i)
        ws.column_dimensions[col_letter].width = 8
    ws.row_dimensions[3].height = 80  # cert acronym headers need height for vertical stacking
    ws.freeze_panes = ws.cell(row=4, column=2).coordinate


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------

def build(v21_xlsx_path: str | Path, output_path: str | Path) -> None:
    rows = read_v21_certification_rows(v21_xlsx_path)
    role_catalog = build_role_catalog(rows)
    vendor_cert_map = build_vendor_cert_map(rows)
    pivot_cells = build_pivot_cells(rows)
    per_role = build_per_role_by_level(rows)

    wb = Workbook()
    wb.remove(wb.active)
    write_explanation_sheet(wb)
    write_summary_sheet(wb, role_catalog, per_role)
    write_pivot_sheet(wb, role_catalog, vendor_cert_map, pivot_cells)
    wb.properties.creator = "Jeff Krueger"
    wb.properties.lastModifiedBy = "Jeff Krueger"
    wb.properties.title = "DoD 8140.03 Cert Path Reference"
    wb.properties.description = (
        "DoD 8140.03 cybersecurity workforce qualification — certification-path "
        "reference. Compiled by Jeff Krueger. Unaffiliated with any firm or agency."
    )
    wb.save(output_path)


if __name__ == "__main__":
    src = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path("8140/sources/dod8140-matrix-v2.1-20250919.xlsx")
    )
    out = (
        Path(sys.argv[2])
        if len(sys.argv) > 2
        else Path("8140/8140-cert-requirements.xlsx")
    )
    build(src, out)
    print(f"wrote {out}")
