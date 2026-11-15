import { CircleMarker, MapContainer, TileLayer, Tooltip, useMap } from 'react-leaflet'
import { useEffect } from 'react'
import 'leaflet/dist/leaflet.css'
import { STATUS_COLOR, STATUS_LABEL } from '../utils.js'

const DEFAULT_CENTER = [43.2389, 76.8897] // Almaty

function FitToPoints({ points }) {
  const map = useMap()
  const key = points.map((p) => p.join(',')).join(';') // refit only when points change
  useEffect(() => {
    if (points.length === 1) map.setView(points[0], 18)
    if (points.length > 1) map.fitBounds(points, { padding: [40, 40], maxZoom: 19 })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, key])
  return null
}

export default function MapView({ detections, selectedId, onSelect }) {
  const located = detections.filter((d) => d.lat != null && d.lon != null)
  const points = located.map((d) => [d.lat, d.lon])
  return (
    <div className="panel">
      <h2>4. Карта</h2>
      <MapContainer center={DEFAULT_CENTER} zoom={13} className="map">
        <TileLayer
          attribution="&copy; OpenStreetMap"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitToPoints points={points} />
        {located.map((d) => (
          <CircleMarker
            key={d.id}
            center={[d.lat, d.lon]}
            radius={d.id === selectedId ? 11 : 8}
            pathOptions={{ color: STATUS_COLOR[d.status], fillOpacity: 0.8 }}
            eventHandlers={{ click: () => onSelect(d.id) }}
          >
            <Tooltip>#{d.id} · {STATUS_LABEL[d.status]}</Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
      {detections.length > 0 && located.length === 0 && (
        <p className="muted">Нет координат: укажите широту, долготу и высоту дрона</p>
      )}
    </div>
  )
}
