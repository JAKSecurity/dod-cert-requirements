"""Structured cell-level diff between two canonical matrices.

Compares two lists of canonical records (each with work_role_code,
work_role_name, qualification_type, proficiency_level, certs).
Produces a structured diff:
    - added_roles:    role codes present in new but not in old
    - removed_roles:  role codes present in old but not in new
    - cell_changes:   per-cell diffs for roles present in both sides,
                      listing added and removed certs per cell

Pure function — no I/O. CLI entrypoint reads JSON, filters to
certification-only (education path out of scope per repo design),
writes JSON diff.
"""
import json
import sys
from pathlib import Path
from typing import Any


def _key(r: dict[str, Any]) -> tuple[str, str, str]:
    return (r["work_role_code"], r["qualification_type"], r["proficiency_level"])


def diff_records(old: list[dict[str, Any]], new: list[dict[str, Any]]) -> dict[str, Any]:
    old_idx = {_key(r): r for r in old}
    new_idx = {_key(r): r for r in new}
    old_roles = {r["work_role_code"] for r in old}
    new_roles = {r["work_role_code"] for r in new}

    added_roles = sorted(new_roles - old_roles)
    removed_roles = sorted(old_roles - new_roles)

    cell_changes = []
    # Only compare cells for roles present in BOTH sides — new roles are
    # already reported in added_roles, retired roles in removed_roles.
    shared_role_keys = {
        k for k in (set(old_idx) & set(new_idx))
        if k[0] not in added_roles and k[0] not in removed_roles
    }
    for key in sorted(shared_role_keys):
        old_certs = set(old_idx[key]["certs"])
        new_certs = set(new_idx[key]["certs"])
        if old_certs != new_certs:
            cell_changes.append({
                "work_role_code": key[0],
                "work_role_name": new_idx[key]["work_role_name"],
                "qualification_type": key[1],
                "proficiency_level": key[2],
                "added": sorted(new_certs - old_certs),
                "removed": sorted(old_certs - new_certs),
            })

    return {
        "added_roles": added_roles,
        "removed_roles": removed_roles,
        "cell_changes": cell_changes,
    }


def _filter_cert_only(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r["qualification_type"] == "certification"]


if __name__ == "__main__":
    old_path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/jan2025.json")
    new_path = Path(sys.argv[2] if len(sys.argv) > 2 else "data/official.json")
    out = Path("data/diff.json")

    old = _filter_cert_only(json.loads(old_path.read_text(encoding="utf-8")))
    new = _filter_cert_only(json.loads(new_path.read_text(encoding="utf-8")))

    result = diff_records(old, new)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        f"certification-only diff: "
        f"+{len(result['added_roles'])} roles, "
        f"-{len(result['removed_roles'])} roles, "
        f"{len(result['cell_changes'])} cell changes -> {out}"
    )
