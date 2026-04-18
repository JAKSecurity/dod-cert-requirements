from scripts.diff_matrices import diff_records


def _rec(code, qtype, level, certs):
    return {
        "work_role_code": code,
        "work_role_name": f"Role {code}",
        "qualification_type": qtype,
        "proficiency_level": level,
        "certs": sorted(certs),
    }


def test_no_change_yields_empty_diff():
    a = [_rec("411", "certification", "basic", ["A+", "Network+"])]
    b = [_rec("411", "certification", "basic", ["A+", "Network+"])]
    d = diff_records(a, b)
    assert d["added_roles"] == []
    assert d["removed_roles"] == []
    assert d["cell_changes"] == []


def test_added_cert_detected():
    a = [_rec("411", "certification", "basic", ["A+"])]
    b = [_rec("411", "certification", "basic", ["A+", "Network+"])]
    d = diff_records(a, b)
    assert d["cell_changes"] == [
        {
            "work_role_code": "411",
            "work_role_name": "Role 411",
            "qualification_type": "certification",
            "proficiency_level": "basic",
            "added": ["Network+"],
            "removed": [],
        }
    ]


def test_removed_cert_detected():
    a = [_rec("411", "certification", "basic", ["A+", "Network+"])]
    b = [_rec("411", "certification", "basic", ["A+"])]
    d = diff_records(a, b)
    assert d["cell_changes"][0]["removed"] == ["Network+"]
    assert d["cell_changes"][0]["added"] == []


def test_new_role_detected():
    a = []
    b = [_rec("999", "certification", "basic", ["X"])]
    d = diff_records(a, b)
    assert d["added_roles"] == ["999"]
    # New role's cells should NOT be listed in cell_changes
    # (that would double-count; added_roles covers it)
    assert d["cell_changes"] == []


def test_retired_role_detected():
    a = [_rec("411", "certification", "basic", ["A+"])]
    b = []
    d = diff_records(a, b)
    assert d["removed_roles"] == ["411"]
    assert d["cell_changes"] == []


def test_multiple_cells_same_role_reported_separately():
    a = [
        _rec("411", "certification", "basic", ["A+"]),
        _rec("411", "certification", "intermediate", ["Security+"]),
    ]
    b = [
        _rec("411", "certification", "basic", ["A+", "Network+"]),
        _rec("411", "certification", "intermediate", ["Security+", "GSEC"]),
    ]
    d = diff_records(a, b)
    assert len(d["cell_changes"]) == 2
    levels_changed = {c["proficiency_level"] for c in d["cell_changes"]}
    assert levels_changed == {"basic", "intermediate"}


def test_certs_sorted_in_diff_output():
    a = [_rec("411", "certification", "basic", ["A+"])]
    b = [_rec("411", "certification", "basic", ["A+", "Network+", "CFR"])]
    d = diff_records(a, b)
    # Added certs should be sorted
    assert d["cell_changes"][0]["added"] == ["CFR", "Network+"]
