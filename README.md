# SAR-Vision: Machine Vision for UAV-Based Search and Rescue

**Diploma project:** Development of a Machine Vision System for Searching for Victims in Emergency Situations Using an Unmanned Aerial Vehicle
(*Разработка системы технического зрения для поиска пострадавших в чрезвычайных ситуациях с применением беспилотного летательного аппарата*)

SAR-Vision is a decision-support tool for UAV operators. It is designed to detect possible people in aerial images and video, estimate their approximate ground coordinates from UAV telemetry, and present the results to an operator for confirmation. It runs locally on a laptop without internet access. The system does not make rescue decisions: every detection is reviewed by a person.

## Problem

People in UAV imagery are often tiny, and reviewing hundreds of photos or long videos manually is slow and tiring. Once a possible person is found, the operator still has to work out where that point is on the ground. See [docs/01-proposal.md](docs/01-proposal.md).

## Target users

- UAV operators in rescue units and volunteer search teams
- Search coordinators
- Ground search teams (indirect users who receive the coordinates)

## Expected outcomes

- A person detection model fine-tuned on public SAR datasets, evaluated against a baseline
- A processing pipeline that turns images or video with telemetry into geolocated detections
- A browser-based operator interface for review and CSV/KML export
- An evaluation of detection quality, throughput and geolocation error

## Team

| Member | Responsibility (YouTrack tasks) |
|---|---|
| Kurmantaev Ali | Literature review, technology comparison, interface mockups, geolocation module |
| Shalmanov Assylzhan | Repository and README, proposal, requirements, existing system comparison, detection demo |
| Shakalova Diana | User research, verification plan, architecture diagrams, project plan and supervisor feedback |

**Supervisor:** Kutpanova Zarina

## Scope

**MVP:** RGB person detection in images and recorded video, tiling for small objects, geolocation for a nadir camera, review interface, CSV/KML export, offline operation.
**Extensions:** live stream input, thermal model, tracking, tilted-camera geolocation.
**Out of scope:** UAV hardware, flight control, onboard processing, identification of individuals.

## Current status

Stage 1: analysis and design (first pre-defense, 24 October 2026).

| Done | In progress | Next |
|---|---|---|
| Proposal, literature review, system and technology comparisons, requirements, diagrams, mockups, verification plan, draft geolocation module with unit tests | User discussions, supervisor review | Dataset preparation, baseline evaluation |

## Technologies (provisional)

Python, PyTorch, Ultralytics YOLO, SAHI, OpenCV, FastAPI, WebSocket, SQLite, Leaflet, React or Vue (undecided), PlantUML. See [docs/05-technology-comparison.md](docs/05-technology-comparison.md).

## Links

- YouTrack: https://sarvision.youtrack.cloud/projects/SAR
- Documentation:
  [1 Proposal](docs/01-proposal.md) ·
  [2 Relevance](docs/02-relevance-evidence.md) ·
  [3 Literature](docs/03-literature-review.md) ·
  [4 Existing systems](docs/04-existing-systems.md) ·
  [5 Technologies](docs/05-technology-comparison.md) ·
  [6 Requirements](docs/06-requirements.md) ·
  [7 Architecture](docs/07-architecture.md) ·
  [8 UX/Prototype](docs/08-ux-prototype.md) ·
  [9 Verification](docs/09-verification-plan.md) ·
  [10 Project management](docs/10-project-management.md) ·
  [11 Supervisor feedback](docs/11-supervisor-feedback.md) ·
  [References](docs/12-references.md)

## Repository structure

```
docs/           documentation (sections 1-11, references, interview notes)
diagrams/src/   PlantUML sources (editable)
diagrams/png/   exported diagrams
prototype/      interface mockups (HTML source and PNG exports)
src/sar_vision/ source code
tests/          automated tests (pytest)
config/         example configuration (no secrets)
```

## Setup and tests

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                           # runs the geolocation unit tests
```

Baseline detection demo (pretrained YOLO, person class):

```bash
cd src
python -m sar_vision.detect_demo --image path/to/frame.jpg --tiling
```

Diagrams: edit `diagrams/src/*.puml` with the VS Code PlantUML extension or plantuml.com and export PNG files to `diagrams/png/`.

## Workflow

YouTrack task `SAR-N` → branch `SAR-N-short-name` → commits `SAR-N: description` → pull request reviewed by another team member → merge into `main`. Submissions are marked with Git tags; the first probationary-period submission is tagged `prob-period-1`.
