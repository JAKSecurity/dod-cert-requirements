# FAR/DFARS Research Scoping — 2026-04

**Purpose:** Internal note documenting initial research scope for `far-dfars-cert-clauses.md`. Jeff reviews and approves depth + structure before the public-facing document is drafted.

## Primary finding

**DFARS 252.239-7001 (Information Assurance Contractor Training and Certification) — current text as of 2025-11-10 — still references DoD 8570.01-M by name**, not DoDM 8140.03.

Paragraph (a) quote: *"The Contractor shall ensure that personnel accessing information systems have the proper and current information assurance certification to perform information assurance functions in accordance with DoD 8570.01-M, Information Assurance Workforce Improvement Program."*

This is the core evidence for the dilemma the page is framing. DoDM 8140.03 has been policy since 2023-02-15; the DFARS clause governing contractor qualification was updated as recently as 2025-11-10 without changing the 8570.01-M reference.

**Authoritative URL:** `https://www.acquisition.gov/dfars/252.239-7001-information-assurance-contractor-training-and-certification.`

## Clauses found / clauses checked

| Clause | Title | Status | Last updated | Notes |
|--------|-------|--------|--------------|-------|
| DFARS 252.239-7001 | Information Assurance Contractor Training and Certification | **Still references 8570.01-M** | 2025-11-10 | Primary clause for this project's dilemma. Unchanged reference to 8570 despite 2025-11 update. |
| DFARS Subpart 239.71 | Security and Privacy for Computer Systems | Container for the above clause | - | Prescribes when 252.239-7001 is included in contracts. |
| FAR 52.204-21 | Basic Safeguarding of Covered Contractor Information Systems | Not relevant | - | Does not address workforce qualification. Out of scope. |
| DoDM 8140.03 | Cyberspace Workforce Qualification and Management Program | Current policy | 2023-02-15 | Policy authority that replaced 8570.01-M. |

Not yet investigated:
- Agency-specific supplements (AFARS, NMCARS, AFFARS) — likely propagate the DFARS language; worth a quick scan.
- Any open **DFARS Case** proposing to update 252.239-7001 to reference 8140 — status unknown; worth one more search.
- Contractor-applicability language within DoDM 8140.03 itself — the manual speaks of "all DoD personnel in cyberspace-related roles, including... contractors," but enforcement for contractors still runs through the contract clause.

## Contextual pieces worth citing in the final document

- **"There is no crosswalk of qualifications between [8570 and 8140]"** — DoD's own transition guidance (`dl.dod.cyber.mil/wp-content/uploads/8140/pdf/unclass-dod8570_ia_program_transition_dod8140_cwp.pdf`). This is quotable and sharpens the dilemma: a contracting officer can't mechanically translate "Security+" under 8570 to "Security+ satisfies work role X at proficiency Y" under 8140 without referencing the V2.1 matrix.
- **DoDM 8140.03 implementation timelines apply to DoD civilians and military service members.** Feb 15, 2025 (cybersecurity element) and Feb 15, 2026 (cyber IT, effects, intel, enablers elements). Contractor qualification is governed by contract language, not these timelines.
- **DFARS rewrite tempo.** DFARS 252.239-7001 was touched 2025-11-10 but the 8570 reference was not updated. This tells us the clause-update machinery is aware of the manual's existence but has not prioritized the textual swap, for reasons not publicly documented. The dilemma section of the final doc should note this without speculating about intent.

## Proposed depth for the public-facing doc

**Medium.** Per the design spec. Specifically:

- CYA front matter (not legal advice, not a KO/COR, public-document sources only)
- One-table summary of relevant clauses with status
- Focused clause-by-clause notes for **DFARS 252.239-7001** (primary) and a brief "also considered and ruled out" note for FAR 52.204-21
- Dilemma section (~300-400 words): what the clause says, what policy says, the contract-language implications for KOs and PMs working a legacy contract whose SOW copy-pasted 8570 language
- "Suggested reading" pointers to DoDM 8140.03 itself, the DoD 8140 transition bulletin, and the DFARS clause's acquisition.gov page

**Explicitly NOT doing:**
- No specific contract-language samples from SAM.gov (that's option (c) from the brainstorm; we settled on medium depth, not deep).
- No legal opinion on how KOs should resolve the conflict. We name the conflict; Jeff's voice stays agnostic.
- No prediction of when DFARS 252.239-7001 will be updated. Not speculating.

## Proposed structure for the final doc

```
far-context/far-dfars-cert-clauses.md
├── Title + CYA disclaimer
├── Why this document exists (one paragraph)
├── Summary: the gap (one paragraph)
├── Clauses — Summary table
├── DFARS 252.239-7001 — detailed notes
│   ├── What it says (with quoted paragraph)
│   ├── What it means in practice
│   └── Status vs. current DoD policy
├── Also considered (FAR 52.204-21)
├── The dilemma — for KOs and PMs
├── Suggested reading
└── Version line (compiled YYYY-MM-DD by Jeff Krueger)
```

## Request for Jeff's approval

Before I draft the public-facing document, please confirm:

1. **Scope is medium** (not deep — no SAM.gov samples, no legal opinion)? Y / N
2. **Primary clause is DFARS 252.239-7001**, with FAR 52.204-21 noted-and-dismissed? Y / N
3. **Dilemma framing: evidence-only, no intent speculation**? Y / N
4. **Should I also investigate agency supplements (AFARS, NMCARS, AFFARS)** and any open DFARS Case for 252.239-7001, before drafting? Or are those nice-to-haves you're willing to defer? Y / N / Y-but-brief
