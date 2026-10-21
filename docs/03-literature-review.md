# 3. Literature Review

## 3.1 Search method

Sources were found through Google Scholar, IEEE Xplore, MDPI and arXiv. We used search terms such as *UAV search and rescue person detection*, *small object detection aerial images*, *thermal human detection UAV* and *real-time object detection*. We included work on detecting people or small objects in UAV imagery, public datasets suitable for SAR and widely used detection architectures. Most sources are from 2021–2025. A few earlier papers are kept because they introduced methods or datasets that the project builds on directly.

The review uses 16 sources: 15 peer-reviewed publications (11 of them from 2021 or later) and the documentation of the Ultralytics framework. Sources [17]–[19] are used only in the system comparison in Section 4.

## 3.2 Analysis of key publications

| Ref. | Focus and method | Data | Main finding | Limitation | Use in SAR-Vision |
|---|---|---|---|---|---|
| [1] 2019 | Deep-learning person detection for land SAR | HERIDAL (introduced) | Deep learning is applicable to SAR aerial imagery; provides a benchmark dataset | RGB only; not designed for real time | HERIDAL as a training and test set |
| [2] 2021 | Comparison of Faster R-CNN, YOLOv4, RetinaNet and Cascade R-CNN for SAR | VisDrone, SARD (introduced) | YOLOv4 selected for its speed, accuracy and low false-detection rate; robustness to weather and motion blur tested | Simulated rescue scenes | SARD dataset; supports choosing a one-stage detector |
| [3] 2022 | Benchmark for detection and tracking from drones | VisDrone | Small objects are a major difficulty in drone imagery | Mostly urban scenes | Pre-training data before SAR fine-tuning |
| [4] 2023 | High-altitude thermal dataset | HIT-UAV: 2,898 images, 60–130 m | Public thermal data for persons and vehicles; YOLOv4 baseline reached 89.88% AP for persons | Limited scene variety | Thermal extension (FR-10) |
| [5] 2022 | Paired visual and thermal dataset for wilderness SAR | WiSARD | Supports experiments combining RGB and thermal imagery | Small size | Possible thermal and fusion experiments |
| [6] 2022 | Faster R-CNN and SSD on aerial thermal images | OSU Thermal, AAU PD T | Faster R-CNN (ResNet50) gave the best accuracy (55.7% mAP@0.5 on AAU PD T); SSD (MobileNet-v1) was fastest (44 FPS on a GTX 1080) | Desktop GPU only | Illustrates the accuracy–speed trade-off |
| [7] 2019 | Onboard embedded vision on an autonomous UAV for SAR | Authors' data | Human detection can run onboard without an operator in the loop | Constrained model size and hardware | Argument for and against onboard processing (Section 5) |
| [8] 2021 | Case study of the SARUAV system | Real operation | First documented rescue supported by an automated human detection system | Post-flight analysis | Evidence of relevance; system compared in Section 4 |
| [9] 2023 | Survey of UAVs for SAR | Literature | Summarises tasks and open challenges in UAV-based SAR | No experiments | Framing of the problem |
| [10] 2025 | YOLO adapted for small objects in SAR (feature fusion variants, extra P2 head, attention modules) | VisDrone, then HERIDAL | YOLOv5s-PBfpn-Deconv reached mAP@50 of 0.802 on HERIDAL and ran in real time on a Jetson Nano | RGB only | Two-stage transfer learning; reference result for evaluation |
| [11] 2022 | SAHI: slicing images into tiles for training and inference | VisDrone, xView | Slicing at inference raised AP by 5.1–6.8% for the tested detectors, and by up to 14.5% when combined with slice-based fine-tuning | Higher inference time | Tiling for small people (FR-3) |
| [12] 2024 | RT-DETR: real-time transformer detector | COCO | 53.1% AP at 108 FPS on a T4 GPU (R50 version) | Larger compute needs than small YOLO models | Alternative detector (Section 5) |
| [13] 2024 | YOLOv10: detection without non-maximum suppression | COCO | Lower latency at comparable accuracy | Limited SAR-specific evidence | Alternative detector (Section 5) |
| [14] 2016 | YOLO: single-stage real-time detection | PASCAL VOC | Detection treated as one regression problem; very fast | Weak on small objects in early versions | Foundation of the selected model family |
| [15] 2015 | Faster R-CNN: two-stage detection with a region proposal network | PASCAL VOC, COCO | High accuracy | Slower than one-stage detectors | Accuracy-oriented alternative |
| [16] | Ultralytics YOLO framework (documentation) | — | Tools for training, evaluation and export to ONNX/TensorRT | Not a scientific publication | Implementation tool |

## 3.3 Analysis

**Detector families.** Two-stage detectors such as Faster R-CNN [15] tend to be accurate but slower. One-stage detectors such as YOLO [14] and SSD trade some accuracy for speed. The comparison by Sambolek and Ivašić-Kos [2] selected YOLOv4 for SAR because it combined good accuracy, speed and few false detections. A similar trade-off appears in thermal imagery [6]. Transformer-based real-time detectors such as RT-DETR [12] are a newer option; their advantage on very small objects in aerial imagery is less established, and they need more compute.

**Small objects.** This is the most consistent difficulty reported in the literature [1], [3]. Three techniques recur. The first is fine-tuning on domain-specific data [2]. The second is staged transfer learning from a general drone dataset to a SAR dataset [10]. The third is changing the input scale, either through architectural changes such as an additional high-resolution detection head [10] or by slicing large images into tiles [11]. Tiling does not require changing the model, but it increases processing time. This matters for our speed requirement.

**Thermal imagery.** Thermal datasets [4], [5] and studies [6] show that people can be detected in thermal images, but public data is limited and differs from RGB data in resolution and appearance. A thermal model would need to be trained and evaluated separately. For this reason, thermal detection is treated as an extension rather than part of the MVP.

**Where processing happens.** Onboard processing [7], [10] avoids sending video to the ground, but it limits model size and requires suitable hardware on the UAV. Processing on a ground laptop allows larger models and does not require modifying the aircraft, but it depends on being able to get video and telemetry from the UAV.

**From detection to action.** Most studies report detection metrics such as mAP. Fewer describe how detections are reviewed by operators or turned into ground coordinates, although this step determines whether a detection helps a rescue team [8]. This gap motivates the geolocation and review components of SAR-Vision.

Good results on public datasets do not guarantee similar performance in real operations. Terrain, season, altitude and camera models in Kazakhstan may differ from those in HERIDAL or SARD, which were collected in Croatia. This is why the evaluation plan includes testing on our own footage where possible.

## 3.4 Implications for SAR-Vision

| Finding from the literature | How the project responds |
|---|---|
| People in aerial images are small objects | Tiling (SAHI), fine-tuning on SAR data, evaluation of tiled versus untiled inference |
| SAR-specific fine-tuning improves results | Staged training: VisDrone, then HERIDAL and SARD |
| Thermal data is limited | Thermal model postponed to an extension; separate evaluation if implemented |
| Domain shift between datasets and real scenes | Separate test on local footage when available; results reported separately |
| Detection alone is not enough for rescue teams | Geolocation, operator review and export are part of the MVP |
