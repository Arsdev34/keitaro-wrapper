# Keitaro Wrapper — создание и редактирование тестовых кампаний

Обёртка над Keitaro Admin API для создания и редактирования кампаний по ТЗ.

## Функционал

### Создание кампании (главная страница)

- Ввод: название кампании, код гео, ID оффера.
- Префикс test_khristoforov_ добавляется к имени автоматически.
- Кампании автоматически присваиваются: группа FORTESTS, домен и источник трафика.
- Создаются два потока:
  - Redirect to Google: фильтр по стране в режиме allow с указанным гео, редирект на Google.
  - Offer Stream: тот же фильтр в режиме deny, оффер привязывается со share 100.
- Логика: пользователь из указанной страны уходит на Google, остальные — на оффер.

### Редактор кампаний

- Загрузка потоков кампании по её ID.
- Просмотр офферов в потоках.
- Добавление оффера в выбранный поток и удаление офферов.
- Все изменения сохраняются в Keitaro.

## Технологии

- Python 3.10+
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- Простой фронтенд на HTML/JS (отдаётся самим FastAPI)
- Keitaro Admin API (запросы через curl)

## Запуск

1. Клонировать репозиторий и перейти в папку проекта.
2. Создать виртуальное окружение и установить зависимости:

   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt

3. Создать файл .env в корне проекта (образец — .env.example):

   KEITARO_URL=https://ваш-домен-keitaro
   KEITARO_API_KEY=ваш_api_ключ

4. Запустить сервер: python -m uvicorn app.main:app --reload
5. Открыть в браузере http://127.0.0.1:8000

## База данных

При первом запуске база SQLite создаётся автоматически (SQLAlchemy create_all).
Отдельный шаг миграций не требуется.

## Структура проекта

app/
  main.py           # приложение FastAPI: API и страницы
  models.py         # модели SQLAlchemy
  database.py       # подключение и инициализация БД
  keitaro_client.py # клиент Keitaro Admin API
  static/           # фронтенд (HTML/JS)
requirements.txt
.env.example

## Пример созданных потоков

- Поток Redirect to Google: action_type http, action_payload https://google.com,
  фильтр country / allow / ["MX"].
- Поток Offer Stream: schema landings, фильтр country / deny / ["MX"],
  оффер привязан со share 100.
