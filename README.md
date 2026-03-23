# Mini Social API

Асинхронний backend-сервіс на FastAPI для міні-соціальної платформи.

## Реалізований функціонал

### MVP
- реєстрація за email/password
- логін
- JWT access + refresh tokens
- хешування паролів (argon2)
- CRUD постів
- список постів з пагінацією (limit/offset)
- деталі поста
- редагування та видалення тільки автором
- у відповіді поста повертаються author та likes_count
- лайк / анлайк ідемпотентні
- захист від дублювання лайків на рівні БД (unique constraint)

### Додатковий функціонал: Redis
- rate limit на лайки: 30 лайків / 60 секунд на користувача
- кешування GET /posts на 30 секунд
- інвалідація кешу при create/update/delete постів та при like/unlike

## Технології
- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.0 (async)
- Alembic
- Pydantic v2
- Redis
- Docker + docker-compose

## Структура проєкту

```text
app/
  api/            # routers
  core/           # config, security, dependencies
  db/             # session, redis
  models/         # SQLAlchemy models
  repositories/   # db layer
  schemas/        # Pydantic schemas
  services/       # business logic
  utils/          # cache helpers
alembic/
```

## Запуск

1. Створити .env на основі прикладу:

```bash
cp .env.example .env
```

2. Запустити сервіси:

```bash
docker-compose up --build
```

3. Відкрити Swagger:

```text
http://localhost:8000/docs
```

## Тести

### У проєкті реалізовані integration-тести з використанням pytest та httpx, які перевіряють основні сценарії:
- реєстрація та логін
- обробка помилок (400, 401, 409)
- створення та отримання постів
- права доступу (тільки автор може редагувати/видаляти)
- ідемпотентність лайків
- відсутність дублювання лайків

### Запуск тестів:

```bash
docker compose exec api pytest
```

## Основні ендпоінти

### Auth
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`

### Posts
- `POST /api/v1/posts`
- `GET /api/v1/posts`
- `GET /api/v1/posts/{id}`
- `PATCH /api/v1/posts/{id}`
- `DELETE /api/v1/posts/{id}`

### Likes
- `POST /api/v1/posts/{id}/like`
- `DELETE /api/v1/posts/{id}/like`

## Приклади запитів

### Реєстрація
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"strongpass123"}'
```

### Логiн
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"strongpass123"}'
```

### Створення поста
```bash
curl -X POST http://localhost:8000/api/v1/posts \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My first post","content":"Hello world"}'
```

### Лайк поста
```bash
curl -X POST http://localhost:8000/api/v1/posts/1/like \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Важливі зауваження
- refresh token реалізований як stateless і не зберігається в БД
- для конкурентних лайків використовується унікальний індекс (user_id, post_id)
- при повторному лайку сервіс повертає 200 OK
- при анлайку відсутнього лайка сервіс також повертає 200 OK
- валідаційні помилки повертають 400 Bad Request

## Можливі покращення
- зберігання та відкликання refresh token
- більш точкова інвалідація кешу
- додавання unit-тестів
- CI/CD(наприклад, GitHub Actions)
