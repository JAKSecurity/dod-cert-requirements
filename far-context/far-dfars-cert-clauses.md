# Why this repo still carries the DoD 8570 reference list

> **Not legal advice.** This document summarizes publicly available contract-clause text as one practitioner's reading. It is not written by a lawyer, a Contracting Officer, or a COR, and it is not a complete legal analysis. If you are making a contract qualification determination, consult your KO, legal counsel, or the issuing agency.

## The short answer

DoD 8570.01-M has been superseded as **DoD policy** (replaced by DoDM 8140.03 on 15 Feb 2023), but it has not been superseded in the **contract clause** that binds DoD contractors to cyber workforce qualification requirements. That clause — DFARS 252.239-7001 — still references 8570.01-M by name.

So contractors can end up in a situation where their contract requires compliance with an explicitly retired DoD manual. The authoritative 8570 list once lived at `public.cyber.mil/wid/cwmp/dod-approved-8570-baseline-certifications/`; DoD removed that page during the 8140 transition. **That's why this repo preserves a reference copy of the retired 8570 baseline list.** A KO, COR, or contractor compliance team that needs to cite 8570 still has somewhere to cite.

## The evidence

### DFARS 252.239-7001 — Information Assurance Contractor Training and Certification

- **Last updated:** 2025-11-10
- **Authoritative text:** [acquisition.gov/dfars/252.239-7001](https://www.acquisition.gov/dfars/252.239-7001-information-assurance-contractor-training-and-certification.)

Paragraph (a), quoted in full as of the 2025-11-10 revision:

> The Contractor shall ensure that personnel accessing information systems have the proper and current information assurance certification to perform information assurance functions in accordance with DoD 8570.01-M, Information Assurance Workforce Improvement Program.

The reference to **DoD 8570.01-M** is not incidental — it is the clause's substantive qualification mandate. The 2025-11-10 revision did not update this reference to DoDM 8140.03.

### DoD's own transition guidance

From the DoD 8140 program's public transition materials:

> The DoD 8570 and DoD 8140 programs are not structured the same and there is no "crosswalk" of qualifications between them.

A contractor cannot mechanically translate "Security+ under 8570" into "Security+ satisfies work role X at proficiency Y under 8140" without referencing the current DoD 8140 qualification matrix. And a Contracting Officer reading a contract that says "comply with DoD 8570.01-M" cannot wave it away as out-of-date when the very DFARS clause that carries the requirement names 8570.01-M in its latest revision.

## Implications

- **For Contracting Officers and CORs:** the clause as currently written is the clause in force. Until DFARS 252.239-7001 is revised to reference 8140, or until a specific contract is modified, existing contract language governs.
- **For contractors:** many contracts have copy-pasted 8570-specific language (cert lists, workforce categories) into their statements of work rather than incorporating DFARS 252.239-7001 by reference. In those contracts, the 8570 list persists contractually until the SOW itself is amended — regardless of what the DFARS clause says.
- **For program managers overseeing mixed populations:** DoD civilians and military service members are governed by DoDM 8140.03 on the DoD CIO's implementation timeline (cybersecurity element by 15 Feb 2025; IT, cyber effects, intelligence, and cyber enablers by 15 Feb 2026). Contractors on the same program are governed by their contract language — which may not have been updated to match.

## Why this repo keeps an 8570 reference copy

When the authoritative list moved behind the 8140 transition and the 8570 page was removed from cyber.mil, the practical need to cite the 8570 baseline list did not disappear. This repo preserves a reference copy — reconstructed from the last publicly-archived snapshot of the DoD page before removal — so that anyone managing a contract that still names 8570 has an authoritative source to cite.

## Suggested reading

- **DFARS 252.239-7001** (current text): [acquisition.gov/dfars/252.239-7001](https://www.acquisition.gov/dfars/252.239-7001-information-assurance-contractor-training-and-certification.)
- **DoDM 8140.03** (current policy): [DoD CIO Library](https://dodcio.defense.gov/Portals/0/Documents/Library/DoDM-8140-03.pdf)
- **DoD 8140 Qualification Matrices** (current qualification reference): [cyber.mil/dod8140/qualification-matrices](https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices)
- **DoD 8140 implementation timeline**: [dodcio.defense.gov](https://dodcio.defense.gov/Portals/0/Documents/Cyber/DoD8140-ImplementationTimeline.pdf)
- **Archived 8570 baseline reference** (this repo): see `8570/8570-baseline-reference.pdf`

---

**Compiled by Jeff Krueger.** Unaffiliated with any firm, agency, or contracting office. Not legal advice.
