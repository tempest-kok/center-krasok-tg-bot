# Архитектура

MVP построен как небольшой Telegram worker.

Поток обработки:

```text
Telegram message
  -> bot.py
  -> InMemoryDialogStore
  -> KnowledgeBase.search
  -> AIClient.answer
  -> OpenAI-compatible API или local fallback
  -> Telegram reply
```

Ключевые решения:

- `aiogram` выбран для асинхронной работы с Telegram Bot API.
- База знаний хранится в JSON, чтобы ее можно было редактировать без изменения кода.
- Поиск реализован прозрачно: токены, теги и небольшие расширения запроса.
- AI API вызывается только при наличии релевантных фактов.
- Память диалога ограничена, чтобы не раздувать prompt и не тащить лишние данные.
- В production память можно заменить на Redis, а polling — на webhook.
