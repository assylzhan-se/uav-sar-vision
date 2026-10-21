# 5. Technology Comparison

This section covers four key technical decisions. Each decision lists the alternatives considered, how they compare against the criteria that matter for this project, and the current choice. Decisions marked *provisional* will be confirmed or revised through experiments in the next stage.

## 5.1 D1 – Person detection model

Criteria: detection quality on small objects after fine-tuning (FR-1), processing speed on a laptop GPU (NFR-1), and the maturity of training and export tools.

| Alternative | Advantages | Disadvantages |
|---|---|---|
| YOLO family (Ultralytics YOLOv8 / YOLO11) | Fast one-stage detector; widely used in SAR research [2], [10]; mature tools for training, evaluation and ONNX/TensorRT export [16] | Small objects still need tiling or architecture changes; Ultralytics code is licensed under AGPL-3.0, which is acceptable for an open academic project but restricts closed commercial use |
| RT-DETR [12] | Transformer detector with real-time speed on a server GPU; no non-maximum suppression step | Higher compute and memory needs; less SAR-specific evidence |
| Faster R-CNN [15] | Strong accuracy, frequently used as a reference [6] | Usually too slow for the throughput target on a laptop |

**Choice (provisional): YOLO, small or medium model size.** It offers the best balance of speed, accuracy and tooling for our constraints. RT-DETR will be trained on the same data as a comparison if time allows. YOLOv10 [13] is a further option with lower latency but less SAR-specific evidence, so it is not part of the initial plan.

## 5.2 D2 – Where processing runs

Criteria: works without internet (NFR-3), does not require modifying the UAV, computing power available for the model, and cost.

| Alternative | Advantages | Disadvantages |
|---|---|---|
| Onboard (e.g. NVIDIA Jetson on the UAV) [7], [10] | No video link needed; detections available during flight | Requires mounting and powering extra hardware; limited model size; not possible with most off-the-shelf enterprise UAVs |
| Ground laptop with GPU | Works offline; no UAV modification; larger models possible | Needs video and telemetry from the UAV, either live from the controller or after landing |
| Cloud server | Highest compute capacity | Requires a reliable internet connection, which is often unavailable in the field (assumption H2) |

**Choice: ground laptop.** The MVP processes recorded footage and photos after they are copied from the UAV. Live stream input is an extension because getting a stream from a consumer controller depends on the UAV model (risk R4).

## 5.3 D3 – Application structure and component communication

Criteria: ease of development for a three-person team, ability to split work, support for a map-based interface, and room for later extensions.

| Alternative | Advantages | Disadvantages |
|---|---|---|
| Single desktop script (OpenCV windows) | Fastest to prototype | Hard to build a map and review list; hard to split work between team members |
| Python backend (FastAPI) and browser interface, connected by REST and WebSocket | Clear separation between processing and interface; maps available through Leaflet; runs locally in a browser | Two codebases to maintain; slightly more setup |
| ROS 2 nodes | Standard in robotics; suited to onboard extensions | Steep learning curve; unnecessary for offline processing on a laptop |

**Choice (provisional): FastAPI backend and a browser interface.** REST handles commands, and WebSocket pushes new detections to the interface. The frontend framework (React or Vue) has not been decided yet. Leaflet with locally stored map tiles is planned for the map.

## 5.4 D4 – Data storage

Criteria: runs on a single laptop without a database server, easy to copy the data of one operation, sufficient for simple queries.

| Alternative | Advantages | Disadvantages |
|---|---|---|
| SQLite and image files on disk | No server; one file per operation; supported by the Python standard library | Not intended for many concurrent users |
| PostgreSQL with PostGIS | Strong spatial queries; multi-user | Needs a server installation; more than the MVP requires |
| MongoDB | Flexible document schema | Needs a server; no clear benefit for our data |

**Choice: SQLite.** If several workstations later need to share data, PostgreSQL would be reconsidered.

## 5.5 Summary of the proposed stack and implementation order

| Layer | Technology | Status |
|---|---|---|
| Detection | PyTorch, Ultralytics YOLO, SAHI | Provisional; to be confirmed by experiments |
| Image and video input | OpenCV, FFmpeg | Selected |
| Telemetry | Image EXIF/XMP metadata and DJI SRT subtitle files (fields vary by model) | To be confirmed once the UAV model is known |
| Backend | Python, FastAPI, WebSocket | Provisional |
| Storage | SQLite | Selected |
| Interface | React or Vue (undecided), Leaflet | Undecided / provisional |
| Optimisation | ONNX Runtime or TensorRT | Only if the speed target is not met without it |

Implementation will follow this order: (1) RGB detection on images with baseline evaluation; (2) tiling and fine-tuning; (3) geolocation for photos with metadata; (4) storage and operator interface; (5) video input with telemetry synchronisation. Live streams and thermal detection will only be added after the MVP works end to end.
