import { useState } from 'react'

const FIELDS = [
  ['lat', 'Широта дрона'],
  ['lon', 'Долгота дрона'],
  ['altitude_m', 'Высота, м'],
  ['yaw_deg', 'Курс, °'],
]

export default function UploadForm({ onSubmit, busy }) {
  const [file, setFile] = useState(null)
  const [tel, setTel] = useState({ lat: '43.2389', lon: '76.8897', altitude_m: '50', yaw_deg: '0' })

  function submit(e) {
    e.preventDefault()
    if (file) onSubmit(file, tel)
  }

  return (
    <form className="panel upload" onSubmit={submit}>
      <h2>1. Снимок с дрона</h2>
      <label className="file">
        <input
          type="file"
          accept="image/jpeg,image/png"
          aria-label="Снимок"
          onChange={(e) => setFile(e.target.files[0] ?? null)}
        />
      </label>
      <div className="telemetry">
        {FIELDS.map(([key, label]) => (
          <label key={key}>
            {label}
            <input
              type="number"
              step="any"
              value={tel[key]}
              onChange={(e) => setTel({ ...tel, [key]: e.target.value })}
            />
          </label>
        ))}
      </div>
      <button type="submit" disabled={!file || busy}>
        {busy ? 'Поиск…' : 'Найти людей'}
      </button>
    </form>
  )
}
