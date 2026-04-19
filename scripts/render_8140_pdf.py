"""Convert the 8140 xlsx to PDF via Microsoft Excel (headless via COM).

Why Excel and not LibreOffice: LibreOffice isn't installed on Jeff's box and
Excel is. COM automation runs Excel invisibly, loads the xlsx, and uses
ExportAsFixedFormat (Excel's native PDF export) for high-fidelity output.

Requires: pywin32, Microsoft Excel.
"""
import sys
from pathlib import Path


def render_pdf(xlsx_path: str | Path, out_pdf: str | Path) -> Path:
    import win32com.client  # type: ignore[import-untyped]

    xlsx_abs = Path(xlsx_path).resolve()
    out_abs = Path(out_pdf).resolve()

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    try:
        wb = excel.Workbooks.Open(str(xlsx_abs))
        try:
            # xlTypePDF = 0
            wb.ExportAsFixedFormat(
                Type=0,
                Filename=str(out_abs),
                Quality=0,  # xlQualityStandard
                IncludeDocProperties=True,
                IgnorePrintAreas=False,
                OpenAfterPublish=False,
            )
        finally:
            wb.Close(SaveChanges=False)
    finally:
        excel.Quit()

    return out_abs


if __name__ == "__main__":
    xlsx = Path(sys.argv[1] if len(sys.argv) > 1 else "8140/8140-cert-requirements.xlsx")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "8140/8140-cert-requirements.pdf")
    render_pdf(xlsx, out)
    print(f"wrote {out}")
