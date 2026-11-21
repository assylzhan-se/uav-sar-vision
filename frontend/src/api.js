// Talks to the backend (docs/api-contract.md). Without VITE_API_URL it uses src/mock.json.
import mock from './mock.json'
import { scaleDetections } from './utils.js'

export const API_URL = import.meta.env.VITE_API_URL || ''
export const isMock = () => !API_URL

function imageSize(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.naturalWidth, height: img.naturalHeight })
      URL.revokeObjectURL(url)
    }
    img.onerror = () => reject(new Error('Не удалось прочитать изображение'))
    img.src = url
  })
}

export async function detect(file, telemetry, { getSize = imageSize } = {}) {
  if (isMock()) {
    const size = await getSize(file)
    return {
      image_id: mock.image_id,
      ...size,
      detections: scaleDetections(mock.detections, mock, size),
    }
  }
  const form = new FormData()
  form.append('file', file)
  for (const [key, value] of Object.entries(telemetry)) {
    if (value !== '' && value != null) form.append(key, value)
  }
  const res = await fetch(`${API_URL}/api/detect`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Ошибка сервера ${res.status}: ${await res.text()}`)
  return res.json()
}

export async function updateStatus(detection, status) {
  if (isMock()) return { ...detection, status }
  const res = await fetch(`${API_URL}/api/detections/${detection.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  })
  if (!res.ok) throw new Error(`Ошибка сервера ${res.status}`)
  return res.json()
}
