"""Canonical JSON schema for 8140 matrix records."""
from dataclasses import dataclass, field
from typing import Any

VALID_QUALIFICATION_TYPES = {"education", "certification"}
VALID_PROFICIENCY_LEVELS = {"basic", "intermediate", "advanced"}


@dataclass
class MatrixRecord:
    work_role_code: str
    work_role_name: str
    qualification_type: str
    proficiency_level: str
    certs: list[str] = field(default_factory=list)

    def to_canonical(self) -> dict[str, Any]:
        return {
            "work_role_code": self.work_role_code,
            "work_role_name": self.work_role_name,
            "qualification_type": self.qualification_type,
            "proficiency_level": self.proficiency_level,
            "certs": sorted(self.certs),
        }


def validate_matrix(records: list[dict[str, Any]]) -> None:
    for i, r in enumerate(records):
        if r["qualification_type"] not in VALID_QUALIFICATION_TYPES:
            raise ValueError(
                f"record {i}: qualification_type {r['qualification_type']!r} invalid"
            )
        if r["proficiency_level"] not in VALID_PROFICIENCY_LEVELS:
            raise ValueError(
                f"record {i}: proficiency_level {r['proficiency_level']!r} invalid"
            )
