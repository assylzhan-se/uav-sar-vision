# 1. Project Proposal

## 1.1 Project information

| Item | Details |
|---|---|
| Title | Development of a Machine Vision System for Searching for Victims in Emergency Situations Using an Unmanned Aerial Vehicle |
| Title (Russian) | Разработка системы технического зрения для поиска пострадавших в чрезвычайных ситуациях с применением беспилотного летательного аппарата |
| Project name | SAR-Vision (Search and Rescue Vision) |
| Team | Kurmantaev Ali, Shalmanov Assylzhan, Shakalova Diana |
| Supervisor | Kutpanova Zarina |
| Stage | First probationary period (analysis and design) |

## 1.2 Project materials

All materials below correspond to the repository version tagged `prob-period-1`.

| Material | Link |
|---|---|
| Repository | https://github.com/assylzhan-se/uav-sar-vision |
| Tagged version | https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1 |
| Task tracking (YouTrack) | https://sarvision.youtrack.cloud/projects/SAR |
| Prototype (interface mockups: HTML source and PNG) | https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1/prototype |
| Editable diagram sources (PlantUML) | https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1/diagrams/src |
| Exported diagrams (PNG) | https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1/diagrams/png |
| Documentation (Markdown sources of all sections) | https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1/docs |
| Draft geolocation module and unit tests | https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1/src/sar_vision and https://github.com/assylzhan-se/uav-sar-vision/tree/prob-period-1/tests |

## 1.3 Problem statement

Unmanned aerial vehicles (UAVs) are increasingly used in search and rescue (SAR) operations because they can cover large or hard-to-reach areas quickly [9]. However, the footage they collect is usually reviewed by a human operator. This is difficult for several reasons:

- At typical survey altitudes, a person may occupy only a few dozen pixels in an image, so they are easy to miss [1], [2].
- A single flight can produce hundreds of photographs or a long video. Reviewing it takes time and the operator's attention decreases over a long session.
- In poor lighting or partial vegetation cover, people are harder to see in visible-light (RGB) imagery. Thermal imagery can help in these conditions but has its own limitations [4], [6].
- After a possible person is spotted, the operator still needs to estimate where that point is on the ground so that a ground team can be sent.

In Kazakhstan, 2,098 people were registered as missing in early 2024 [21], and the Ministry of Emergency Situations used drones in about 5,000 operations in 2026 [23]. Published work shows that automated person detection can support this process. For example, the SARUAV system contributed to locating a missing person during a real operation in Poland [8]. At the same time, detecting very small objects, limiting false alarms and processing data quickly on field hardware remain open problems [9], [10].

## 1.4 Target users

| User | Need |
|---|---|
| UAV operator in a police unit, volunteer search team or regional rescue unit that uses standard drones without built-in AI detection | Be alerted to possible people in the footage instead of reviewing every frame manually |
| Search coordinator | See reviewed detections on a map and pass locations to ground teams |
| Ground search team (indirect user) | Receive approximate coordinates of a location to check |

These user groups are based on the literature and on public reports from Kazakhstan (Section 2). The Ministry of Emergency Situations already has AI-equipped drones on part of its fleet [23], so the project focuses on teams without such equipment and on vendor-independent review of recorded footage. The user groups have not yet been validated in discussions with users.

## 1.5 Aim and objectives

**Aim.** To develop a machine vision system that helps a UAV operator find possible victims in aerial imagery by automatically detecting people, estimating their approximate ground coordinates and presenting the results for human review.

The system is a decision-support tool. It does not replace rescuers and does not make rescue decisions on its own; every detection must be reviewed by an operator.

**Objectives:**

1. Review existing research, datasets and systems for person detection in UAV imagery.
2. Validate the main assumptions about user needs through discussions with practitioners.
3. Prepare training and test data from public SAR datasets.
4. Train and evaluate a person detection model for RGB imagery and compare it with a baseline.
5. Implement estimation of a detection's ground coordinates from UAV telemetry.
6. Build an operator interface for reviewing, confirming or rejecting detections and exporting confirmed locations.
7. Evaluate the system against the metrics in Section 9.

## 1.6 Scope

The full set of features we would like to support (RGB and thermal imagery, live video, offline maps, geolocation, operator review and export) is too large to build at once. We therefore define a minimum viable product (MVP) and treat the remaining features as extensions.

| Category | Features |
|---|---|
| MVP (first version) | Person detection in RGB images and recorded video; small-object handling by image tiling; approximate geolocation for a downward-facing (nadir) camera over flat terrain; operator interface with a detection list and map; confirm/reject; CSV/KML export; local operation on a laptop without internet access |
| Planned extensions (if time allows) | Live video stream input (RTSP); separate thermal detection model; tracking to merge repeated detections of the same person; geolocation for tilted cameras |
| Out of scope | Building or modifying a UAV, flight control or route planning; onboard (in-flight) processing; identification of individuals; assessment of a person's medical condition; certification for operational use |

The main dependency for field testing is access to a UAV that records telemetry (for example, a DJI enterprise model). If access is not available, evaluation will rely on public datasets and recorded footage (see risk R1 in Section 10).

## 1.7 Expected outcomes

- A person detection model fine-tuned on public SAR datasets, with results reported against the targets and baseline in Section 9.
- A processing pipeline that takes images or video with telemetry and produces geolocated detections.
- A web-based operator interface for reviewing and exporting detections.
- An evaluation report covering detection quality, processing speed and geolocation error.

The expected technical contribution is not a new detection algorithm. It is the integration of an existing detector, small-object techniques, telemetry-based geolocation and a human review workflow into one tool that runs locally, together with an evaluation of how well this combination works.

## 1.8 Engineering complexity

The project involves several non-trivial engineering problems:

- Detecting small objects in high-resolution frames, which requires tiling and fine-tuning rather than an off-the-shelf model [10], [11].
- Balancing detection quality against processing speed on a laptop GPU.
- Converting pixel positions into geographic coordinates using camera parameters and telemetry, and estimating the resulting error.
- Synchronising video frames with telemetry records.
- Integrating several components (input, inference, geolocation, storage, user interface) into a system that a non-specialist can operate.
