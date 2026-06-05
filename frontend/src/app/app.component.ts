import { Component } from '@angular/core';
import { CityListComponent } from './components/city-list/city-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CityListComponent],
  template: `<app-city-list />`,
})
export class AppComponent {}
