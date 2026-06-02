# AI Telegram Assistant для «Центр Красок #1»

Готовый MVP Telegram-бота с AI-ассистентом, который отвечает на вопросы о компании в формате обычного чата: без команд, кнопок и меню. Пользователь пишет вопрос, бот ищет релевантные факты в локальной базе знаний и передает их в AI API вместе с guardrails, чтобы ответ был связан с компанией и не превращался в выдумку.

## Что реализовано

- обычный Telegram-чат на `aiogram`;
- OpenAI-compatible AI API через пакет `openai`;
- локальная база знаний о «Центр Красок #1»;
- простой RAG: поиск релевантных фактов по ключевым словам и тегам;
- короткая память диалога на каждый чат;
- системный prompt с ограничениями против галлюцинаций;
- отказ от ответа, если вопрос не связан с базой знаний;
- fallback-ответ по базе знаний, если AI API не подключен;
- тесты retrieval, fallback и памяти диалога;
- подробная инструкция запуска и адаптации.

## Предположения

- Бот работает как MVP в режиме polling, без webhook и без CRM.
- Информация о компании подготовлена вручную из открытых источников.
- Цены, наличие, акции, вакансии и сроки доставки не считаются стабильными данными; бот должен отправлять пользователя на сайт или к менеджеру.
- Для production можно заменить память в процессе на Redis/PostgreSQL и добавить webhook, мониторинг и автоматическое обновление базы знаний.

## Структура проекта

```text
.
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── company_knowledge.json
│   └── sources.md
├── docs/
│   ├── architecture.md
│   └── demo.md
├── src/
│   └── assistant_bot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── ai_client.py
│       ├── bot.py
│       ├── config.py
│       ├── knowledge_base.py
│       ├── memory.py
│       └── prompts.py
├── scripts/
│   └── run_bot.ps1
└── tests/
    ├── test_ai_client.py
    ├── test_knowledge_base.py
    └── test_memory.py
```

## Компоненты

`src/assistant_bot/bot.py` — точка Telegram-интеграции. Принимает текстовые сообщения, показывает `typing`, вызывает AI-клиент и отправляет ответ.

`src/assistant_bot/ai_client.py` — оркестратор ответа. Сначала ищет факты в базе знаний, затем либо вызывает AI API, либо возвращает локальный fallback.

`src/assistant_bot/knowledge_base.py` — загрузка JSON-базы, токенизация, поиск по ключевым словам, тегам и небольшим расширениям запроса.

`src/assistant_bot/prompts.py` — личность ассистента, правила ответа, тексты отказа и обертка контекста компании.

`src/assistant_bot/memory.py` — короткая история сообщений на чат. Для MVP хранится в памяти процесса.

`src/assistant_bot/config.py` — загрузка `.env`: токены, модель, endpoint, путь к базе знаний и лимиты.

`data/company_knowledge.json` — структурированная информация о компании, источники и факты для RAG.

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Заполните `.env`:

```env
TELEGRAM_BOT_TOKEN=your_botfather_token
OPENAI_API_KEY=your_ai_api_key
OPENAI_MODEL=gemini-2.5-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
KNOWLEDGE_PATH=data/company_knowledge.json
MAX_HISTORY_MESSAGES=8
TOP_K_FACTS=5
MAX_ANSWER_CHARS=3500
```

`OPENAI_BASE_URL` можно оставить пустым для OpenAI или указать совместимый endpoint другого провайдера.

## Запуск

```powershell
python -m src.assistant_bot
```

Альтернативно:

```powershell
python -m src.assistant_bot.bot
```

На Windows также можно использовать:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_bot.ps1
```

## Проверка

```powershell
python -m unittest discover -s tests
python -m compileall src
```

## Примеры вопросов

- Чем занимается компания?
- Какие услуги предоставляет?
- Где находится офис?
- Какие бренды есть?
- Что есть для дизайнеров?
- Какие условия для строителей?
- Какие есть вакансии?
- Какой Instagram у компании?

## Как бот ограничивает галлюцинации

1. Вопрос сначала проходит локальный поиск по базе знаний.
2. Если фактов не найдено, AI API не вызывается.
3. В модель передаются только найденные фрагменты, а не вся база.
4. System prompt запрещает выдумывать цены, остатки, акции, вакансии и сроки доставки.
5. При отсутствии AI API бот все равно отвечает по найденным фактам, чтобы можно было проверить MVP локально.

## Использованные источники

Основные источники перечислены в `data/company_knowledge.json` и `data/sources.md`:

- https://centr-krasok.kz/
- https://centr-krasok.kz/about/
- https://centr-krasok.kz/about/contacts/
- https://centr-krasok.kz/designers/
- https://centr-krasok.kz/for_builders/
- https://centr-krasok.kz/brands/
- https://centr-krasok.kz/news/
- https://astana.hh.kz/employer/3943302

GitHub-репозиторий `Nusultan11/telegrambot-centrekrasok` использован только как референс идей: RAG-подход, разделение ответственности, guardrails, тесты и документация. Код, структура файлов и тексты в этом решении написаны самостоятельно.

## Что нужно изменить под моего бота

### Файлы, которые потребуется изменить

- `.env` — реальные токены и настройки запуска.
- `data/company_knowledge.json` — факты, источники и ограничения именно вашей компании.
- `src/assistant_bot/prompts.py` — личность, стиль, правила и сценарии поведения ассистента.
- `src/assistant_bot/knowledge_base.py` — логику поиска, если вашей базе нужны другие теги, синонимы или формат данных.
- `src/assistant_bot/ai_client.py` — модель, параметры генерации и дополнительные проверки ответа.
- `src/assistant_bot/bot.py` — поведение Telegram-бота, если нужны команды, кнопки, медиа, webhook или интеграция с CRM.
- `README.md` и `docs/` — описание проекта, источников и инструкции для сдачи/деплоя.

### Переменные и секреты

Замените в `.env`:

- `TELEGRAM_BOT_TOKEN` — токен вашего Telegram-бота из BotFather.
- `OPENAI_API_KEY` — ключ OpenAI или совместимого AI-провайдера.
- `OPENAI_MODEL` — модель, например `gemini-2.5-flash` или модель вашего провайдера.
- `OPENAI_BASE_URL` — endpoint совместимого API, если используется не OpenAI.
- `KNOWLEDGE_PATH` — путь к вашей базе знаний, если файл переименован.
- `MAX_HISTORY_MESSAGES` — сколько сообщений хранить в контексте.
- `TOP_K_FACTS` — сколько фактов передавать в AI.
- `MAX_ANSWER_CHARS` — максимальная длина ответа.

### Где находится логика поведения бота

- Telegram handlers: `src/assistant_bot/bot.py`.
- Сбор ответа: `src/assistant_bot/ai_client.py`.
- Поиск фактов: `src/assistant_bot/knowledge_base.py`.
- История диалога: `src/assistant_bot/memory.py`.
- Тексты отказов и личность ассистента: `src/assistant_bot/prompts.py`.

### Где настраиваются промпты, сценарии и личность

Основной prompt лежит в `src/assistant_bot/prompts.py`.

Изменяйте:

- название компании;
- тон общения;
- запреты и разрешенные темы;
- правила отказа;
- текст для нетекстовых сообщений;
- поведение при недостатке информации.

### Что завязано на примере «Центр Красок #1»

- все факты в `data/company_knowledge.json`;
- название компании в `src/assistant_bot/prompts.py`;
- тексты отказов в `src/assistant_bot/prompts.py`;
- примеры вопросов в `README.md`;
- тесты, которые проверяют бренды, адреса, вакансии и контакты;
- синонимы в `QUERY_EXPANSIONS` внутри `src/assistant_bot/knowledge_base.py`.

### Пошаговая адаптация

1. Создайте своего бота в BotFather и получите `TELEGRAM_BOT_TOKEN`.
2. Выберите AI-провайдера и получите `OPENAI_API_KEY`.
3. Соберите факты о вашей компании: сайт, соцсети, контакты, услуги, FAQ, ограничения.
4. Замените содержимое `data/company_knowledge.json`, сохранив формат `sources` и `facts`.
5. В каждом факте заполните `id`, `title`, `tags` и `text`; теги должны отражать реальные вопросы пользователей.
6. Обновите `src/assistant_bot/prompts.py`: название, тон, правила, запреты и темы.
7. При необходимости расширьте `QUERY_EXPANSIONS` в `src/assistant_bot/knowledge_base.py`.
8. Обновите тесты в `tests/`, чтобы они проверяли уже вашу компанию.
9. Запустите `python -m unittest discover -s tests`.
10. Запустите бота командой `python -m src.assistant_bot` и проверьте вопросы в Telegram.
