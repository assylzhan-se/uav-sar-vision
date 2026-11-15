import { countByStatus, formatCoord, STATUS_LABEL } from '../utils.js'

export default function DetectionList({ detections, selectedId, onSelect, onStatus }) {
  const counts = countByStatus(detections)
  return (
    <div className="panel">
      <h2>3. Находки</h2>
      <p className="counts">
        Всего: {detections.length} · новых: {counts.new} · подтверждено: {counts.confirmed} ·
        отклонено: {counts.rejected}
      </p>
      {detections.length === 0 && <p className="muted">Пока нет находок</p>}
      <ul className="list">
        {detections.map((d) => (
          <li
            key={d.id}
            className={`${d.status} ${d.id === selectedId ? 'selected' : ''}`}
            onClick={() => onSelect(d.id)}
          >
            <div>
              <b>#{d.id}</b> · уверенность {(d.confidence * 100).toFixed(0)}% ·{' '}
              <span className="status">{STATUS_LABEL[d.status]}</span>
              <div className="muted">{formatCoord(d.lat, d.lon)}</div>
            </div>
            <div className="actions">
              <button onClick={(e) => { e.stopPropagation(); onStatus(d, 'confirmed') }}>
                Подтвердить
              </button>
              <button onClick={(e) => { e.stopPropagation(); onStatus(d, 'rejected') }}>
                Отклонить
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
