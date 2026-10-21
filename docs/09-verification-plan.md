# 9. Verification and Evaluation Plan

## 9.1 What the evaluation should show

The evaluation should answer four questions:

1. Does fine-tuning and tiling improve person detection compared with an off-the-shelf model?
2. Is processing fast enough for practical use on a laptop?
3. How accurate are the estimated coordinates under the stated assumptions?
4. Can operators complete the review workflow without help?

**Current status:** no evaluation has been carried out yet. The only completed check is a set of unit tests for the draft geolocation module. All tests below are planned.

## 9.2 Data

| Dataset | Use | Split |
|---|---|---|
| VisDrone [3] | Pre-training on drone imagery (pedestrian and people classes) | Official splits |
| HERIDAL [1] | Main SAR training and test set (RGB) | Official train/test; validation taken from train |
| SARD [2] | Additional SAR training data; secondary test | 70/15/15 if no official split |
| HIT-UAV [4] | Thermal extension (FR-10) | Official splits |
| Own footage (if a UAV is available) | Local conditions; geolocation test | Test only |

Test data is never used for training or for choosing thresholds.

## 9.3 Metrics

| Metric | Definition | Related requirement |
|---|---|---|
| Recall, precision | At IoU 0.5 and a fixed confidence threshold chosen on validation data | FR-1, FR-10 |
| mAP@0.5 | Standard detection metric, for comparison with published results | FR-1 |
| False positives per image | Average number of false detections per image; indicates operator workload | FR-1 |
| Throughput (FPS) | Mean processed frames per second for 1920×1080 video, with and without tiling | NFR-1 |
| Latency | Time from frame arrival to display, 95th percentile (live mode only) | NFR-2 |
| Geolocation error | Horizontal distance in metres between the estimated and measured marker positions | FR-4 |
| SUS score | System Usability Scale, after the usability session | NFR-5 |

## 9.4 Baselines

| Baseline | Purpose |
|---|---|
| B1: YOLO pretrained on COCO, person class only, no fine-tuning | Shows the effect of SAR-specific training |
| B2: Fine-tuned model without tiling | Shows the effect of tiling on small people |
| B3: Published result of [10] on HERIDAL (mAP@50 = 0.802) | Places our result relative to recent work; differences in setup will be noted |
| B4: Published human performance from [20] (unaided recall 66%) | Indicates whether the detector could help operators; not directly comparable because the image sets differ |

A small comparison with manual review (time taken and people found by volunteers on the same footage) may be added if time permits. It is not part of the acceptance criteria.

## 9.5 Test plan

| ID | Test | Conditions | Pass criterion | Status |
|---|---|---|---|---|
| T-1 | RGB detection quality | HERIDAL test split; B1 and B2 also evaluated | FR-1 targets | Planned |
| T-2 | Effect of tiling | Images with persons smaller than 32 px | Recall with tiling reported against B2 | Planned |
| T-3 | Thermal detection (extension) | HIT-UAV test split | FR-10 target | Planned, if FR-10 is implemented |
| T-4 | Geolocation accuracy | ≥ 10 ground markers with phone-GPS positions, 50 m altitude, nadir camera, flat area | FR-4 targets | Planned; depends on UAV access (R1) |
| T-5 | Throughput and latency | 5-minute 1080p video, reference laptop, 5 runs | NFR-1 (and NFR-2 if live mode exists) | Planned |
| T-6 | End-to-end functional test | Image folder and MP4 input; threshold change; alerts | FR-2, FR-5, FR-8, FR-11 | Planned |
| T-7 | Review and export | Confirm 3 and reject 2 detections, restart, export CSV and KML | FR-6, FR-7 | Planned |
| T-8 | Offline operation | Network disabled during T-6 | NFR-3 | Planned |
| T-9 | Usability | 3 participants complete UC-1 to UC-5, then answer the SUS questionnaire | NFR-5 | Planned |
| T-10 | Unit tests | `pytest` for geolocation, telemetry parsing and export; run in GitHub Actions on each pull request | NFR-7 | Partly done: 6 geolocation tests pass locally; CI not yet set up |

## 9.6 Measurement conditions to be recorded

For every reported result, the following will be recorded: model and weights version, input size, confidence and IoU thresholds, tiling settings, hardware (CPU, GPU, RAM), operating system, driver and library versions, and the number of repeated runs. For T-4, the UAV model, altitude source, weather and ground truth method will also be recorded. Results from public datasets and from our own footage will be reported separately.
