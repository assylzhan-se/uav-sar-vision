// Pure helpers (tested in utils.test.js)

/** Box in pixels -> CSS position in percent of the image, so it scales with the picture. */
export function boxToPercent(bbox, width, height) {
  const [x1, y1, x2, y2] = bbox
  return {
    left: (x1 / width) * 100,
    top: (y1 / height) * 100,
    width: ((x2 - x1) / width) * 100,
    height: ((y2 - y1) / height) * 100,
  }
}

/** Scale mock boxes made for one image size to another image size. */
export function scaleDetections(detections, from, to) {
  const sx = to.width / from.width
  const sy = to.height / from.height
  return detections.map((d) => ({
    ...d,
    bbox: [d.bbox[0] * sx, d.bbox[1] * sy, d.bbox[2] * sx, d.bbox[3] * sy],
  }))
}

export function countByStatus(detections) {
  const counts = { new: 0, confirmed: 0, rejected: 0 }
  for (const d of detections) counts[d.status] = (counts[d.status] ?? 0) + 1
  return counts
}

export function formatCoord(lat, lon) {
  if (lat == null || lon == null) return 'нет координат'
  return `${lat.toFixed(6)}, ${lon.toFixed(6)}`
}

export const STATUS_LABEL = { new: 'новая', confirmed: 'подтверждена', rejected: 'отклонена' }
export const STATUS_COLOR = { new: '#E07A2F', confirmed: '#2E8B57', rejected: '#8A8F98' }
