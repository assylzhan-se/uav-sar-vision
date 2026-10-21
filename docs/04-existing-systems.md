# 4. Existing System Comparison

## 4.1 Systems selected

We compared four existing approaches that a SAR team could use today, plus the planned SAR-Vision design:

- **S1 – Manual review.** The operator watches the live view or reviews recorded footage. This is the baseline practice.
- **S2 – SARUAV.** Software developed at the University of Wrocław for detecting people in UAV photographs [8], [17].
- **S3 – Loc8.** Image-scanning software that searches photographs for user-defined colours [18].
- **S4 – DJI Matrice 4 series onboard AI.** Commercial enterprise UAVs with built-in detection of people, vehicles and vessels [19].
- **S5 – Research prototype.** The YOLO-based small-object detector of Ciccone and Ceruti [10].

Evidence for commercial products comes from news and industry articles rather than full technical documentation. Where a feature could not be confirmed, the table says so instead of assuming it.

## 4.2 Comparison

| Criterion | S1 Manual review | S2 SARUAV | S3 Loc8 | S4 DJI Matrice 4 onboard AI | S5 Research prototype [10] | SAR-Vision (planned) |
|---|---|---|---|---|---|---|
| Detection method | Human observer | Automated detection of people in photos [8], [17] | Pixel-level search for user-defined colour palettes; not person-specific [18] | Onboard AI detection and tracking of people, vehicles and vessels [19] | Fine-tuned YOLOv5 variant | Fine-tuned YOLO with tiling |
| Imagery | Any camera | Visible or near-infrared photos; not based on thermal data [17] | Photos; thermal use not stated [18] | RGB confirmed; thermal AI detection not confirmed [19] | RGB | RGB (MVP); thermal as extension |
| Timing | Live, limited by attention | Post-flight photo analysis [17] | Post-capture; real-time frame extraction announced as beta in 2020 [18] | In flight (described; latency not specified) [19] | Real time on Jetson Nano | Recorded data (MVP); live stream as extension |
| Location output | Estimated manually | Coordinates of identified places [17] | Image latitude/longitude in report [18] | Not confirmed from reviewed source | Not reported in reviewed material | Estimated coordinates of each detection |
| Operator review workflow | Not applicable | Map reports for rescuers [17] | User reviews flagged images [18] | Not confirmed | Not a system | Confirm/reject with persistent status |
| Hardware dependence | None | Works with photos from various cameras [17] | Works with photos from various sources [18] | DJI aircraft only | Jetson Nano | Any laptop; NVIDIA GPU recommended |
| Availability | Free | Licensing terms not confirmed | Subscription (as of 2020) [18] | Included with purchase of the aircraft | Research paper | Open source (academic project) |

## 4.3 Discussion

The comparison shows that automated assistance for SAR imagery already exists in several forms, so SAR-Vision is not a new idea. The differences lie in how existing tools work:

- **SARUAV** is the closest system in purpose and has been used in a real rescue [8]. It works on photographs after the flight and does not use thermal data [17].
- **Loc8** searches for colours rather than recognising people [18]. This works when the missing person wears distinctive clothing, but it depends on that information and on the background.
- **DJI's onboard AI** recognises people during the flight [19], but it is tied to specific DJI aircraft. The reviewed source does not describe how detections are exported or geolocated.
- **Research prototypes** such as [10] report strong detection results but focus on the model rather than on an operator workflow.

SAR-Vision aims to combine an open, fine-tuned person detector with telemetry-based geolocation and an operator review workflow in a tool that runs locally and does not depend on a specific UAV vendor. Whether this combination is useful in practice is what the evaluation in Section 9 and the user discussions in Section 2 are intended to show. We do not claim that it will outperform the systems above.
