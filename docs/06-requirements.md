# 6. Requirements Specification

Priorities follow the MoSCoW method: **M** (must), **S** (should), **C** (could) and **W** (won't in this version). All numerical values are *proposed targets* that have not yet been measured. They may be adjusted after the baseline experiments and user discussions, and any change will be recorded in the repository.

## 6.1 Functional requirements

| ID | Requirement | Pri. | Acceptance criterion | UC / Test |
|---|---|---|---|---|
| FR-1 | Detect people in RGB aerial images and video frames and mark each detection with a bounding box and confidence score | M | On the HERIDAL test split: recall ≥ 0.80 and precision ≥ 0.70 at IoU 0.5, at a confidence threshold chosen on the validation split | UC-2 / T-1 |
| FR-2 | Accept a folder of images (JPG) and a recorded video file (MP4) as input | M | Both input types are processed end to end in a demonstration | UC-1 / T-6 |
| FR-3 | Support tiled (sliced) inference for high-resolution images | M | Tiling can be switched on and off; its effect on recall for small persons is reported | UC-2 / T-2 |
| FR-4 | Estimate the latitude and longitude of each detection from UAV telemetry, for a nadir camera over approximately flat terrain | M | Mean horizontal error ≤ 10 m and maximum ≤ 20 m over at least 10 ground markers at 50 m altitude | UC-2 / T-4 |
| FR-5 | Show detections to the operator as a frame with boxes, a list with thumbnails and markers on a map | M | Every stored detection appears in the list and, if it has coordinates, on the map | UC-3 / T-6 |
| FR-6 | Let the operator confirm or reject each detection; save the status | M | Statuses are unchanged after the application is restarted | UC-4 / T-7 |
| FR-7 | Export confirmed detections to CSV and KML | M | Files open in a spreadsheet and in Google Earth; coordinates match the database | UC-5 / T-7 |
| FR-8 | Let the operator change the confidence threshold | S | Changing the threshold changes the number of displayed detections | UC-6 / T-6 |
| FR-9 | Accept a live video stream (RTSP) as input | S | A stream from a test server is processed continuously for 10 minutes | UC-1 / T-6 |
| FR-10 | Detect people in thermal images with a separate model | S | Recall ≥ 0.80 for the person class on the HIT-UAV test split at IoU 0.5 | UC-2 / T-3 |
| FR-11 | Alert the operator when a new detection appears | S | A visual alert is shown within 1 s of the detection being stored | UC-3 / T-6 |
| FR-12 | Merge repeated detections of the same person across consecutive frames | C | Defined after the MVP; measured on annotated video | — |
| FR-13 | Support geolocation for tilted camera angles | C | Defined after FR-4 is validated | — |
| FR-14 | Run detection onboard the UAV | W | Out of scope | — |

## 6.2 Non-functional requirements

| ID | Requirement | Pri. | Acceptance criterion | Test |
|---|---|---|---|---|
| NFR-1 | Throughput: process 1920×1080 video without tiling at ≥ 10 frames per second | M | Mean FPS over a 5-minute video, measured 5 times on the reference laptop | T-5 |
| NFR-2 | Latency in live-stream mode: from frame arrival to detection displayed | S | 95th percentile ≤ 1 s (applies only if FR-9 is implemented) | T-5 |
| NFR-3 | Full operation without internet access, including the model, map tiles and interface | M | All MVP functions work with the network disabled | T-8 |
| NFR-4 | Runs on Windows 10/11 or Ubuntu 22.04; NVIDIA GPU recommended; slower CPU-only mode available | M | Installation following the README succeeds on a clean machine | T-6 |
| NFR-5 | Usability: an operator without machine-learning knowledge can complete the main workflow | S | 3 test users complete UC-1 to UC-5 without help; SUS score reported (target ≥ 70) | T-9 |
| NFR-6 | No credentials or operation data in the repository; operation data stored locally | M | Repository and `.gitignore` reviewed before each tagged submission | Review |
| NFR-7 | Geolocation, telemetry parsing and export are covered by unit tests | S | Unit tests pass in continuous integration; line coverage of these modules ≥ 70% | T-10 |

**Reference laptop.** NFR-1 and NFR-2 will be measured on a laptop with an NVIDIA RTX 3060 or comparable GPU. The exact model, drivers and library versions will be recorded with the results. If the team's hardware differs, the target will be stated for the hardware actually used.

## 6.3 Notes on the acceptance criteria

- **Detection metrics.** Recall and precision are calculated at an intersection-over-union (IoU) threshold of 0.5 between predicted and ground-truth boxes. Test splits are never used for training or for tuning the threshold. Recall is the primary metric because a missed person is more costly than a false alarm (assumption H3); precision is kept as a constraint so that the operator is not overloaded.
- **Throughput with tiling.** NFR-1 applies to untiled inference. Tiling multiplies the number of model runs per frame, so its speed will be reported separately. Tiling is expected mainly for high-resolution still photographs.
- **Geolocation accuracy.** The error depends on the UAV's GNSS accuracy, altitude above ground, camera orientation and terrain. The 10 m target applies only to the stated conditions. Ground truth positions measured with a phone also contain an error of a few metres, which will be reported.
- **Dataset results and real use.** Meeting FR-1 on HERIDAL does not show that the system will perform equally well in Kazakhstan. Results on local footage, if collected, will be reported separately.
