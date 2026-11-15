import { boxToPercent, STATUS_COLOR } from '../utils.js'

export default function ImageWithBoxes({ src, result, selectedId, onSelect }) {
  if (!src) return <div className="panel empty">Загрузите снимок, чтобы увидеть находки</div>
  return (
    <div className="panel">
      <h2>2. Кадр</h2>
      <div className="frame">
        <img src={src} alt="Снимок с дрона" />
        {result?.detections.map((d) => {
          const p = boxToPercent(d.bbox, result.width, result.height)
          return (
            <button
              key={d.id}
              className={`box ${d.id === selectedId ? 'selected' : ''}`}
              title={`#${d.id} · ${(d.confidence * 100).toFixed(0)}%`}
              style={{
                left: `${p.left}%`, top: `${p.top}%`, width: `${p.width}%`, height: `${p.height}%`,
                borderColor: STATUS_COLOR[d.status],
              }}
              onClick={() => onSelect(d.id)}
            >
              <span style={{ background: STATUS_COLOR[d.status] }}>#{d.id}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
