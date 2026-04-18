import pytest

from scripts.schema import MatrixRecord, validate_matrix


def test_matrix_record_basic():
    r = MatrixRecord(
        work_role_code="411",
        work_role_name="Technical Support Specialist",
        qualification_type="certification",
        proficiency_level="basic",
        certs=["A+", "Network+"],
    )
    assert r.work_role_code == "411"
    assert r.certs == ["A+", "Network+"]


def test_certs_are_sorted_in_canonical_form():
    r = MatrixRecord(
        work_role_code="411",
        work_role_name="Tech Support",
        qualification_type="certification",
        proficiency_level="intermediate",
        certs=["Security+", "CND", "GFACT"],
    )
    canonical = r.to_canonical()
    assert canonical["certs"] == ["CND", "GFACT", "Security+"]


def test_validate_matrix_accepts_well_formed():
    records = [
        {
            "work_role_code": "411",
            "work_role_name": "X",
            "qualification_type": "certification",
            "proficiency_level": "basic",
            "certs": ["A+"],
        }
    ]
    validate_matrix(records)  # no raise


def test_validate_matrix_rejects_bad_proficiency():
    records = [
        {
            "work_role_code": "411",
            "work_role_name": "X",
            "qualification_type": "certification",
            "proficiency_level": "expert",
            "certs": ["A+"],
        }
    ]
    with pytest.raises(ValueError, match="proficiency_level"):
        validate_matrix(records)
