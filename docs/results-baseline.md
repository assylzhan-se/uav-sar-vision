# Baseline results: pretrained detector (SAR-18)

Owner: Shalmanov Assylzhan. Reproduce:

```bash
python -m sar_vision.evaluation --images VisDrone2019-DET-val/images \
    --labels VisDrone2019-DET-val/annotations --format visdrone \
    --modes fast,balanced,accurate --conf 0.15 --limit 40
```

## Setup

- Model: YOLOv8s pretrained on COCO (class *person*), **not yet fine-tuned** (baseline B1).
- Data: 40 random images of VisDrone2019-DET-val (seed 0), 895 people
  (categories *pedestrian* and *people*). Boxes smaller than the model can see are kept, so the
  task is hard on purpose.
- Matching: IoU ≥ 0.5, greedy by confidence; AP50 = 101-point interpolation.
- Hardware: CPU only (laptop-class), so time is an upper bound; a GPU is 10–30× faster.

## Result

| Mode | Recall | Precision | AP50 | ms / image |
|---|---|---|---|---|
| fast (640 px) | 0.221 | 0.715 | 0.196 | 223 |
| balanced (1280 px) | 0.416 | 0.703 | 0.378 | 532 |
| accurate (SAHI 416 px tiles) | 0.507 | 0.610 | 0.441 | 2673 |

Other configurations tried during tuning (same 40 images): SAHI with 640 px tiles —
recall 0.418, precision 0.636; SAHI 320 px — recall 0.504, precision 0.573, 4.2 s per image.
416 px tiles give the best recall/time balance, so they were chosen for `accurate`.

## Conclusions

1. Small people are the main problem: at the default 640 px the model misses 78 % of them.
   Higher input resolution doubles recall; tiling adds about 9 more points.
2. Tiling costs precision (more false alarms on tile borders and small objects) and time,
   so the operator chooses the mode: `balanced` for a first pass, `accurate` for suspicious frames.
3. Recall 0.5 is not enough for SAR (target in requirements: ≥ 0.8). Next step (SAR-21):
   fine-tune YOLOv8s on VisDrone + HERIDAL/SARD and compare with this table.

## Video mode

`process_video` samples one frame per `every_s` seconds and merges repeated detections of the
same person with a simple centre-distance tracker (`detection/tracking.py`). On a synthetic
8-second fly-over made from one VisDrone image (`scripts/make_demo_video.py`) 8 frames gave
101 raw detections. **Limitation:** with a moving camera the simple tracker can split one
person into several tracks (it does not compensate camera motion), so the number of
"people" is an over-estimate; motion compensation is planned.
