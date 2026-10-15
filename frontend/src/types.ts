export interface WeatherDaily {
  code: number
  description: string
  max: number
  min: number
}

export interface Weather {
  temperature: number
  apparent: number
  humidity: number
  wind: number
  code: number
  description: string
  daily: WeatherDaily
}

export interface Departure {
  line: string
  direction: string
  time: string
  minutes: number
}

export interface TransitStop {
  name: string
  number: string
  departures: Departure[]
}

export interface Transit {
  stops: TransitStop[]
  mock?: boolean
}

export interface TrainDeparture {
  time: string
  destination: string
  train: string
  category: string
  track: string
  status: string
  minutes: number | null
}

export interface Train {
  station: string
  departures: TrainDeparture[]
}

export interface Dashboard {
  generated_at: string | null
  sources: Record<string, string>
  weather: Weather | null
  transit: Transit | null
  train: Train | null
}
