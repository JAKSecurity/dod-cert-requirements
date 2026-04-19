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

import colorsys

from scripts.visual_spec import (
    CERT_COLOR_OVERRIDES,
    CERT_ORDER_BY_VENDOR,
    CERT_SHORT_NAMES,
    CY101_SEPARATOR_BEFORE_CODE,
    DEFAULT_PALETTE,
    ROLE_NAME_OVERRIDES,
    ROLE_ORDER,
    ROLE_ROW_HIGHLIGHTS,
    VENDOR_HUE_SPEC,
    VENDOR_ORDER,
    VENDOR_PALETTE,
    VENDOR_SHORT_NAMES,
)


# Lightness values for proficiency levels. Lower = darker.
LEVEL_LIGHTNESS = {1: 0.82, 2: 0.64, 3: 0.42}
HEADER_CELL_LIGHTNESS = 0.30  # cert acronym header — darker than Advanced


def _hsl_to_argb(hue_deg: float, sat: float, lightness: float) -> str:
    """Convert HSL (hue in degrees, sat+lightness 0-1) to Excel ARGB string."""
    h = (hue_deg % 360) / 360.0
    r, g, b = colorsys.hls_to_rgb(h, lightness, sat)
    return f"FF{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"


def _cert_color_spec(short_cert: str, vendor_short: str,
                     cert_index: int, total_certs: int) -> tuple[float, float]:
    """Return (hue_deg, saturation) for a cert column. Overrides win."""
    if short_cert in CERT_COLOR_OVERRIDES:
        return CERT_COLOR_OVERRIDES[short_cert]
    spec = VENDOR_HUE_SPEC.get(vendor_short)
    if spec is None:
        return 0.0, 0.0
    if total_certs <= 1:
        t = 0.0
    else:
        t = cert_index / (total_certs - 1)
    hue = spec["hue_start"] + t * (spec["hue_end"] - spec["hue_start"])
    return hue, spec["sat"]


def _cert_cell_fill(short_cert: str, vendor_short: str, cert_index: int,
                    total_certs: int, level: int) -> str:
    hue, sat = _cert_color_spec(short_cert, vendor_short, cert_index, total_certs)
    # For grayscale (sat=0) we use a lightness scale; for color we also use lightness.
    return _hsl_to_argb(hue, sat, LEVEL_LIGHTNESS[level])


def _cert_header_fill(short_cert: str, vendor_short: str, cert_index: int,
                      total_certs: int) -> str:
    hue, sat = _cert_color_spec(short_cert, vendor_short, cert_index, total_certs)
    return _hsl_to_argb(hue, sat, HEADER_CELL_LIGHTNESS)


def _heatmap_fill(value: int, max_value: int, kind: str) -> str | None:
    """Return fill color for a heat-map cell. kind=positions or points."""
    if value <= 0 or max_value <= 0:
        return None
    t = value / max_value
    # Two palettes: positions (green-red scale) and points (similar).
    # Both use lightness driven by t.
    if kind == "positions":
        # light pink -> dark red scale, per Jan 2025 convention
        return _hsl_to_argb(hue_deg=0, sat=0.55, lightness=0.90 - 0.55 * t)
    # points
    return _hsl_to_argb(hue_deg=130, sat=0.45, lightness=0.90 - 0.55 * t)

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


def _vendor_short_name(v: str) -> str:
    return VENDOR_SHORT_NAMES.get(v, v)


def _cert_short_name(c: str) -> str:
    return CERT_SHORT_NAMES.get(c, c)


def _build_cert_column_layout(rows: list[dict]) -> list[tuple[str, str]]:
    """Return ordered list of (short_cert, short_vendor) tuples for pivot columns.

    Layout follows visual_spec.VENDOR_ORDER and CERT_ORDER_BY_VENDOR for known
    shared certs; V2.1-new certs are appended to their vendor group in
    appearance order. Unknown vendors (i.e. vendor strings not in
    VENDOR_SHORT_NAMES) get their own group at the end of the layout.
    """
    # Index V2.1 data by short vendor, collecting short cert names in
    # their V2.1 appearance order for consistency.
    by_vendor: dict[str, list[str]] = {}
    seen: set[tuple[str, str]] = set()
    for r in rows:
        vs = _vendor_short_name(r["vendor"])
        cs = _cert_short_name(r["acronym"])
        if (vs, cs) in seen:
            continue
        seen.add((vs, cs))
        by_vendor.setdefault(vs, []).append(cs)

    layout: list[tuple[str, str]] = []
    known_vendors: list[str] = list(VENDOR_ORDER)
    for v in known_vendors:
        present_certs = set(by_vendor.get(v, []))
        if not present_certs:
            continue
        spec_order = CERT_ORDER_BY_VENDOR.get(v, [])
        ordered: list[str] = []
        # First: spec-ordered certs that are actually present in V2.1.
        for cert in spec_order:
            if cert in present_certs:
                ordered.append(cert)
                present_certs.discard(cert)
        # Then: any remaining V2.1-present certs not in the spec, appended
        # in their V2.1 appearance order.
        for cert in by_vendor[v]:
            if cert in present_certs:
                ordered.append(cert)
                present_certs.discard(cert)
        for cert in ordered:
            layout.append((cert, v))

    # Finally: unknown vendors (not in VENDOR_ORDER). Append in appearance order.
    for v, certs in by_vendor.items():
        if v in known_vendors:
            continue
        for cert in certs:
            layout.append((cert, v))

    return layout


def _build_pivot_cells_short(rows: list[dict]) -> dict[tuple[str, str], int]:
    """(role_code, short_cert_name) -> highest proficiency level 1/2/3."""
    cells: dict[tuple[str, str], int] = {}
    for r in rows:
        key = (r["wrc"], _cert_short_name(r["acronym"]))
        level = PROFICIENCY_LEVEL[r["proficiency"]]
        if key not in cells or cells[key] < level:
            cells[key] = level
    return cells


def _build_role_row_order(role_catalog: dict) -> list[str | None]:
    """Produce the ordered list of role rows for the pivot. Pending-review
    roles are omitted entirely. The sentinel value None marks the position
    of the CY 101 separator row (inserted between the two role groups).
    Roles present in role_catalog but not in ROLE_ORDER are appended at the
    end (safety net for V2.1 additions not yet slotted into the spec).
    """
    ordered_roles: list[str | None] = []
    seen: set[str] = set()
    for code in ROLE_ORDER:
        if code in role_catalog:
            if code == CY101_SEPARATOR_BEFORE_CODE:
                ordered_roles.append(None)
            ordered_roles.append(code)
            seen.add(code)
    unexpected = sorted(set(role_catalog) - seen - set(PENDING_REVIEW_ROLES))
    if unexpected:
        # Silent safety net; listed in refresh-notes if needed.
        ordered_roles.extend(unexpected)
    return ordered_roles


# Cell alignment / style presets
CERT_HEADER_ROT = Alignment(horizontal="center", vertical="bottom", text_rotation=90, wrap_text=False)
CELL_CENTER = Alignment(horizontal="center", vertical="center")


def _palette_for(vendor_short: str) -> dict:
    return VENDOR_PALETTE.get(vendor_short, DEFAULT_PALETTE)


def _cert_index_within_vendor(cert_columns: list[tuple[str, str]]) -> dict[int, tuple[int, int]]:
    """Map global column index -> (index-within-vendor, total-certs-for-vendor)."""
    by_vendor_positions: dict[str, list[int]] = {}
    for idx, (_, vendor) in enumerate(cert_columns):
        by_vendor_positions.setdefault(vendor, []).append(idx)
    mapping: dict[int, tuple[int, int]] = {}
    for vendor, positions in by_vendor_positions.items():
        total = len(positions)
        for within_idx, global_idx in enumerate(positions):
            mapping[global_idx] = (within_idx, total)
    return mapping


def write_pivot_sheet(
    wb: Workbook,
    role_catalog: dict,
    rows: list[dict],
) -> None:
    ws = wb.create_sheet("Certification Analysis")

    cert_columns = _build_cert_column_layout(rows)
    pivot_cells = _build_pivot_cells_short(rows)
    role_rows = _build_role_row_order(role_catalog)
    cert_pos = _cert_index_within_vendor(cert_columns)

    first_cert_col = 2  # Column B
    last_cert_col = first_cert_col + len(cert_columns) - 1
    echo_col = last_cert_col + 1  # right-hand Work Role echo column
    margin_col = echo_col + 1      # "darker shades = more coverage" note column

    banner_fill = PatternFill("solid", fgColor="FF1F4E79")
    white_bold = Font(bold=True, color="FFFFFFFF")
    white_bold_small = Font(bold=True, color="FFFFFFFF", size=10)

    # ----- Row 1: banner -----
    ws.cell(row=1, column=1, value="DoD 8140.03 Foundational Qualification: Personal Certification").font = Font(
        bold=True, size=12, color="FFFFFFFF"
    )
    ws.cell(row=1, column=1).fill = banner_fill
    ws.cell(row=1, column=1).alignment = CELL_CENTER
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=echo_col)

    # ----- Row 2: vendor group headers (merged per vendor) -----
    col_cursor = first_cert_col
    vendor_iter = list(VENDOR_ORDER) + sorted(
        {vend for _, vend in cert_columns if vend not in VENDOR_ORDER}
    )
    for v in vendor_iter:
        certs_for_v = [c for c, vv in cert_columns if vv == v]
        if not certs_for_v:
            continue
        span = len(certs_for_v)
        start = col_cursor
        end = col_cursor + span - 1
        pal = _palette_for(v)
        cell = ws.cell(row=2, column=start, value=v)
        cell.font = white_bold
        cell.fill = PatternFill("solid", fgColor=pal["base"])
        cell.alignment = CELL_CENTER
        if span > 1:
            ws.merge_cells(start_row=2, start_column=start, end_row=2, end_column=end)
        col_cursor = end + 1

    # ----- Row 3: cert acronym headers (each cert its own color) -----
    for c in (1, echo_col):
        hcell = ws.cell(row=3, column=c, value="Work Role")
        hcell.font = white_bold
        hcell.fill = banner_fill
        hcell.alignment = CELL_CENTER
    for i, (cert, vendor) in enumerate(cert_columns):
        within_idx, total = cert_pos[i]
        header_fill = _cert_header_fill(cert, vendor, within_idx, total)
        cell = ws.cell(row=3, column=first_cert_col + i, value=cert)
        cell.font = white_bold_small
        cell.fill = PatternFill("solid", fgColor=header_fill)
        cell.alignment = CERT_HEADER_ROT

    # ----- Role rows -----
    cy101_link = "https://cyber.mil/training/cyber-101/"
    cy101_message = (
        "CY 101 (40-hour online course) satisfies DoD 8140 foundational qualification "
        "requirements for all Cyber Enabler work roles below (validate with DoD under V2.1)"
    )
    band_fill = PatternFill("solid", fgColor="FFF2F2F2")  # very light gray banding

    current_row = 4
    first_data_row = 4
    last_data_row = 4
    data_row_count = 0
    for entry in role_rows:
        if entry is None:
            # CY 101 separator row
            c = ws.cell(row=current_row, column=1, value=cy101_message)
            c.font = Font(bold=True, italic=True, color="FFFFFFFF")
            c.fill = PatternFill("solid", fgColor="FF203864")
            c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
            c.hyperlink = cy101_link
            ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=echo_col)
            ws.row_dimensions[current_row].height = 22
            current_row += 1
            continue
        code = entry
        name = ROLE_NAME_OVERRIDES.get(code, role_catalog[code]["name"])
        role_label = f"({code}) {name}"
        band = (data_row_count % 2 == 1)
        data_row_count += 1
        # Column A (left label) and echo column (right label)
        a_cell = ws.cell(row=current_row, column=1, value=role_label)
        a_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        echo_cell = ws.cell(row=current_row, column=echo_col, value=role_label)
        echo_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        # Row-level highlight (e.g. 451 red) overrides banding
        highlight = ROLE_ROW_HIGHLIGHTS.get(code)
        if highlight:
            fill = PatternFill("solid", fgColor=highlight)
            a_cell.fill = fill
            a_cell.font = Font(bold=True, color="FFFFFFFF")
            echo_cell.fill = fill
            echo_cell.font = Font(bold=True, color="FFFFFFFF")
        elif band:
            a_cell.fill = band_fill
            echo_cell.fill = band_fill
        # Data cells
        for i, (cert, vendor) in enumerate(cert_columns):
            level = pivot_cells.get((code, cert))
            if level is None:
                if band:
                    blank = ws.cell(row=current_row, column=first_cert_col + i)
                    blank.fill = band_fill
                continue
            within_idx, total = cert_pos[i]
            fill_hex = _cert_cell_fill(cert, vendor, within_idx, total, level)
            cell = ws.cell(row=current_row, column=first_cert_col + i, value=level)
            cell.alignment = CELL_CENTER
            cell.fill = PatternFill("solid", fgColor=fill_hex)
            # Text color: light on dark cells, dark on light cells
            text_color = "FFFFFFFF" if level == 3 else "FF000000"
            cell.font = Font(bold=True, color=text_color)
        last_data_row = current_row
        current_row += 1

    # ----- Proficiency legend row -----
    current_row += 1  # blank
    legend_cell = ws.cell(
        row=current_row, column=1,
        value="Proficiency levels: Basic = 1, Intermediate = 2, Advanced = 3",
    )
    legend_cell.font = Font(italic=True)
    current_row += 1

    # ----- Repeated cert header row (above heatmap) -----
    repeat_header_row = current_row
    for c in (1, echo_col):
        rh = ws.cell(row=repeat_header_row, column=c, value="Work Role")
        rh.font = white_bold
        rh.fill = banner_fill
        rh.alignment = CELL_CENTER
    for i, (cert, vendor) in enumerate(cert_columns):
        within_idx, total = cert_pos[i]
        header_fill = _cert_header_fill(cert, vendor, within_idx, total)
        cell = ws.cell(row=repeat_header_row, column=first_cert_col + i, value=cert)
        cell.font = white_bold_small
        cell.fill = PatternFill("solid", fgColor=header_fill)
        cell.alignment = CERT_HEADER_ROT
    ws.row_dimensions[repeat_header_row].height = 60
    current_row += 1

    # ----- Summary rows (formulas + heatmap fills) -----
    totals_row = current_row
    ws.cell(row=totals_row, column=1, value="Total Positions Covered").font = Font(bold=True)
    ws.cell(row=totals_row, column=echo_col, value="Total Positions Covered").font = Font(bold=True)
    current_row += 1

    points_row = current_row
    ws.cell(row=points_row, column=1, value='Total "Points" (proficiency levels \u00d7 positions)').font = Font(bold=True)
    ws.cell(row=points_row, column=echo_col, value='Total "Points"').font = Font(bold=True)
    current_row += 1

    # Pre-compute max values per row for heat-map scaling
    positions_values: list[int] = []
    points_values: list[int] = []
    for i, (cert, _vendor) in enumerate(cert_columns):
        positions_values.append(
            sum(1 for code in role_catalog if (code, cert) in pivot_cells)
        )
        points_values.append(
            sum(pivot_cells[(code, cert)] for code in role_catalog if (code, cert) in pivot_cells)
        )
    max_positions = max(positions_values) if positions_values else 0
    max_points = max(points_values) if points_values else 0

    for i in range(len(cert_columns)):
        col_letter = get_column_letter(first_cert_col + i)
        data_range = f"{col_letter}{first_data_row}:{col_letter}{last_data_row}"
        # Formulas (auditable)
        tcell = ws.cell(row=totals_row, column=first_cert_col + i, value=f"=COUNT({data_range})")
        pcell = ws.cell(row=points_row, column=first_cert_col + i, value=f"=SUM({data_range})")
        tcell.alignment = CELL_CENTER
        pcell.alignment = CELL_CENTER
        # Heatmap fills driven by pre-computed values
        pos_fill = _heatmap_fill(positions_values[i], max_positions, "positions")
        pts_fill = _heatmap_fill(points_values[i], max_points, "points")
        if pos_fill:
            tcell.fill = PatternFill("solid", fgColor=pos_fill)
        if pts_fill:
            pcell.fill = PatternFill("solid", fgColor=pts_fill)
        # Bold text on the high-coverage cells
        high_threshold_pos = 0.7 * max_positions if max_positions else 0
        high_threshold_pts = 0.7 * max_points if max_points else 0
        if positions_values[i] >= high_threshold_pos and positions_values[i] > 0:
            tcell.font = Font(bold=True)
        if points_values[i] >= high_threshold_pts and points_values[i] > 0:
            pcell.font = Font(bold=True)

    # Margin note: "darker shades cover more work roles"
    margin_cell = ws.cell(
        row=totals_row, column=margin_col,
        value="darker shades cover more work roles"
    )
    margin_cell.font = Font(italic=True, size=9)
    margin_cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.merge_cells(start_row=totals_row, start_column=margin_col, end_row=points_row, end_column=margin_col)

    # ----- Footnote (pending-review roles) -----
    current_row += 2
    footnote = (
        "Note: The following work roles exist in DoD 8140 V2.1 but have no "
        "published certification options (pending DoD review): "
        + ", ".join(f"({c}) {n}" for c, n in PENDING_REVIEW_ROLES.items())
        + "."
    )
    fn_cell = ws.cell(row=current_row, column=1, value=footnote)
    fn_cell.font = Font(italic=True, color="FF595959")
    fn_cell.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=echo_col)
    ws.row_dimensions[current_row].height = 30

    # ----- Column widths -----
    ws.column_dimensions["A"].width = 47
    for i in range(len(cert_columns)):
        letter = get_column_letter(first_cert_col + i)
        ws.column_dimensions[letter].width = 3.5
    ws.column_dimensions[get_column_letter(echo_col)].width = 47
    ws.column_dimensions[get_column_letter(margin_col)].width = 22

    # ----- Row heights -----
    ws.row_dimensions[1].height = 19
    ws.row_dimensions[2].height = 19
    ws.row_dimensions[3].height = 60  # rotated cert acronyms
    for r in range(4, last_data_row + 1):
        if r not in ws.row_dimensions or ws.row_dimensions[r].height is None:
            ws.row_dimensions[r].height = 16

    # ----- Freeze panes: left of B, below row 3 -----
    ws.freeze_panes = "B4"


# ----------------------------------------------------------------------------
# Entry point
# ----------------------------------------------------------------------------

def build(v21_xlsx_path: str | Path, output_path: str | Path) -> None:
    rows = read_v21_certification_rows(v21_xlsx_path)
    role_catalog = build_role_catalog(rows)
    per_role = build_per_role_by_level(rows)

    wb = Workbook()
    wb.remove(wb.active)
    write_explanation_sheet(wb)
    write_summary_sheet(wb, role_catalog, per_role)
    write_pivot_sheet(wb, role_catalog, rows)
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
