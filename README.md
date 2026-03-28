# Briar forum sharing

В репозитории есть два способа делиться форумами Briar:

- `share_briar_forum.py` — CLI-скрипт для генерации share-ссылки.
- Веб-страница (`index.html`) — простой сайт с формой, копированием ссылки и скачиванием JSON.

## 1) CLI-скрипт

```bash
./share_briar_forum.py tech-room-42 "Tech Room" "@alice" \
  --description "Обсуждаем open-source и безопасность" \
  --tag security --tag foss \
  --output forum_share.json
```

## 2) Сайт для дележа форумами

Запуск локально:

```bash
python3 -m http.server 8000
```

Откройте `http://localhost:8000` в браузере, заполните форму и нажмите
**«Сгенерировать ссылку»**.

Сайт умеет:
- собирать payload форума;
- генерировать ссылку `briar-forum://share/...`;
- копировать ссылку и markdown;
- скачивать JSON с payload и ссылкой.
