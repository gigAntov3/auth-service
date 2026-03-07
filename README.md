# Auth Service API 🔐

Сервис авторизации и управления пользователями с поддержкой email/phone верификации и JWT токенов.

## 🚀 Основные возможности

- Регистрация и вход с выдачей JWT токенов (access + refresh)
- Верификация email и телефона через коды подтверждения
- Управление профилем пользователя
- Защита от брутфорса (лимит попыток ввода кодов)

## 📚 API Endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/v1/auth/register` | Регистрация нового пользователя |
| POST | `/api/v1/auth/login` | Вход в систему |
| POST | `/api/v1/auth/refresh` | Обновление JWT токена |
| POST | `/api/v1/auth/logout` | Выход из системы |

### Верификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/v1/auth/verify/request` | Запрос кода подтверждения |
| POST | `/api/v1/auth/verify/confirm` | Подтверждение кода |

### Пользователи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/v1/users/me` | Получение информации о текущем пользователе |
| PATCH | `/api/v1/users/me` | Обновление профиля |
| POST | `/api/v1/users/me/change-password` | Изменение пароля |
| POST | `/api/v1/users/me/change-email` | Запрос на смену email |

## 🛡️ Безопасность

- **JWT токены**: access token (15 мин), refresh token (7 дней)
- **Хеширование паролей**: bcrypt
- **Rate limiting**: 5 попыток ввода кода, 3 запроса кода в час
- **HTTPS** обязателен в production

## 🚦 Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс создан |
| 400 | Неверные данные |
| 401 | Не авторизован |
| 404 | Ресурс не найден |
| 409 | Конфликт (email/phone уже существует) |
| 429 | Превышен лимит попыток |

## 📦 Технологии

- **Python 3.11+** / **FastAPI**
- **PostgreSQL** / **Redis**
- **SQLAlchemy** / **Alembic**
- **JWT** / **bcrypt**
- **Docker** / **docker-compose**

## 🚀 Быстрый старт

```bash
# Клонирование и запуск
git clone https://github.com/your-org/auth-service.git
cd auth-service
cp .env.example .env
docker-compose up -d

# Или локально
poetry install
poetry run alembic upgrade head
poetry run uvicorn main:app --reload