import { useState } from 'react'
import { detect, isMock, updateStatus } from './api.js'
import UploadForm from './components/UploadForm.jsx'
import ImageWithBoxes from './components/ImageWithBoxes.jsx'
import DetectionList from './components/DetectionList.jsx'
import MapView from './components/MapView.jsx'

export default function App() {
  const [src, setSrc] = useState(null)
  const [result, setResult] = useState(null)
  const [selectedId, setSelectedId] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function handleUpload(file, telemetry) {
    setBusy(true)
    setError('')
    try {
      if (src) URL.revokeObjectURL(src)
      setSrc(URL.createObjectURL(file))
      setResult(await detect(file, telemetry))
      setSelectedId(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleStatus(detection, status) {
    try {
      const updated = await updateStatus(detection, status)
      setResult((r) => ({
        ...r,
        detections: r.detections.map((d) => (d.id === updated.id ? updated : d)),
      }))
    } catch (e) {
      setError(e.message)
    }
  }

  const detections = result?.detections ?? []
  return (
    <div className="app">
      <header>
        <h1>SAR-Vision</h1>
        <span className={`mode ${isMock() ? 'mock' : 'live'}`}>
          {isMock() ? 'демо-данные (mock.json)' : 'подключено к серверу'}
        </span>
      </header>
      {error && <p className="error" role="alert">{error}</p>}
      <main>
        <div className="col">
          <UploadForm onSubmit={handleUpload} busy={busy} />
          <DetectionList
            detections={detections}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onStatus={handleStatus}
          />
        </div>
        <div className="col wide">
          <ImageWithBoxes src={src} result={result} selectedId={selectedId} onSelect={setSelectedId} />
          <MapView detections={detections} selectedId={selectedId} onSelect={setSelectedId} />
        </div>
      </main>
    </div>
  )
}
