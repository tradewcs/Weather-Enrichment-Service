import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { City } from '../models/city.model';

@Injectable({ providedIn: 'root' })
export class CityService {
  private api = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getCities(): Observable<City[]> {
    return this.http.get<City[]>(`${this.api}/cities`);
  }

  addCity(name: string): Observable<City> {
    return this.http.post<City>(`${this.api}/cities`, { name });
  }

  refreshWeather(cityId: number): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.api}/cities/${cityId}/refresh`, {});
  }
}
