import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CityService } from '../../services/city.service';
import { AddCityComponent } from '../add-city/add-city.component';
import { City } from '../../models/city.model';

@Component({
  selector: 'app-city-list',
  standalone: true,
  imports: [CommonModule, AddCityComponent],
  templateUrl: './city-list.component.html',
  styleUrl: './city-list.component.css',
})
export class CityListComponent implements OnInit {
  cities: City[] = [];
  loading = false;
  error = '';
  refreshing: Set<number> = new Set();

  constructor(private cityService: CityService) {}

  ngOnInit() {
    this.loadCities();
  }

  loadCities() {
    this.loading = true;
    this.error = '';

    this.cityService.getCities().subscribe({
      next: (data) => {
        this.cities = data;
        this.loading = false;
      },
      error: () => {
        this.error = 'Failed to load cities.';
        this.loading = false;
      },
    });
  }

  refresh(cityId: number) {
    this.refreshing.add(cityId);

    this.cityService.refreshWeather(cityId).subscribe({
      next: () => {
        setTimeout(() => {
          this.loadCities();
          this.refreshing.delete(cityId);
        }, 4000);
      },
      error: () => {
        this.refreshing.delete(cityId);
      },
    });
  }

  isRefreshing(cityId: number): boolean {
    return this.refreshing.has(cityId);
  }

  formatDate(dateStr: string): string {
    return new Date(dateStr).toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}
