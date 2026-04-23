> **Not legal advice.** This is one practitioner's reading of publicly available contract-clause text. Consult your KO, legal counsel, or the issuing agency for qualification determinations.

## The core issue

DoD 8570.01-M was superseded as **DoD policy** by DoDM 8140.03 on 15 Feb 2023. But it has not been superseded in the **contract clause** that binds DoD contractors to cyber workforce qualification requirements. DFARS 252.239-7001 (last revised 2025-11-10) still references 8570.01-M by name:

> The Contractor shall ensure that personnel accessing information systems have the proper and current information assurance certification to perform information assurance functions in accordance with DoD 8570.01-M, Information Assurance Workforce Improvement Program.

The 2025-11-10 revision did not update that reference. And since the DoD removed the authoritative 8570 page from `public.cyber.mil` during the 8140 transition, contractors needing to cite the 8570 baseline list were left with no canonical source. That's why this repo keeps a reference copy, reconstructed from the last publicly-archived snapshot of the page before removal.

## Why a mechanical translation doesn't work

DoD's own 8140 transition guidance is explicit:

> The DoD 8570 and DoD 8140 programs are not structured the same and there is no "crosswalk" of qualifications between them.

The 8570 workforce model had four broad categories: IAT, IAM, IASAE, and CSSP. An IAT-II technician might have qualified with Security+, and that Security+ satisfied the contract requirement.

DoDM 8140.03 replaces those four categories with roughly 70 specific work roles. The person previously coded as IAT-II may now be coded as (621) Software Developer and (632) Systems Developer. Security+ does not qualify either of those roles under 8140.

Contractors carrying an 8570-era cert portfolio into the 8140 world cannot assume their people are still qualified. They need the current 8140 qualification matrix to see which certs satisfy which work roles at which proficiency levels.

But a Contracting Officer reading a contract that says "comply with DoD 8570.01-M" cannot wave it away as out-of-date. The DFARS clause carrying the requirement still names 8570.01-M in its latest revision.

## What this means in practice

**For Contracting Officers and CORs.** The clause as currently written is the clause in force. Until DFARS 252.239-7001 is revised to reference 8140, or until a specific contract is modified, existing contract language governs.

**For contractors.** Many contracts copy-pasted 8570-specific language (cert lists, workforce categories) into their statements of work rather than incorporating DFARS 252.239-7001 by reference. In those contracts, the 8570 list persists contractually until the SOW itself is amended, regardless of what the DFARS clause says.

**For program managers with mixed populations.** DoD civilians and military service members are governed by DoDM 8140.03 on the DoD CIO's implementation timeline: cybersecurity element by 15 Feb 2025; IT, cyber effects, intelligence, and cyber enablers by 15 Feb 2026. Contractors on the same program are governed by their contract language, which may not have been updated to match.

## Authoritative sources

- **DFARS 252.239-7001** (current text): [acquisition.gov/dfars/252.239-7001](https://www.acquisition.gov/dfars/252.239-7001-information-assurance-contractor-training-and-certification.)
- **DoDM 8140.03** (current policy): [DoD CIO Library](https://dodcio.defense.gov/Portals/0/Documents/Library/DoDM-8140-03.pdf)
- **DoD 8140 Qualification Matrices**: [cyber.mil/dod8140/qualification-matrices](https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices)
- **DoD 8140 implementation timeline**: [dodcio.defense.gov](https://dodcio.defense.gov/Portals/0/Documents/Cyber/DoD8140-ImplementationTimeline.pdf)
- **Archived 8570 baseline reference**: [web.archive.org snapshot (2024-01-30) of the original cyber.mil page](https://web.archive.org/web/20240130000000*/public.cyber.mil/wid/dod-approved-8570-baseline-certifications/)
