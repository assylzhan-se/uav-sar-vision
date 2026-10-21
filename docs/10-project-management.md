# 10. Project Management and Risks

## 10.1 Team and responsibilities

Responsibilities follow the task assignment in YouTrack and may be adjusted as the project develops. Each member is responsible for their own commits, pull requests and YouTrack tasks.

| Member | Main responsibility | Further tasks |
|---|---|---|
| Kurmantaev Ali (Құрмантаев Әли Романұлы) | Literature review (SAR-4), technology comparison (SAR-6) | Interface mockups (SAR-9), geolocation module (SAR-11) |
| Shalmanov Assylzhan (Шалманов Асылжан Саясатұлы) | Repository and README (SAR-1), proposal (SAR-2), requirements (SAR-7) | Existing system comparison (SAR-5), detection demo (SAR-13) |
| Shakalova Diana (Шакалова Диана Аскаровна) | User research (SAR-3), verification plan (SAR-10) | Architecture diagrams (SAR-8), project plan and supervisor feedback (SAR-12) |

Supervisor: Kutpanova Zarina.

## 10.2 Repository and task tracking

**Repository.** A GitHub repository will contain source code, documentation, diagrams (PlantUML sources and PNG exports), prototype materials, tests and configuration examples. The planned structure is:

```
README.md        docs/          diagrams/src, diagrams/png
prototype/       src/           tests/
config/          requirements.txt   .gitignore
```

The README will include the project description, problem, users, team and responsibilities, supervisor, scope, status, technologies, links to YouTrack and the documentation, and setup and test instructions. Secrets and operation data are excluded through `.gitignore`; only example configuration files with placeholder values are committed.

Repository: https://github.com/assylzhan-se/uav-sar-vision. YouTrack: https://sarvision.youtrack.cloud/projects/SAR.

**Workflow.** The `main` branch holds reviewed work. Each change is linked to a YouTrack task:

- branch: `SAR-7-requirements`
- commit message: `SAR-7: Add requirements and acceptance criteria`
- pull request: describes the change, references the task and explains how the change was checked

Another team member reviews each pull request before it is merged. The task in YouTrack links back to the pull request and is closed only when its acceptance criterion is met. Each pre-defense submission is marked with a Git tag (`pre-defense-1`, `pre-defense-2`, `final-pre-defense`). Tags are not moved after submission.

**Contribution evidence.** The committee will assess each member's individual contribution through commit history, pull requests and reviews. At the time of writing, this history has not yet been created. The documents in this submission should be committed by their respective authors through separate pull requests, not uploaded in a single commit.

## 10.3 Tasks for the first pre-defense

The following tasks are recorded in YouTrack (project key SAR).

| ID | Task | Assignee | Acceptance criterion | Priority |
|---|---|---|---|---|
| SAR-1 | Repository structure, README, `.gitignore` | Shalmanov | All README sections present | Critical |
| SAR-2 | Project proposal and scope | Shalmanov | Section 1 reviewed by the supervisor | Critical |
| SAR-3 | User discussions (3–5) | Shakalova | Notes for each discussion stored in `docs/interviews/` | Critical |
| SAR-4 | Literature review | Kurmantaev | ≥ 12 sources, ≥ 8 scientific | Critical |
| SAR-5 | Existing system comparison | Shalmanov | 3–5 systems, 6–10 criteria, sources cited | Major |
| SAR-6 | Technology comparison | Kurmantaev | ≥ 3 decisions with 2–3 alternatives each | Major |
| SAR-7 | Requirements and acceptance criteria | Shalmanov | Every requirement has a priority and a test | Critical |
| SAR-8 | Context, use case and component diagrams | Shakalova | `.puml` sources and PNG exports committed | Critical |
| SAR-9 | Interface mockups | Kurmantaev | Three screens covering UC-1 to UC-5 | Major |
| SAR-10 | Verification and evaluation plan | Shakalova | Metrics, baselines and tests defined | Major |
| SAR-11 | Draft geolocation module and unit tests | Kurmantaev | `pytest` passes | Normal |
| SAR-12 | Project management, supervisor review, full document | Shakalova | Feedback recorded in Section 11 | Critical |
| SAR-13 | Baseline detection demo script | Shalmanov | Script draws person boxes on a test image | Normal |

## 10.4 Milestones

The dates after the first pre-defense are proposed targets and depend on the official schedule.

| Milestone | Target | Main result |
|---|---|---|
| M1 Analysis and design | 24 October 2026 (pre-defense 1) | This document, diagrams, mockups, repository and task board |
| M2 Data and baseline | November 2026 | Prepared datasets; baseline B1 evaluated; first fine-tuned model |
| M3 Processing pipeline | December 2026 | Images/video, detection, geolocation and storage working from the command line |
| M4 MVP with interface | Pre-defense 2 (date to be announced) | Operator interface, review and export; first metrics |
| M5 Evaluation and extensions | February–March 2027 | Tests T-1 to T-10; extensions if time allows |
| M6 Final version | Final pre-defense (date to be announced) | Complete system and thesis |

## 10.5 Risks

| ID | Risk | Likelihood | Impact | Mitigation | Fallback |
|---|---|---|---|---|---|
| R1 | No access to a UAV with telemetry for field tests | High | High | Ask the university, emergency services and commercial pilots early | Evaluate on public datasets and recorded footage; report geolocation as untested |
| R2 | Not enough GPU capacity for training | Medium | High | Use small and medium models; free cloud notebooks for training | Reduce image size or number of experiments |
| R3 | Detection quality below target | Medium | Medium | Staged transfer learning, tiling, threshold tuning | Report the achieved results honestly and analyse the causes |
| R4 | Live video cannot be obtained from the UAV controller | Medium | Low (extension) | Check the options for the specific UAV model | Process recorded footage after landing (MVP) |
| R5 | Telemetry is missing or inaccurate | Medium | Medium | Confirm the metadata format with sample files early | Show detections without coordinates; report the error sources |
| R6 | User discussions cannot be arranged | Medium | High | Contact several organisations in parallel | Short online questionnaire and expert discussions |
| R7 | Team workload and missed deadlines | Medium | Medium | Weekly check-ins; tasks with deadlines in YouTrack | Drop *could* requirements first |
| R8 | Flight restrictions | Medium | Medium | Fly only at permitted sites with a licensed pilot | Use existing recordings |

## 10.6 Dependencies and next steps

Several parts of the plan depend on earlier steps:

- The telemetry parser and geolocation tests depend on knowing which UAV model and file format users have (SAR-3, R1, R5).
- Model training depends on dataset preparation and GPU access (R2).
- The interface depends on the API contract in Section 8.2.

The next steps after the first pre-defense are:

1. Hold the user discussions and update the requirements.
2. Download and convert the datasets.
3. Evaluate baseline B1.
4. Start fine-tuning.
