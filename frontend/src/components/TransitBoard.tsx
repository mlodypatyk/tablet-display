import type { Transit } from '../types'

function formatMinutes(minutes: number): string {
  if (minutes === 0) return 'teraz'
  if (minutes === 1) return 'za 1 min'
  return `za ${minutes} min`
}

export default function TransitBoard({ transit }: { transit: Transit }) {
  return (
    <section className="board">
      <div className="stops">
        {transit.stops.map((stop) => (
          <div className="stop" key={`${stop.name}-${stop.number}`}>
            <header className="board__header">
              <h2>
              {stop.name}
              {stop.number ? <span className="stop__pole"> {stop.number}</span> : null}
              </h2>
            </header>
            {stop.departures.length === 0 ? (
              <div className="empty">Brak odjazdów</div>
            ) : (
              <ul className="departures">
                {stop.departures.map((dep, i) => (
                  <li className="departure" key={i}>
                    <span className="departure__line">{dep.line}</span>
                    <span className="departure__dir">{dep.direction}</span> 
                    <span className="departure__time">{(dep.minutes ?? 46) < 45 ? formatMinutes(dep.minutes) : dep.time}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}
