import type { Train } from '../types'

function formatMinutes(minutes: number | null): string {
  if (minutes === null) return ''
  if (minutes === 0) return 'teraz'
  if (minutes === 1) return 'za 1 min'
  return `za ${minutes} min`
}

export default function TrainBoard({ train }: { train: Train }) {
  return (
    <section className="board">
      <header className="board__header">
        <h2>Pociągi — {train.station}</h2>
      </header>
      {train.departures.length === 0 ? (
        <div className="empty">Brak odjazdów</div>
      ) : (
        <ul className="trains">
          {train.departures.map((dep, i) => (
            <li className="train" key={i}>
              <span className="train__time">{dep.time}</span>
              <span className="train__name">{dep.train}</span>
              <span className="train__dest">{dep.destination}</span>
              <span className="train__track">{dep.track}</span>
              <span className="train__when">{formatMinutes(dep.minutes)}</span>
              {dep.status === 'delayed' ? (
                <span className="train__status train__status--delayed">opóźniony</span>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
