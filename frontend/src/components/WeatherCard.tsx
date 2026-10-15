import type { Weather } from '../types'

const ICONS: Record<number, string> = {
  0: '☀️',
  1: '🌤️',
  2: '⛅',
  3: '☁️',
  45: '🌫️',
  48: '🌫️',
  51: '🌦️',
  53: '🌦️',
  55: '🌧️',
  56: '🌧️',
  57: '🌧️',
  61: '🌧️',
  63: '🌧️',
  65: '🌧️',
  66: '🌧️',
  67: '🌧️',
  71: '🌨️',
  73: '🌨️',
  75: '❄️',
  77: '❄️',
  80: '🌦️',
  81: '🌦️',
  82: '🌧️',
  85: '🌨️',
  86: '🌨️',
  95: '⛈️',
  96: '⛈️',
  99: '⛈️',
}

export default function WeatherCard({ weather }: { weather: Weather }) {
  return (
    <div className="weather">
      <div className="weather__icon">{ICONS[weather.code] ?? '🌡️'}</div>
      <div className="weather__main">
        <span className="weather__temp">{weather.temperature.toFixed(0)}°</span>
        <span className="weather__desc">
          Odczuwalna {weather.apparent.toFixed(0)}°
        </span>
      </div>
    </div>
  )
}
