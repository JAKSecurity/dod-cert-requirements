"""Build the 8570 reference PDF from the archived cyber.mil HTML.

Pipeline:
    archive HTML  -->  parse tables  -->  markdown  -->  (pandoc)  -->  docx
                                                    -->  (Word COM)  -->  pdf

Layout (per Jeff, 2026-04-20):
    - Tables at the top — readers came for the cert list, surface it first.
    - All narrative (provenance, why-this-exists, notes, reference block)
      moves below the tables.
    - Baseline cert table is laid out as one cert per row with grid lines,
      mirroring the visual style of the original DoD page.
"""
import subprocess
import sys
import tempfile
from copy import copy
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup


def _header_texts(row) -> list[str]:
    """Extract header cell text; strip <sup> footnote markers."""
    out = []
    for td in row.find_all(["td", "th"]):
        td_copy = copy(td)
        for sup in td_copy.find_all("sup"):
            sup.decompose()
        out.append(td_copy.get_text(" ", strip=True))
    return out


def _cell_certs(td) -> list[str]:
    """Split a data cell (with <br>-separated cert entries) into a list."""
    text = td.get_text(separator="\n").strip()
    return [p.strip() for p in text.split("\n") if p.strip()]


def _ragged_table_markdown(headers: list[str], columns: list[list[str]]) -> str:
    """Render a ragged-column table as markdown. Each column's entries
    become individual rows; shorter columns pad with empty cells."""
    # Pad columns list to match header count
    while len(columns) < len(headers):
        columns.append([])
    max_rows = max((len(c) for c in columns), default=0)
    if max_rows == 0:
        return ""
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for i in range(max_rows):
        row = []
        for col in columns:
            row.append(col[i] if i < len(col) else "")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def extract_baseline_tables(baseline_table) -> list[str]:
    """Parse the 8570 baseline table (alternating header/data row pairs).

    Produces a list of markdown sub-tables — one per category block
    (IAT, IAM, IASAE, CSSP Analyst row, CSSP Auditor row). Each is
    3-column with ragged rows (one cert per row)."""
    rows = list(baseline_table.find_all("tr"))
    result: list[str] = []
    for i in range(0, len(rows), 2):
        if i + 1 >= len(rows):
            break
        headers = _header_texts(rows[i])
        data_cells = [_cell_certs(td) for td in rows[i + 1].find_all(["td", "th"])]
        block = _ragged_table_markdown(headers, data_cells)
        if block:
            result.append(block)
    return result


def extract_provider_table(provider_table) -> str:
    """Parse the 8570 certification providers table.

    Already 2-column (Provider | Cert Name), one row per pair. Preserve
    directly as markdown."""
    if provider_table is None:
        return ""
    rows = list(provider_table.find_all("tr"))
    if not rows:
        return ""
    # Header
    header_cells = [td.get_text(" ", strip=True).replace("|", "/")
                    for td in rows[0].find_all(["td", "th"])]
    lines = ["| " + " | ".join(header_cells) + " |"]
    lines.append("| " + " | ".join(["---"] * len(header_cells)) + " |")
    for tr in rows[1:]:
        cells = [td.get_text(" ", strip=True).replace("|", "/").replace("\n", " ")
                 for td in tr.find_all(["td", "th"])]
        while len(cells) < len(header_cells):
            cells.append("")
        lines.append("| " + " | ".join(cells[: len(header_cells)]) + " |")
    return "\n".join(lines)


def extract_footnotes(soup: BeautifulSoup) -> list[str]:
    """Return the three policy-relevant footnote paragraphs."""
    keys = ("The GIAC GSE", "* This organization", "** CySA+")
    out: list[str] = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if any(text.startswith(k) for k in keys):
            out.append(text)
    return out


def build_markdown(baseline_blocks: list[str], provider_md: str,
                   footnotes: list[str]) -> str:
    compile_date = date.today().isoformat()
    parts = [
        "---",
        'title: "DoD 8570.01-M Approved Baseline Certifications — Reference Copy"',
        'author: "Compiled by Jeff Krueger"',
        f'date: "{compile_date}"',
        "---",
        "",
        "## Approved Baseline Certifications",
        "",
    ]
    # Block order in the source HTML corresponds to the 5 category pairs:
    block_labels = [
        None,  # IAT (headers already carry names)
        None,  # IAM
        None,  # IASAE
        None,  # CSSP Analyst / Infrastructure Support / Incident Responder
        None,  # CSSP Auditor / Manager
    ]
    for idx, block in enumerate(baseline_blocks):
        parts.append(block)
        parts.append("")
    parts.extend([
        "## IA Workforce Certification Providers",
        "",
        provider_md,
        "",
    ])
    parts.append("## Notes")
    parts.append("")
    # This repo's own annotations on the reproduced list:
    parts.append(
        "- This document reproduces the DoD 8570 Approved Baseline Certifications list "
        "as DoD last published it (snapshot date above). Cert names and vendor branding "
        "are preserved as written; some have changed since."
    )
    parts.append(
        "- **CASP+ / SecurityX:** CompTIA renamed the CompTIA Advanced Security Practitioner "
        "(CASP+) certification to **SecurityX** on **17 December 2024**, coinciding with the "
        "release of exam version CAS-005 (V5). The two names refer to the same CompTIA-owned "
        "certification; any reference to CASP+ in this document should be read as the credential "
        "CompTIA now calls SecurityX."
    )
    # Footnotes preserved from the archived DoD page:
    for fn in footnotes:
        parts.append(f"- {fn}")
    parts.append("")
    parts.extend([
        "## Provenance",
        "",
        "Reproduced from a web.archive.org snapshot of `public.cyber.mil/wid/cwmp/dod-approved-8570-baseline-certifications/` dated **2024-01-30**, which was the last publicly archived version of this page before DoD removed it following the DoDM 8140.03 transition.",
        "",
        "**Archive URL:** <https://web.archive.org/web/20240130012654/https://public.cyber.mil/wid/cwmp/dod-approved-8570-baseline-certifications/>",
        "",
        "## Why this document exists",
        "",
        "DoD 8570.01-M was superseded by DoDM 8140.03 in 2023. When public.cyber.mil removed the 8570 baseline page, the authoritative list that many still-active contracts reference by name lost its public home. This document preserves that list so contract officers, CORs, and compliance staff can still cite an authoritative record.",
        "",
        "This is a reference reproduction. It is not a policy document. For current cybersecurity workforce qualification requirements, see DoDM 8140.03 and the DoD Cyber Workforce Qualifications Matrices at `www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices`.",
        "",
        "## Reference",
        "",
        f"- Snapshot date: 2024-01-30",
        f"- Compilation date: {compile_date}",
        "- Compiled by: Jeff Krueger",
        "",
    ])
    return "\n".join(parts)


def pandoc_markdown_to_docx(md_path: Path, docx_path: Path) -> None:
    subprocess.run(
        ["pandoc", str(md_path), "-o", str(docx_path), "--from", "markdown"],
        check=True,
    )


def word_docx_to_pdf_with_grid(docx_path: Path, pdf_path: Path) -> None:
    """Open DOCX in Word, apply grid lines to every table, export to PDF."""
    import win32com.client  # type: ignore[import-untyped]

    # Word border constants
    WD_LINE_STYLE_SINGLE = 1
    BORDER_IDS = (-1, -2, -3, -4, -5, -6)  # top/left/bottom/right/horiz/vert

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(docx_path.resolve()))
        try:
            # Apply grid lines (major + minor) to every table
            for t in doc.Tables:
                t.Borders.Enable = True
                for bid in BORDER_IDS:
                    try:
                        t.Borders(bid).LineStyle = WD_LINE_STYLE_SINGLE
                        t.Borders(bid).LineWidth = 4  # 1pt
                    except Exception:
                        pass
            doc.SaveAs2(str(pdf_path.resolve()), FileFormat=17)
        finally:
            doc.Close(SaveChanges=False)
    finally:
        word.Quit()


def render_pdf(html_path: str | Path, out_pdf: str | Path) -> Path:
    html = Path(html_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    baseline = soup.find("table", id="tablepress-iawip-approved_baseline_certifications")
    provider = soup.find("table", id="tablepress-iawip-certification_providers")
    baseline_blocks = extract_baseline_tables(baseline) if baseline else []
    provider_md = extract_provider_table(provider)
    footnotes = extract_footnotes(soup)
    doc_md = build_markdown(baseline_blocks, provider_md, footnotes)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        md_path = tmp_dir / "8570.md"
        docx_path = tmp_dir / "8570.docx"
        md_path.write_text(doc_md, encoding="utf-8")
        pandoc_markdown_to_docx(md_path, docx_path)
        word_docx_to_pdf_with_grid(docx_path, Path(out_pdf))
    return Path(out_pdf)


if __name__ == "__main__":
    html = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else "8570/sources/cyber-mil-snapshot-20240130.html"
    )
    out = Path(
        sys.argv[2] if len(sys.argv) > 2 else "8570/8570-baseline-reference.pdf"
    )
    render_pdf(html, out)
    print(f"wrote {out}")
