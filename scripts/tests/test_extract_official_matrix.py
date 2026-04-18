from pathlib import Path

from scripts.extract_official_matrix import extract_from_xlsx

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_v21.xlsx"


def test_extracts_three_work_roles():
    records = extract_from_xlsx(FIXTURE)
    codes = {r.work_role_code for r in records}
    assert codes == {"111", "211", "411"}


def test_aggregates_multiple_certs_at_same_role_and_level():
    records = extract_from_xlsx(FIXTURE)
    r211_advanced = [
        r for r in records
        if r.work_role_code == "211" and r.proficiency_level == "advanced"
    ]
    assert len(r211_advanced) == 1
    assert set(r211_advanced[0].certs) == {"CySA+", "GCFA"}


def test_splits_same_role_across_proficiency_levels():
    records = extract_from_xlsx(FIXTURE)
    r411 = [r for r in records if r.work_role_code == "411"]
    levels = {r.proficiency_level for r in r411}
    assert levels == {"basic", "intermediate"}


def test_all_records_are_certification_type():
    records = extract_from_xlsx(FIXTURE)
    assert all(r.qualification_type == "certification" for r in records)


def test_role_names_are_stripped():
    records = extract_from_xlsx(FIXTURE)
    r111 = next(r for r in records if r.work_role_code == "111")
    # Fixture deliberately has trailing space in 'All-Source Analyst '
    assert r111.work_role_name == "All-Source Analyst"


def test_role_code_is_string_not_int():
    records = extract_from_xlsx(FIXTURE)
    assert all(isinstance(r.work_role_code, str) for r in records)


def test_proficiency_values_are_lowercased():
    records = extract_from_xlsx(FIXTURE)
    levels = {r.proficiency_level for r in records}
    assert levels.issubset({"basic", "intermediate", "advanced"})


def test_certs_are_deduplicated_per_cell():
    # Duplicate rows for same (role, level, cert) should collapse
    from openpyxl import load_workbook
    import tempfile, shutil
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        shutil.copy(FIXTURE, tmp.name)
        wb = load_workbook(tmp.name)
        ws = wb["Certification Repository"]
        # Add a duplicate row for (411, basic, A+)
        ws.append([411, "Technical Support Specialist", "IT (Cyberspace)", "A+", "Basic", "CompTIA, Inc."])
        wb.save(tmp.name)
        records = extract_from_xlsx(tmp.name)
    r411_basic = [r for r in records if r.work_role_code == "411" and r.proficiency_level == "basic"]
    assert len(r411_basic) == 1
    assert sorted(r411_basic[0].certs) == ["A+", "Network+"]
