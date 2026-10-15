import { useDashboard } from './api'
import Clock from './components/Clock'
import WeatherCard from './components/WeatherCard'
import TransitBoard from './components/TransitBoard'
import TrainBoard from './components/TrainBoard'

export default function App() {
  const { data, error } = useDashboard(60_000)

  return (
    <div className="app">
      <header className="app__top">
        <Clock />
        {data?.weather ? <WeatherCard weather={data.weather} /> : null}
      </header>

      <main className="app__main">
        {data?.transit ? (
          <TransitBoard transit={data.transit} />
        ) : (
          <section className="board board--empty">Ładowanie komunikacji…</section>
        )}
        {data?.train ? (
          <TrainBoard train={data.train} />
        ) : (
          <section className="board board--empty">Ładowanie pociągów…</section>
        )}
      </main> 
    </div>
  )
}
