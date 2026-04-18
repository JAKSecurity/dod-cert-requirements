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


def render(diff: dict[str, Any], refresh_date: str | None = None) -> str:
    refresh_date = refresh_date or date.today().isoformat()
    lines = [
        f"# 8140 Matrix Changelog — refreshed {refresh_date}",
        "",
        "This document summarizes how the current DoD 8140 Foundational Qualification Matrix (V2.1, effective 2025-09-19) differs from the Jan 2025 private working version that served as this repo's starting point. It is informational — the refreshed xlsx published in this repo is generated directly from V2.1 source data, not patched from the Jan 2025 version.",
        "",
        "Scope: certification-path qualifications only. Other qualification paths (education, DoD training, commercial training, experience alternatives) are out of scope for this repo and therefore not diffed.",
        "",
    ]

    total = len(diff["added_roles"]) + len(diff["removed_roles"]) + len(diff["cell_changes"])
    if total == 0:
        lines.append("No changes detected against V2.1 source.")
        return "\n".join(lines) + "\n"

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Work roles added in V2.1:** {len(diff['added_roles'])}")
    lines.append(f"- **Work roles removed since Jan 2025:** {len(diff['removed_roles'])}")
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

    if diff["removed_roles"]:
        lines.append("## Work roles not in V2.1")
        lines.append("")
        lines.append("These work roles existed in the Jan 2025 version but do not appear in the V2.1 Certification Repository. They may have been renamed, merged, or moved to a non-certification qualification path.")
        lines.append("")
        for r in diff["removed_roles"]:
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


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/diff.json")
    out = Path("8140/CHANGELOG.md")
    out.parent.mkdir(exist_ok=True)
    diff = json.loads(src.read_text(encoding="utf-8"))
    out.write_text(render(diff), encoding="utf-8")
    print(f"wrote {out}")
