# 2. Evidence of Relevance

The evidence for this stage comes from an analysis of available data: peer-reviewed studies, official statistics and public reports from Kazakhstan's emergency services, and documented search cases. All of it is secondary evidence. No interviews or discussions with users have been conducted so far, and this section does not report any. Findings are kept separate from the assumptions that remain unverified.

## 2.1 Scale of the problem in Kazakhstan

In January 2024, the Prosecutor General's Office reported that 2,098 people were registered as missing in Kazakhstan, out of 10,178 people on the wanted list. Most of them (1,572) had left home and not returned [21]. Not every missing-person case involves an area search, but the figure shows that searches for people are a regular task for police and rescue services.

Kazakhstan's Ministry of Emergency Situations (MES) describes searches in steppe, forest and mountain areas as complicated by "long distances, darkness and hard-to-reach terrain" [23]. It also stresses that in such operations "every minute counts" [22].

## 2.2 Current use of drones in search operations

| ID | Finding | Source |
|---|---|---|
| E1 | The MES operated 134 drones in May 2025 and 242 in October 2026. In 2026, drones were used in about 5,000 operations and contributed to 28 rescues. | [22], [23] |
| E2 | Thermal cameras are used to find people at night, in smoke and in dense vegetation. | [22], [23] |
| E3 | 187 of the MES drones have AI functions that recognise people, vehicles and boats and alert the operator. | [23] |
| E4 | Drones are also used outside the MES. In a 2025 search in East Kazakhstan, police used a thermal drone, and the operator passed coordinates to ground teams. | [24] |
| E5 | Practice in European emergency services recommends two people per aircraft: one to pilot and one to analyse the video. Reviewing footage is a separate task. | [25] |

## 2.3 Evidence on manual review of aerial images

The most direct evidence comes from a study that compared people with a detection algorithm on the same SAR aerial images [20]:

- Without algorithm support, participants found 66% of the people in the images (precision 53%). With support, they found 72% (precision 46%).
- With support, inspection took on average 30% less time (1,110 s versus 1,495 s).
- The algorithm alone reached about 90% recall, but with many false alarms.
- The authors note that operator attention drops over hundreds of images, which increases the chance of missing someone.
- People missed by the algorithm were also detected less often by participants who relied on it. One such person was found by 19% of supported participants, compared with 44% of unsupported ones.

These results support the idea that automated detection helps operators, but they also show a risk: the operator may trust the algorithm too much. For this reason, SAR-Vision presents detections for review instead of filtering images automatically (FR-5, FR-6). The other studies in the literature review confirm that people in aerial SAR images are small objects and that specialised training improves detection [1], [2], [10].

## 2.4 Assumptions and their status

| ID | Assumption | Status after data analysis | Evidence | Requirements affected |
|---|---|---|---|---|
| H1 | Manual review of UAV images is slow and people are missed | Supported | [20], [25] | Project aim |
| H2 | Internet access is often unavailable in the field, so processing must run locally | Partly supported: search areas are remote and hard to reach, but no source reports connectivity directly | [22], [23] | NFR-3 |
| H3 | Missing a person is worse than a false alarm, so recall has priority | Supported by the study design and results; not confirmed by users | [20] | FR-1, FR-8 |
| H4 | Teams use UAVs that record position, altitude and camera orientation | Not verified: the drone models used by the MES and police are not stated in the sources | — | FR-4 |
| H5 | Coordinates are needed in a form that can be passed to ground teams | Supported: operators pass coordinates to ground teams | [24] | FR-7 |

## 2.5 Implications for the project

1. **The problem is real and current in Kazakhstan.** Drones are widely used in searches, and manual review is a known weak point (H1).
2. **AI-assisted detection is already used by the MES on part of its fleet** (E3). SAR-Vision is therefore not positioned as a replacement for these systems. Its intended users are teams without AI-equipped enterprise drones, such as police units, volunteer search teams and regional units using standard drones. It also supports post-flight review of recorded footage independently of the drone manufacturer.
3. **The operator must stay in the loop.** Evidence of over-reliance on algorithms [20] supports the confirm/reject workflow and showing all detections rather than hiding images.

## 2.6 Limitations

This evidence is secondary. The figures from the MES are the ministry's own reported statistics, and news reports describe individual cases. The study in [20] was conducted in Croatia. No discussions with users in Kazakhstan have been held, so H2 and H4 remain open, and the needs of police units or volunteer teams have not been confirmed directly. Discussions with practitioners remain planned for the next stage. If they take place, their results will be added to this section and the requirements will be updated.
