"""Build the 8570 reference PDF from the archived cyber.mil HTML.

Pipeline:
    archive HTML  -->  parse tables  -->  markdown  -->  (pandoc)  -->  docx
                                                    -->  (Word COM)  -->  pdf

The provenance paragraph cites the web.archive.org snapshot URL and date.
Authorship line: "Compiled by Jeff Krueger" — no email, no web URL.
"""
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup


def extract_tables(html: str) -> tuple[str, str, list[str]]:
    """Return (baseline_markdown, provider_markdown, footnotes_list)."""
    soup = BeautifulSoup(html, "lxml")

    baseline = soup.find("table", id="tablepress-iawip-approved_baseline_certifications")
    provider = soup.find("table", id="tablepress-iawip-certification_providers")

    def table_to_markdown(table) -> str:
        if table is None:
            return "[source table not found]"
        rows: list[list[str]] = []
        for tr in table.find_all("tr"):
            cells = []
            for td in tr.find_all(["td", "th"]):
                text = td.get_text(separator="\n").strip()
                text = text.replace("|", "/")  # avoid MD table pipe confusion
                cells.append(text.replace("\n", " / "))
            rows.append(cells)
        if not rows:
            return ""
        lines = ["| " + " | ".join(rows[0]) + " |"]
        lines.append("| " + " | ".join(["---"] * len(rows[0])) + " |")
        for r in rows[1:]:
            # Pad to header width in case of ragged rows
            while len(r) < len(rows[0]):
                r.append("")
            lines.append("| " + " | ".join(r[: len(rows[0])]) + " |")
        return "\n".join(lines)

    baseline_md = table_to_markdown(baseline)
    provider_md = table_to_markdown(provider)

    footnote_keys = (
        "The GIAC GSE",
        "* This organization",
        "** CySA+",
    )
    footnotes: list[str] = []
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if any(text.startswith(k) for k in footnote_keys):
            footnotes.append(text)

    return baseline_md, provider_md, footnotes


def build_markdown(baseline_md: str, provider_md: str, footnotes: list[str]) -> str:
    compile_date = date.today().isoformat()
    parts = [
        "---",
        'title: "DoD 8570.01-M Approved Baseline Certifications — Reference Copy"',
        'author: "Compiled by Jeff Krueger"',
        f'date: "{compile_date}"',
        "---",
        "",
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
        "## Approved Baseline Certifications",
        "",
        baseline_md,
        "",
        "## IA Workforce Certification Providers",
        "",
        provider_md,
        "",
    ]
    if footnotes:
        parts.append("## Notes")
        parts.append("")
        for fn in footnotes:
            parts.append(f"- {fn}")
        parts.append("")
    parts.extend([
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


def word_docx_to_pdf(docx_path: Path, pdf_path: Path) -> None:
    import win32com.client  # type: ignore[import-untyped]

    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(docx_path.resolve()))
        try:
            # wdFormatPDF = 17
            doc.SaveAs2(str(pdf_path.resolve()), FileFormat=17)
        finally:
            doc.Close(SaveChanges=False)
    finally:
        word.Quit()


def render_pdf(html_path: str | Path, out_pdf: str | Path) -> Path:
    html = Path(html_path).read_text(encoding="utf-8")
    baseline_md, provider_md, footnotes = extract_tables(html)
    doc_md = build_markdown(baseline_md, provider_md, footnotes)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        md_path = tmp_dir / "8570.md"
        docx_path = tmp_dir / "8570.docx"
        md_path.write_text(doc_md, encoding="utf-8")
        pandoc_markdown_to_docx(md_path, docx_path)
        word_docx_to_pdf(docx_path, Path(out_pdf))
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
