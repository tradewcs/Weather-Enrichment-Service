export interface WeatherData {
  temperature: number;
  feels_like: number;
  humidity: number;
  description: string;
  wind_speed: number;
  fetched_at: string;
}

export interface City {
  id: number;
  name: string;
  created_at: string;
  weather: WeatherData | null;
}
