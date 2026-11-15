import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import mock from './mock.json'

// The map needs a real browser; in tests it is replaced by a simple stub.
vi.mock('./components/MapView.jsx', () => ({
  default: ({ detections }) => <div data-testid="map">markers: {detections.length}</div>,
}))
vi.mock('./api.js', () => ({
  isMock: () => true,
  detect: vi.fn(async () => structuredClone(mock)),
  updateStatus: vi.fn(async (d, status) => ({ ...d, status })),
}))
globalThis.URL.createObjectURL = () => 'blob:frame'
globalThis.URL.revokeObjectURL = () => {}

import App from './App.jsx'

describe('operator screen', () => {
  it('uploads an image, shows boxes, list and markers, and confirms a detection', async () => {
    const user = userEvent.setup()
    render(<App />)
    expect(screen.getByText('Пока нет находок')).toBeInTheDocument()

    const file = new File(['x'], 'frame.jpg', { type: 'image/jpeg' })
    await user.upload(screen.getByLabelText('Снимок'), file)
    await user.click(screen.getByRole('button', { name: 'Найти людей' }))

    expect(await screen.findByText(/Всего: 2/)).toBeInTheDocument()
    expect(screen.getByAltText('Снимок с дрона')).toBeInTheDocument()
    expect(screen.getByTestId('map')).toHaveTextContent('markers: 2')

    await user.click(screen.getAllByRole('button', { name: 'Подтвердить' })[0])
    expect(await screen.findByText(/подтверждено: 1/)).toBeInTheDocument()
  })
})
