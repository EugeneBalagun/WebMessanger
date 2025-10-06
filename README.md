# Web Messenger - Мессенджер

Полнофункциональный веб-мессенджер с React + FastAPI + PostgreSQL + Docker.

## 🚀 Быстрый старт

```bash
# Клонируйте репозиторий
git clone https://github.com/EugeneBalagun/WebMessanger.git
cd WebMessanger

# Запустите приложение
docker-compose up --build
Доступ после запуска:

📱 Фронтенд: http://localhost:3000

🔧 Бекенд API: http://localhost:8000

📚 Документация API: http://localhost:8000/docs

📋 Реализованные функции
✅ Регистрация и авторизация пользователей (JWT)

✅ Личные чаты один на один

✅ Прикрепление файлов к сообщениям (несколько файлов)

✅ Редактирование и удаление сообщений

✅ Адаптивный дизайн на Tailwind CSS

✅ Полная докеризация приложения

🛠 Технологии
Фронтенд: React 18 + TypeScript + Tailwind CSS

Бекенд: FastAPI + SQLModel + JWT аутентификация

База данных: PostgreSQL

Контейнеризация: Docker + Docker Compose

🎯 Демонстрация работы
Зарегистрируйте двух пользователей

Войдите под первым пользователем

Создайте чат со вторым пользователем

Отправьте сообщения с прикрепленными файлами

Отредактируйте или удалите сообщение

Выйдите из системы

🐳 Docker сервисы
frontend - React приложение (порт 3000)

backend - FastAPI приложение (порт 8000)

db - PostgreSQL база данных (порт 5432)

🔧 Для разработчиков
Backend разработка
bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
Frontend разработка
bash
cd frontend
npm start
📁 Структура проекта
text
WebMessanger/
├── backend/                 # FastAPI приложение
│   ├── app/
│   │   ├── routers/        # API эндпоинты
│   │   ├── models.py       # Модели БД
│   │   └── database.py     # Настройка БД
│   ├── main.py             # Точка входа
│   └── requirements.txt    # Зависимости Python
├── frontend/               # React приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   └── config.ts       # Конфигурация
│   └── package.json        # Зависимости Node.js
└── docker-compose.yml      # Docker конфигурация
📞 API эндпоинты
Метод	Путь	Описание
POST	/register	Регистрация пользователя
POST	/login	Авторизация (JWT)
GET	/chats/	Чаты пользователя
POST	/chats/	Создать чат
GET	/messages/{chat_id}	Сообщения чата
POST	/messages/	Отправить сообщение
PUT	/messages/{id}	Редактировать сообщение
DELETE	/messages/{id}	Удалить сообщение
🐛 Решение проблем
Приложение не запускается:

bash
# Полная пересборка
docker-compose down
docker-compose up --build
Проверить логи:

bash
docker-compose logs backend
docker-compose logs frontend
Проверить контейнеры:

bash
docker-compose ps
👨‍💻 Автор
Eugene Balagun

📄 Лицензия
MIT License

text

**Закоммитьте README:**
```bash
git add README.md
git commit -m "Add comprehensive README in Russian"
git push
