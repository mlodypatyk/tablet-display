import type { Dashboard } from '../types'

const LABELS: Record<string, string> = {
  weather: 'Pogoda',
  transit: 'Komunikacja',
  train: 'Pociągi',
}

export default function StatusBar({ data, error }: { data: Dashboard | null; error: string | null }) {
  const updated = data?.generated_at
    ? new Date(data.generated_at).toLocaleTimeString('pl-PL')
    : null

  return (
    <footer className="statusbar">
      <span className="statusbar__updated">
        {error ? `Błąd: ${error}` : updated ? `Aktualizacja: ${updated}` : 'Ładowanie…'}
      </span>
      <div className="statusbar__sources">
        {Object.entries(LABELS).map(([key, label]) => {
          const status = data?.sources?.[key]
          let cls = 'dot dot--pending'
          let text = '…'
          if (status === 'ok') {
            cls = 'dot dot--ok'
            text = ''
          } else if (status === 'stale') {
            cls = 'dot dot--stale'
            text = 'nieaktualne'
          } else if (status === 'error') {
            cls = 'dot dot--error'
            text = 'błąd'
          }
          return (
            <span className="statusbar__source" key={key}>
              <span className={cls} />
              {label}
              {text ? `: ${text}` : ''}
            </span>
          )
        })}
      </div>
    </footer>
  )
}
