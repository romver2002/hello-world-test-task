# Heroes API — FastAPI (async) + SQLAlchemy 2 (async) + psycopg3

## Запуск
1) Скопируйте `.env.example` → `.env` и задайте:
```

DATABASE\_URL=postgresql+psycopg://heroes\:heroes\@db:5432/heroes
SUPERHERO\_TOKEN=<токен из [https://superheroapi.com/>](https://superheroapi.com/>)

````
2) `docker compose up --build`
3) Swagger: http://localhost:8000/docs

## Эндпоинты
### POST /hero/
Body:
```json
{ "name": "Batman" }
````

* 201 — создан новый герой, 200 — герой уже есть в БД.
* 404 — внешний API не нашёл героя.

### GET /hero/

Параметры (все необязательные):

* `name` — **точное совпадение**.
* `intelligence | intellegence | strength | speed | power` — **числовые**:

  * точное: `strength=80`
  * больше/равно: `strength=>=80`
  * меньше/равно: `strength=<=90`

Если по фильтрам пусто — 404.

> Параметр `intellegence` (как в ТЗ) поддержан как alias к `intelligence`.

## Тесты

Тесты запускаются на PostgreSQL внутри docker-compose.

1) Собрать и поднять:
```
docker compose build --no-cache
docker compose up -d
```
2) Создать тестовую БД:
```
docker compose exec -T db psql -U heroes -c "CREATE DATABASE heroes_test;"
```
3) Применить миграции (prod БД и тестовая):
```
# основная БД (DATABASE_URL из .env)
docker compose exec api alembic upgrade head

# тестовая БД
docker compose exec -e DATABASE_URL="postgresql+psycopg://heroes:heroes@db:5432/heroes_test" api alembic upgrade head
```
4) Запустить тесты:
```
docker compose exec api pytest -q
```


