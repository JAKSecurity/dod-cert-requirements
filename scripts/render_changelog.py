"""Pretty-print structured diff to human-readable CHANGELOG markdown.

This is an *informational* changelog showing how the V2.1 DoD 8140
qualification matrix differs from the Jan 2025 private working version.
It does NOT drive the refresh (the refreshed xlsx is built fresh from
V2.1 data; this changelog is for readers who want provenance).
"""
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


def render(
    diff: dict[str, Any],
    refresh_date: str | None = None,
    known_gap_roles: list[str] | None = None,
) -> str:
    """Render a structured diff as human-readable CHANGELOG markdown.

    known_gap_roles: work_role_codes that appear as "removed" in the diff because
        the V2.1 Certification Repository has no cert rows for them, but that
        actually exist in V2.1's role universe without any published
        certification options (DoD-pending review). These are re-categorized
        from "removed" to a dedicated "known gaps" section.
    """
    refresh_date = refresh_date or date.today().isoformat()
    gap_codes = set(known_gap_roles or [])
    lines = [
        f"# 8140 Matrix Changelog — refreshed {refresh_date}",
        "",
        "This document summarizes how the current DoD 8140 Foundational Qualification Matrix (V2.1, effective 2025-09-19) differs from the Jan 2025 private working version that served as this repo's starting point. It is informational — the refreshed xlsx published in this repo is generated directly from V2.1 source data, not patched from the Jan 2025 version.",
        "",
        "Scope: certification-path qualifications only. Other qualification paths (education, DoD training, commercial training, experience alternatives) are out of scope for this repo and therefore not diffed.",
        "",
    ]

    # Partition removed_roles into genuine-removed vs known-gap (pending DoD review)
    genuine_removed = [r for r in diff["removed_roles"] if r["work_role_code"] not in gap_codes]
    pending_review = [r for r in diff["removed_roles"] if r["work_role_code"] in gap_codes]

    total = len(diff["added_roles"]) + len(diff["removed_roles"]) + len(diff["cell_changes"])
    if total == 0:
        lines.append("No changes detected against V2.1 source.")
        return "\n".join(lines) + "\n"

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Work roles added in V2.1:** {len(diff['added_roles'])}")
    lines.append(f"- **Work roles removed since Jan 2025:** {len(genuine_removed)}")
    if pending_review:
        lines.append(f"- **Work roles with no cert data (pending DoD review):** {len(pending_review)}")
    lines.append(f"- **Cell-level cert changes (shared roles):** {len(diff['cell_changes'])}")
    lines.append("")

    if diff["added_roles"]:
        lines.append("## Work roles added in V2.1")
        lines.append("")
        lines.append("These work roles are in the current V2.1 Certification Repository but were not tracked in the Jan 2025 version. See the refreshed xlsx for their cert-list details.")
        lines.append("")
        for r in diff["added_roles"]:
            lines.append(f"- **({r['work_role_code']})** {r['work_role_name']}")
        lines.append("")

    if genuine_removed:
        lines.append("## Work roles not in V2.1")
        lines.append("")
        lines.append("These work roles existed in the Jan 2025 version but do not appear in the V2.1 Certification Repository. They may have been renamed, merged, or moved to a non-certification qualification path.")
        lines.append("")
        for r in genuine_removed:
            lines.append(f"- **({r['work_role_code']})** {r['work_role_name']}")
        lines.append("")

    if pending_review:
        lines.append("## Work roles with no certification data (pending DoD review)")
        lines.append("")
        lines.append("These work roles exist in the DoD 8140 V2.1 role universe but have no certification options published in the Certification Repository — the DoD marks them as pending review. They were historically tracked with blank certification cells and are omitted from the refreshed certification matrix. Their cert paths will be added in a future refresh when DoD publishes data.")
        lines.append("")
        for r in pending_review:
            lines.append(f"- **({r['work_role_code']})** {r['work_role_name']}")
        lines.append("")

    if diff["cell_changes"]:
        lines.append("## Cert-list changes (roles in both versions)")
        lines.append("")
        by_role: dict[str, list[dict[str, Any]]] = {}
        for c in diff["cell_changes"]:
            by_role.setdefault(c["work_role_code"], []).append(c)
        for code in sorted(by_role):
            role_changes = by_role[code]
            name = role_changes[0]["work_role_name"]
            lines.append(f"### ({code}) {name}")
            lines.append("")
            # Order cells: basic, intermediate, advanced
            level_order = {"basic": 0, "intermediate": 1, "advanced": 2}
            for c in sorted(role_changes, key=lambda x: level_order.get(x["proficiency_level"], 99)):
                label = f"{c['qualification_type'].capitalize()} / {c['proficiency_level'].capitalize()}"
                lines.append(f"**{label}**")
                if c["added"]:
                    lines.append(f"- Added: {', '.join(c['added'])}")
                if c["removed"]:
                    lines.append(f"- Removed: {', '.join(c['removed'])}")
                lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# Work roles that exist in DoD 8140 V2.1 but have no certification options
# published (pending DoD review). Historically tracked by Jeff with blank cert
# cells in the Jan 2025 version. They look "removed" in the structured diff
# because the V2.1 Certification Repository has zero rows for them.
PENDING_REVIEW_ROLES = ["462", "731", "901"]


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/diff.json")
    out = Path("8140/CHANGELOG.md")
    out.parent.mkdir(exist_ok=True)
    diff = json.loads(src.read_text(encoding="utf-8"))
    out.write_text(
        render(diff, known_gap_roles=PENDING_REVIEW_ROLES),
        encoding="utf-8",
    )
    print(f"wrote {out}")
