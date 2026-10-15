import type { Weather } from '../types'

export default function WeatherCard({ weather }: { weather: Weather }) {
  return (
    <div className="weather">
      <div className="weather__main">
        <span className="weather__temp">{weather.temperature.toFixed(0)}°</span>
        <span className="weather__desc">{weather.description}</span>
      </div>
      <div className="weather__meta">
        <div>
          <span className="weather__label">Dzień</span>
          <span>
            {weather.daily.min.toFixed(0)}° / {weather.daily.max.toFixed(0)}°
          </span>
        </div>
        <div>
          <span className="weather__label">Odczuwalna</span>
          <span>{weather.apparent.toFixed(0)}°</span>
        </div>
        <div>
          <span className="weather__label">Wiatr</span>
          <span>{weather.wind.toFixed(0)} km/h</span>
        </div>
        <div>
          <span className="weather__label">Wilgotność</span>
          <span>{weather.humidity}%</span>
        </div>
      </div>
    </div>
  )
}
