import type { Train } from '../types'

function formatMinutes(minutes: number | null): string {
  if (minutes === null) return ''
  if (minutes === 0) return 'teraz'
  return `${minutes} min`
}

export default function TrainBoard({ train }: { train: Train }) {
  return (
    <section className="board">
      <header className="board__header">
        <h2>{train.station}</h2>
      </header>
      {train.departures.length === 0 ? (
        <div className="empty">Brak odjazdów</div>
      ) : (
        <ul className="trains">
          {train.departures.map((dep, i) => (
            <li className="train" key={i}>
              <span className="train__name">{dep.train}</span>
              <span className="train__dest">{dep.destination}</span>
              {dep.status === 'delayed' ? (
                <span className="train__status train__status--delayed">opóźniony</span>
              ) : null}
              <span className="train__time">{(dep.minutes ?? 46) < 45 ? formatMinutes(dep.minutes) : dep.time}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
