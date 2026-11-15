import { describe, expect, it } from 'vitest'
import { boxToPercent, countByStatus, formatCoord, scaleDetections } from './utils.js'
import { detect, updateStatus } from './api.js'
import mock from './mock.json'

describe('utils', () => {
  it('converts a pixel box to percent of the image', () => {
    expect(boxToPercent([192, 108, 384, 216], 1920, 1080)).toEqual({
      left: 10, top: 10, width: 10, height: 10,
    })
  })

  it('scales boxes to a different image size', () => {
    const [d] = scaleDetections([{ id: 1, bbox: [100, 100, 200, 200] }],
      { width: 1000, height: 1000 }, { width: 4000, height: 2000 })
    expect(d.bbox).toEqual([400, 200, 800, 400])
    expect(d.id).toBe(1)
  })

  it('counts detections by status', () => {
    const list = [{ status: 'new' }, { status: 'confirmed' }, { status: 'new' }]
    expect(countByStatus(list)).toEqual({ new: 2, confirmed: 1, rejected: 0 })
  })

  it('formats coordinates or says they are missing', () => {
    expect(formatCoord(43.2389123, 76.8897)).toBe('43.238912, 76.889700')
    expect(formatCoord(null, null)).toBe('нет координат')
  })
})

describe('mock api (no backend)', () => {
  it('mock.json follows the contract', () => {
    for (const d of mock.detections) {
      expect(Object.keys(d).sort()).toEqual(
        ['bbox', 'confidence', 'frame', 'id', 'image_id', 'lat', 'lon', 'status'])
      expect(d.bbox).toHaveLength(4)
    }
  })

  it('detect returns mock boxes scaled to the uploaded image', async () => {
    const file = new File(['x'], 'frame.jpg', { type: 'image/jpeg' })
    const res = await detect(file, {}, { getSize: async () => ({ width: 3840, height: 2160 }) })
    expect(res.width).toBe(3840)
    expect(res.detections).toHaveLength(2)
    expect(res.detections[0].bbox[0]).toBe(mock.detections[0].bbox[0] * 2)
  })

  it('updateStatus changes only the status', async () => {
    const d = mock.detections[0]
    const updated = await updateStatus(d, 'confirmed')
    expect(updated).toEqual({ ...d, status: 'confirmed' })
  })
})
