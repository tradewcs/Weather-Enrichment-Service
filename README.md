# Weather-Enrichment-Service
A service for tracking weather across multiple cities

**Версія:** 1.0  

---

## 1. Загальний опис

Веб-застосунок для зберігання списку міст та перегляду актуальної погодної інформації по кожному з них. Погодні дані отримуються асинхронно через зовнішній API та зберігаються в базі даних. Користувач може вручну ініціювати оновлення погоди для окремого міста.

---

## 2. Стек технологій

| Шар | Технологія |
|---|---|
| Backend | Python 3.11+, FastAPI |
| База даних | PostgreSQL 15+, SQLAlchemy 2.x (async) |
| Черга задач | Celery 5.x |
| Брокер | Redis 7+ |
| Зовнішній API | OpenWeatherMap (безкоштовний тариф) |
| Frontend | Angular 17+ |
| Контейнеризація | Docker, Docker Compose |

---

## 3. Архітектура

```
Browser (Angular)
       │
       │ REST API
       ▼
  FastAPI App
       │             ┌──────────┐
       ├───────────▶│  Redis   │◀──── Celery Worker
       │             └──────────┘           │
       ▼                                    ▼
  PostgreSQL ◀──────────────────── (оновлення погоди)
```

**Сервіси у docker-compose:**
- `api` — FastAPI застосунок
- `worker` — Celery worker
- `db` — PostgreSQL
- `redis` — Redis
- `frontend` — Angular (або serve через nginx)

---

## 4. Backend

### 4.1 Моделі бази даних

**Таблиця `cities`**

| Поле | Тип | Опис |
|---|---|---|
| `id` | UUID / serial | Первинний ключ |
| `name` | VARCHAR(100) | Назва міста |
| `created_at` | TIMESTAMP | Дата створення |

**Таблиця `weather_data`**

| Поле | Тип | Опис |
|---|---|---|
| `id` | UUID / serial | Первинний ключ |
| `city_id` | FK → cities.id | Зв'язок із містом |
| `temperature` | FLOAT | Температура, °C |
| `feels_like` | FLOAT | Відчувається як, °C |
| `humidity` | INTEGER | Вологість, % |
| `description` | VARCHAR(255) | Текстовий опис (напр. «ясно») |
| `wind_speed` | FLOAT | Швидкість вітру, м/с |
| `fetched_at` | TIMESTAMP | Час отримання даних |

### 4.2 API ендпоінти

#### `POST /cities`
Додати місто.

**Request body:**
```json
{ "name": "Kyiv" }
```

**Відповідь `201 Created`:**
```json
{
  "id": 1,
  "name": "Kyiv",
  "created_at": "2025-01-01T12:00:00Z"
}
```

**Поведінка:** після збереження міста в БД синхронно повертає відповідь і **асинхронно** запускає Celery-задачу `fetch_weather_task(city_id)`.

**Помилки:**
- `422` — валідаційна помилка (назва порожня або > 100 символів)
- `409` — місто з такою назвою вже існує

---

#### `GET /cities`
Отримати список усіх міст з останніми погодними даними.

**Відповідь `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "Kyiv",
    "created_at": "2025-01-01T12:00:00Z",
    "weather": {
      "temperature": 5.2,
      "feels_like": 2.1,
      "humidity": 80,
      "description": "overcast clouds",
      "wind_speed": 4.5,
      "fetched_at": "2025-01-01T12:05:00Z"
    }
  },
  {
    "id": 2,
    "name": "Lviv",
    "created_at": "2025-01-01T11:00:00Z",
    "weather": null
  }
]
```

> `weather: null` — якщо задача ще не виконалась або дані ще не надійшли.

---

#### `POST /cities/{city_id}/refresh`
Вручну тригернути оновлення погоди для міста.

**Відповідь `202 Accepted`:**
```json
{ "message": "Weather update queued", "city_id": 1 }
```

**Помилки:**
- `404` — місто не знайдено

---

### 4.3 Celery-задача

**Назва:** `fetch_weather_task`  
**Брокер / Backend:** Redis

**Логіка виконання:**
1. Отримати назву міста з БД за `city_id`.
2. Зробити запит до OpenWeatherMap API (`/weather?q={city}&appid={key}&units=metric`).
3. Розпарсити відповідь: витягти `temp`, `feels_like`, `humidity`, `description`, `wind_speed`.
4. Зберегти новий запис у таблицю `weather_data`.
5. У разі помилки від зовнішнього API — логувати, не падати.

**Retry-стратегія:** 3 спроби з затримкою 10 с між ними (`autoretry_for=(Exception,), retry_backoff=10, max_retries=3`).

---

### 4.4 Конфігурація

Усі чутливі параметри передаються через `.env`:

```
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/weather_db
REDIS_URL=redis://redis:6379/0
OPENWEATHER_API_KEY=your_key_here
```

---

## 5. Frontend (Angular)

### 5.1 Структура застосунку

```
src/
  app/
    components/
      city-list/       — список міст
      add-city/        — форма додавання
    services/
      city.service.ts  — HTTP-клієнт
    models/
      city.model.ts
```

### 5.2 Функціонал

**Список міст (`CityListComponent`)**
- Завантажує `GET /cities` при ініціалізації.
- Для кожного міста відображає:
  - Назву міста
  - Температуру (або «—» якщо `weather: null`)
  - Вологість
  - Опис погоди
  - Час останнього оновлення
  - Кнопку **«Оновити погоду»**
- Стани: `loading` (спінер), `error` (повідомлення про помилку), `empty` (немає міст).

**Форма додавання (`AddCityComponent`)**
- Текстове поле для назви міста.
- Кнопка **«Додати»** (заблокована, якщо поле порожнє або запит в процесі).
- Після успішного додавання — оновлює список.
- Показує помилку при `409` («Місто вже існує») або мережевій помилці.

**Оновлення погоди**
- По кліку на «Оновити погоду» — `POST /cities/{id}/refresh`.
- Кнопка заблокована під час запиту.
- Після відповіді `202` — показати повідомлення «Оновлення запущено», через 3–5 с перезавантажити список.

### 5.3 HTTP-сервіс (`CityService`)

```typescript
getCities(): Observable<City[]>
addCity(name: string): Observable<City>
refreshWeather(cityId: number): Observable<{ message: string }>
```

Глобальний перехоплювач (interceptor) для обробки `5xx` помилок з виводом загального повідомлення.

---

## 6. Docker Compose

**Сервіси:**

| Сервіс | Image | Порт | Залежності |
|---|---|---|---|
| `db` | `postgres:15` | 5432 | — |
| `redis` | `redis:7-alpine` | 6379 | — |
| `api` | custom build | 8000 | `db`, `redis` |
| `worker` | той самий image що `api` | — | `db`, `redis` |
| `frontend` | custom build (nginx) | 4200/80 | `api` |

Міграції запускаються через `alembic upgrade head` як `command` або окремий `init`-контейнер перед стартом `api`.

---

## 7. Критерії прийому (Definition of Done)

- `docker-compose up` піднімає весь стек без помилок.
- `POST /cities` → місто зберігається, задача ставиться в чергу.
- Через кілька секунд `GET /cities` повертає погодні дані для доданого міста.
- `POST /cities/{id}/refresh` → задача повторно ставиться в чергу.
- Angular-інтерфейс відображає список, дозволяє додати місто та оновити погоду.
- Loading і error стани коректно обробляються на UI.
- Код покритий базовими коментарями; `.env.example` присутній у репозиторії.

---

## 8. Що виходить за скоуп

- Автентифікація та авторизація
- Автоматичне фонове оновлення за розкладом (cron)
- Видалення міст
- Пагінація списку
- Unit та integration тести
- CI/CD pipeline
