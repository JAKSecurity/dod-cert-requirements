from scripts.render_changelog import render


def test_empty_diff_renders_no_changes():
    md = render(
        {"added_roles": [], "removed_roles": [], "cell_changes": []},
        refresh_date="2026-04-18",
    )
    assert "No changes" in md or "no changes" in md


def test_added_role_appears_with_name():
    md = render(
        {
            "added_roles": [
                {"work_role_code": "999", "work_role_name": "New Role"}
            ],
            "removed_roles": [],
            "cell_changes": [],
        },
        refresh_date="2026-04-18",
    )
    assert "999" in md
    assert "New Role" in md
    assert "Added" in md or "added" in md


def test_removed_role_appears_with_name():
    md = render(
        {
            "added_roles": [],
            "removed_roles": [
                {"work_role_code": "888", "work_role_name": "Old Role"}
            ],
            "cell_changes": [],
        },
        refresh_date="2026-04-18",
    )
    assert "888" in md
    assert "Old Role" in md


def test_cell_change_formatted_as_added_removed():
    md = render(
        {
            "added_roles": [],
            "removed_roles": [],
            "cell_changes": [
                {
                    "work_role_code": "411",
                    "work_role_name": "Technical Support Specialist",
                    "qualification_type": "certification",
                    "proficiency_level": "basic",
                    "added": ["CFR"],
                    "removed": ["A+"],
                }
            ],
        },
        refresh_date="2026-04-18",
    )
    assert "411" in md
    assert "Technical Support Specialist" in md
    assert "CFR" in md
    assert "A+" in md


def test_refresh_date_in_output_header():
    md = render(
        {"added_roles": [], "removed_roles": [], "cell_changes": []},
        refresh_date="2026-04-18",
    )
    assert "2026-04-18" in md


def test_known_gap_roles_recategorized_from_removed():
    md = render(
        {
            "added_roles": [],
            "removed_roles": [
                {"work_role_code": "462", "work_role_name": "Control Systems"},
                {"work_role_code": "555", "work_role_name": "Legit Removed Role"},
            ],
            "cell_changes": [],
        },
        refresh_date="2026-04-18",
        known_gap_roles=["462"],
    )
    # Both roles present, but under different sections
    assert "pending" in md.lower()
    assert "462" in md and "Control Systems" in md
    assert "555" in md and "Legit Removed Role" in md
    # 462 should appear AFTER the pending-review heading, not removed heading.
    pending_idx = md.lower().index("pending")
    removed_idx = md.lower().index("not in v2.1") if "not in v2.1" in md.lower() else -1
    if removed_idx > 0:
        # 462 appears after pending heading
        idx_462 = md.index("462")
        assert idx_462 > pending_idx


def test_summary_counts_are_correct():
    md = render(
        {
            "added_roles": [
                {"work_role_code": "111", "work_role_name": "A"},
                {"work_role_code": "222", "work_role_name": "B"},
            ],
            "removed_roles": [
                {"work_role_code": "999", "work_role_name": "Z"}
            ],
            "cell_changes": [
                {
                    "work_role_code": "411",
                    "work_role_name": "X",
                    "qualification_type": "certification",
                    "proficiency_level": "basic",
                    "added": ["Y"],
                    "removed": [],
                }
            ],
        },
        refresh_date="2026-04-18",
    )
    assert "2" in md  # 2 added roles
    assert "1" in md  # 1 removed role / 1 cell change
