# Frontend (React + Leaflet)

Owner: Shakalova Diana. Data format: [docs/api-contract.md](../docs/api-contract.md).

## What it does

Operator screen from the mockups (`prototype/`):

1. Upload a UAV image and enter telemetry (latitude, longitude, altitude, heading).
2. The frame is shown with boxes around found people (colour = status).
3. List of detections with confidence and coordinates; buttons *Confirm* / *Reject*.
4. Map (Leaflet) with a marker for every detection; click a marker, box or list item to select it.

Two modes:
- **Demo mode** (default): answers come from `src/mock.json`, so the screen works without the backend.
- **Server mode**: create `.env.local` with `VITE_API_URL=http://localhost:8000` and start the backend.

## Run

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

## Tests

```bash
npm test
```

8 tests (Vitest + Testing Library): box-to-percent conversion, scaling, status counts,
coordinate formatting, `mock.json` follows the contract, mock API, and a full operator scenario
(upload → boxes, list and markers → confirm a detection).
