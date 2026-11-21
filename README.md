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

Stage 2: working prototype (meeting 22 November 2026).

| Module | Owner | What works |
|---|---|---|
| CV (`src/sar_vision/detection`) | Shalmanov Assylzhan | YOLOv8 person detection, 3 modes (fast / balanced / accurate with SAHI), video processing with a tracker, evaluation on VisDrone ([results](docs/results-baseline.md)) |
| Backend (`backend/`) | Kurmantayev Ali | REST API, SQLite, geolocation, telemetry from EXIF/DJI XMP, video upload, history, CSV/KML export, statistics |
| Frontend (`frontend/`) | Shakalova Diana | Operator screen: upload photo or video, mode and threshold, boxes, list with filters, map, history, export |

## Quick start (demo)

```bash
python -m venv .venv
.venv\Scripts\activate              # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .                     # makes `sar_vision` importable everywhere
python scripts/check.py              # MUST end with "ALL CHECKS PASSED"

uvicorn app.main:app --app-dir backend          # terminal 1, http://localhost:8000/docs
cd frontend && npm install && npm run dev       # terminal 2, http://localhost:5173
```

The header must show a green **"Сервер подключён · детектор YOLOv8"**. Yellow "mock" or red
"Сервер недоступен" means the demo is NOT using the real model.

CV only: `python -m sar_vision.detection --image frame.jpg --compare` (all modes),
`python -m sar_vision.detection --video flight.mp4 --every 1`.

## Technologies (provisional)

Python, PyTorch, Ultralytics YOLOv8, SAHI, OpenCV, FastAPI, SQLite, Pillow (EXIF), React 19 + Vite, Leaflet, Vitest, pytest, PlantUML. See [docs/05-technology-comparison.md](docs/05-technology-comparison.md).

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

## Tests

```bash
python scripts/check.py      # all: CV + backend + frontend + live server with the real model
pytest                       # CV only
pytest backend/tests         # backend only
cd frontend && npm test      # frontend only
```

Diagrams: edit `diagrams/src/*.puml` with the VS Code PlantUML extension or plantuml.com and export PNG files to `diagrams/png/`.

## Workflow

YouTrack task `SAR-N` → branch `SAR-N-short-name` → commits `SAR-N: description` → pull request reviewed by another team member → merge into `main`. Submissions are marked with Git tags; the first probationary-period submission is tagged `prob-period-1`.
