import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CityService } from '../../services/city.service';

@Component({
  selector: 'app-add-city',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './add-city.component.html',
  styleUrl: './add-city.component.css',
})
export class AddCityComponent {
  @Output() cityAdded = new EventEmitter<void>();

  name = '';
  loading = false;
  error = '';

  constructor(private cityService: CityService) {}

  submit() {
    if (!this.name.trim()) return;

    this.loading = true;
    this.error = '';

    this.cityService.addCity(this.name.trim()).subscribe({
      next: () => {
        this.name = '';
        this.loading = false;
        this.cityAdded.emit();
      },
      error: (err) => {
        this.loading = false;
        if (err.status === 409) {
          this.error = 'City already exists.';
        } else {
          this.error = 'Something went wrong. Try again.';
        }
      },
    });
  }
}
