# 2. Evidence of Relevance

This section separates three kinds of evidence: findings from published sources, assumptions that still need to be checked, and the plan for collecting evidence from users.

## 2.1 Evidence from published sources

| ID | Finding | Source |
|---|---|---|
| E1 | UAVs are widely used in SAR. Open challenges include data processing, small-object detection and operation under limited resources. | [9] |
| E2 | Automated person detection in UAV imagery has contributed to locating a missing person in a real operation. | [8] |
| E3 | People in aerial SAR imagery are small objects. Detectors fine-tuned on SAR data perform better than general-purpose detectors. | [1], [2] |
| E4 | Thermal imagery is useful for detecting people, but it has lower resolution and fewer public datasets than RGB imagery. | [4], [5], [6] |
| E5 | YOLO-based detectors adapted for small objects can run in real time on embedded hardware. | [10] |

These sources show that the general problem is real and actively studied. They do not show what users in Kazakhstan specifically need, which equipment they use or how they currently work. That gap is covered in Sections 2.2 and 2.3.

## 2.2 Assumptions that require validation

| ID | Assumption (hypothesis) | Requirements affected |
|---|---|---|
| H1 | UAV footage is currently reviewed manually, and this takes a significant amount of time. | Project aim |
| H2 | Reliable internet access is often unavailable in the field, so processing must run locally. | NFR-3 |
| H3 | Missing a person is considered worse than receiving false alarms, so recall should be prioritised over precision. | FR-1, FR-8 |
| H4 | Teams use UAVs that record GPS position, altitude and camera orientation in a usable format. | FR-4 |
| H5 | Coordinates are most useful as a map point or a file that opens in common mapping tools. | FR-7 |

Until they are validated, these assumptions are treated as provisional, and the requirements that depend on them may change.

## 2.3 User research plan and status

**Status:** user discussions have not yet been conducted as of the date of this document. No results are reported here.

**Plan.** The team plans to hold 3–5 semi-structured discussions (about 20–30 minutes each, in person or online) with:

- UAV operators or rescuers from emergency services (for example, regional emergency departments);
- members of volunteer search teams;
- UAV pilots who carry out thermal or aerial survey work.

The question guide is given in Appendix A. For each discussion, the team will record the respondent's role (without personal data unless consent is given), the date, the main answers and which hypotheses were supported or contradicted. Notes will be stored in the repository under `docs/interviews/`.

**How findings will be used.** Each hypothesis H1–H5 will be marked as supported, contradicted or unclear. Requirements linked to a contradicted hypothesis will be revised. For example, if users report that coordinates are always passed by voice radio, the export format in FR-7 would be reconsidered.
