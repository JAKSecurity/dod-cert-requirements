from pathlib import Path

from scripts.normalize_jan2025_xlsx import normalize_xlsx

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_jan2025.xlsx"


def test_extracts_two_work_roles():
    records = normalize_xlsx(FIXTURE)
    roles = {r.work_role_code for r in records}
    assert roles == {"411", "421"}


def test_each_role_has_education_and_certification_records_at_each_level():
    records = normalize_xlsx(FIXTURE)
    r411 = [r for r in records if r.work_role_code == "411"]
    combos = {(r.qualification_type, r.proficiency_level) for r in r411}
    # All six combos emitted, regardless of cell content
    assert combos == {
        ("education", "basic"),
        ("education", "intermediate"),
        ("education", "advanced"),
        ("certification", "basic"),
        ("certification", "intermediate"),
        ("certification", "advanced"),
    }


def test_certs_are_split_and_stripped():
    records = normalize_xlsx(FIXTURE)
    basic_cert_411 = next(
        r for r in records
        if r.work_role_code == "411"
        and r.qualification_type == "certification"
        and r.proficiency_level == "basic"
    )
    assert basic_cert_411.certs == ["A+", "Network+"]


def test_tbd_values_produce_empty_cert_lists():
    records = normalize_xlsx(FIXTURE)
    ed_adv_411 = next(
        r for r in records
        if r.work_role_code == "411"
        and r.qualification_type == "education"
        and r.proficiency_level == "advanced"
    )
    assert ed_adv_411.certs == []  # "TBD" → empty


def test_blank_cell_produces_empty_cert_list():
    records = normalize_xlsx(FIXTURE)
    ed_inter_411 = next(
        r for r in records
        if r.work_role_code == "411"
        and r.qualification_type == "education"
        and r.proficiency_level == "intermediate"
    )
    assert ed_inter_411.certs == []


def test_literal_blank_marker_treated_as_empty():
    # Jeff's real xlsx uses the literal string '<blank>' in 40 cells to mean
    # "no certs at this level" — normalizer must treat this as empty.
    from scripts.normalize_jan2025_xlsx import _split_certs
    assert _split_certs("<blank>") == []
    assert _split_certs("<BLANK>") == []
    assert _split_certs("  <blank>  ") == []
    assert _split_certs("TBD") == []
    assert _split_certs("N/A") == []
    assert _split_certs("-") == []


def test_role_name_captured_without_code():
    records = normalize_xlsx(FIXTURE)
    r411 = next(r for r in records if r.work_role_code == "411")
    assert r411.work_role_name == "Technical Support Specialist"


def test_role_code_is_string_not_int():
    records = normalize_xlsx(FIXTURE)
    assert all(isinstance(r.work_role_code, str) for r in records)


def test_cert_intermediate_with_multiple_certs():
    records = normalize_xlsx(FIXTURE)
    cert_inter_411 = next(
        r for r in records
        if r.work_role_code == "411"
        and r.qualification_type == "certification"
        and r.proficiency_level == "intermediate"
    )
    assert cert_inter_411.certs == ["GFACT", "CND", "Security+", "GSEC"]
