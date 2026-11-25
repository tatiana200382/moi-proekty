# Инструменты GitHub для Flowwow и карточек маркетплейсов

**Дата проверки:** 09.11.2026, 22:30–22:45 MSK.  
**Контекст:** Silver Song Flowers, СПб, магазин `silversong-flowersf-4152`, 20–50 карточек, 1–3 заказа в месяц, бюджет продвижения 10 000 ₽/мес. Сотрудник работает только с черновиками: без публикации, оплат и записи в кабинет.  
**Что сделано:** поиск по GitHub API, README и деревьям файлов, проверка PyPI/npm, официальной документации Flowwow, статический разбор кода. **Ни один репозиторий не запускался и не устанавливался.**

## Коротко

- По запросу `flowwow` — **51 репозиторий**, но живого инструмента для seller API почти нет: один специализированный клиент, несколько парсеров и учебные тестовые задания.
- Официального SDK Flowwow нет: в организации `flowwow` 14 публичных репозиториев, среди них платёжный клиент и инфраструктура, но не seller API.
- В официальном API есть `products/create` и `products/update`, **но поля «черновик» в схеме нет**. Это запись в каталог, а не локальный черновик; сотруднику с политикой «только черновики» эти методы давать нельзя.
- Из 18 отобранных инструментов: **2 — взять**, **6 — адаптировать**, **10 — отклонить**. Три реальных кандидата — `seller-skills-ru`, `WB-OZON-AI-TEAM` и `nt-flowwow-seller-client` (последний как read-only референс, не как зависимость).

## Как искали

Запросы к GitHub API (`/search/repositories`, без токена): `flowwow` (51), `flowwow api` (1), `flowwow seller` (2), `флаувау` (0), `flowwow parser` (3), `flowwow bot` (0), `flowwow in:readme` (94). Дополнительно — `flowwow.com in:readme`, `topic:flowwow`, запросы по Wildberries/Ozon/Яндекс Маркету и карточкам товаров.

Проверены:
- GitHub-организация `flowwow` и все её публичные репозитории;
- PyPI: пакет `nt-flowwow-seller-client` (v0.3.0), пакета `flowwow` нет (404);
- npm: поиск `flowwow` — **0 пакетов**;
- официальная документация API: `https://seller-docs.flowwow.com/5.-instrumenty-prodavca/5.1-dokumentaciya-i-podderzhka-po-api/otkrytoe-api-dlya-prodavcov-0.0.1.md`.

Ограничения: поиск по коду GitHub без токена недоступен, поэтому исходники смотрели вручную по дереву файлов и raw-файлам. Звёзды и даты коммитов — снимок на 09.11.2026; `0` означает ноль звёзд, а не «нет данных». Лицензионный разбор — не юридическая консультация.

## Важная поправка по API

В документации, кроме методов из вводной (shops / products / reviews / stocks), есть:

- `POST /apiseller/products/create` — создание товара;
- `POST /apiseller/products/update` — изменение товара (нужно передавать все поля, частичного обновления нет);
- `POST /apiseller/products/archive`, `/unarchive`, `/hide`, `/unhide`, `/setTop18`;
- `POST /apiseller/categories/subCategoryProperties` — схема обязательных полей подкатегории;
- `POST /apiseller/products/offersMappings`, `GET /apiseller/orders/view`, `GET /apiseller/orders/list`.

**Черновика в API нет.** В `OfferCreateItem` обязательны `offerId`, `productType`, `name`, `price`, `images`, для основного товара — `subCategoryId`; поля `isActive`/`draft` нет. Создание и обновление — это запись в каталог, а не сохранение черновика. Для нашей политики «сотрудник только готовит черновики» подходят только чтение и локальные файлы.

Наш клиент [`flowwow-api.mjs`](../tools/flowwow-api.mjs) уже покрывает `ping`, `shops`, `products`, `reviews`, `stocks` и не содержит записи. Ему не хватает чтения `categories/subCategoryProperties` и пагинации отзывов; это стоит добавить. `products/create|update|hide|unhide|stocks/put` добавлять нельзя.

## Таблица 1. Flowwow-специфичные инструменты

| № | Инструмент | Автор | ★ | Последний коммит | Лицензия | Язык | Что делает | Зависимости | Ключи | Риски | Вердикт |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [nt-flowwow-seller-client](https://github.com/Melyohin-AA/nt-flowwow-seller-client) | Melyohin-AA | 0 | 2026-10-12 | MIT | Python | Асинхронный клиент seller API: shops, products, offersMappings, hide/unhide, stocks/put, orders | Python ≥3.10, `aiohttp` | Flowwow JWT | 0★, один автор; нет reviews, categories, create/update; есть write-методы | **Адаптировать**: взять read-only референс, не зависимость |
| 2 | [flowwow-shop-stat-go](https://github.com/aelphias/flowwow-shop-stat-go) | aelphias | 0 | 2026-02-28 | MIT | Go | Скрейпит публичный счётчик покупок, отзывы и рейтинг магазина, пишет SQLite, шлёт сводку в Telegram | Go 1.24, `chromedp`, SQLite, `godotenv` | Telegram bot token + chat_id | 0★, нет тестов; селекторы публичной страницы ломаются; Chrome; ToS-риск | **Адаптировать** идею, переписать под Node |
| 3 | [flowwow_stat](https://github.com/aelphias/flowwow_stat) | aelphias | 0 | 2026-02-15 | нет | TypeScript | То же на Puppeteer: счётчик покупок → SQLite → Telegram + графики | Node ≥18, `puppeteer`, `better-sqlite3` | Telegram bot token + chat_id | Нет лицензии; 0★; Puppeteer; хрупкий парсинг | **Отклонить** (идея уже есть в №2) |
| 4 | [flower-catalog-ai](https://github.com/aqwarius2003/flower-catalog-ai) | aqwarius2003 | 0 | 2026-10-16 | MIT | Python | Wordstat → кластеризация → парсинг Flowwow → Gemini-названия/описания → rembg-фото → Streamlit | Python ≥3.12, Streamlit, `google-genai`, Patchright, Scrapling, rembg/onnxruntime | Yandex Cloud key + folder, Gemini key, Serper key | Анти-детект и обход Turnstile; 3 платных API; один коммит; Москва захардкожена | **Адаптировать** только Wordstat + LLM-промпт, без скрапера |
| 5 | [aromatny-flowwow-public-audit](https://github.com/tophqru/aromatny-flowwow-public-audit) | tophqru | 0 | 2026-10-31 | нет | Python + JSON/JPEG | Публичный каталог 66 карточек чужого магазина: product.json, 435 JPEG, QA-workflow | Python + GitHub Actions; ~97 МБ данных | Нет (CI — `GITHUB_TOKEN`) | Нет лицензии; чужие фото/данные; нельзя переиспользовать | **Отклонить** как код/данные; структура аудита — пример |
| 6 | [Parser_Flowwow](https://github.com/citizen322/Parser_Flowwow) | citizen322 | 0 | 2025-01-09 | нет | JavaScript | Selenium-парсер товаров Flowwow (торты, выпечка) в Excel | Node, `selenium-webdriver`, `xlsx` (не объявлены) | Нет | Нет лицензии; зависимости не объявлены; старый Selenium | **Отклонить** |
| 7 | [flowwow-parser](https://github.com/TomiksOfficial/flowwow-parser) | TomiksOfficial | 0 | 2024-06-01 | нет | Go | Colly/Selenium-парсер Flowwow по Вологде, выгрузка в JSON | Go, `colly`, `selenium`; chromedriver в репозитории | Нет | Нет лицензии; 386 КБ chromedriver; 2024; Windows-сборка | **Отклонить** |
| 8 | [Calculator_flowwow](https://github.com/ARK700/Calculator_flowwow) | ARK700 | 0 | 2021-02-24 | нет | HTML/JS | Калькулятор цены букета с коэффициентом 0,651 | Нет | Нет | Нет лицензии; коэффициент 0,651 не подтверждён; 2021 | **Отклонить** |

## Таблица 2. Инструменты для маркетплейсов, применимые к Flowwow

| № | Инструмент | Автор | ★ | Последний коммит | Лицензия | Язык | Что делает | Зависимости | Ключи | Риски | Вердикт |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 9 | [ru-marketplace-mcp](https://github.com/Vladimir-Human/ru-marketplace-mcp) | Vladimir-Human | 185 | 2026-11-08 | MIT | Python | MCP-серверы к 12 площадкам: карточки, цены, отзывы, рейтинги; только чтение | Python ≥3.12, `uv`, MCP, Playwright/Chrome CDP | Нет; опционально MPStats cookie | Flowwow нет; запускает локальный Chrome; 16 пакетов; Ozon/Авито иногда требуют браузер | **Адаптировать** для сравнения цен на цветы в Яндекс Маркете/Ozon |
| 10 | [marketplaces-mcp-ru](https://github.com/ilyautov/marketplaces-mcp-ru) | ilyautov | 61 | 2026-10-07 | MIT | Python | MCP к кабинетам WB/Ozon/Яндекс Маркета/Авито: 1022 метода, продажи, остатки, цены, отзывы | Python ≥3.10, `mcp`, `httpx`, `pyyaml` | WB/Ozon/YM/Avito токены | Flowwow нет; есть write-методы (`confirm_write`); много токенов; сложно ограничить | **Отклонить** для текущей задачи; архитектура MCP — референс |
| 11 | [yandex-tools-mcp](https://github.com/seyka-ai/yandex-tools-mcp) | seyka-ai | 70 | 2026-10-28 | MIT | JavaScript | MCP к Wordstat, Search, Webmaster, Metrika, Direct | Node/Bun, MCP SDK, `npx` | Yandex Cloud API key + folder; OAuth для остальных | Wordstat ≠ поиск Flowwow; платный ключ; не про карточки напрямую | **Адаптировать** для семантики и сезонности |
| 12 | [BormoStats](https://github.com/Bormotoon/BormoStats) | Bormotoon | 3 | 2026-11-06 | GPL-3.0 | Python | Self-hosted аналитика, юнит-экономика, остатки, реклама, репрайсер для WB/Ozon/YM | Docker, Python 3.14, FastAPI, ClickHouse, Redis, Celery, React | Много токенов + admin/DB/Telegram | GPL; тяжёлый стек; write-репрайсер; избыточно для 1–3 заказов | **Отклонить** (вернуться при росте) |
| 13 | [MarketplacesGoodsTracker](https://github.com/TimNekk/MarketplacesGoodsTracker) | TimNekk | 29 | 2026-10-28 | GPL-3.0 | Python | Трекер цен и остатков WB/Ozon → Google Sheets | Python 3.12, Playwright, camoufox, `gspread`, Google `creds.json` | Google service account, логины WB/Ozon, прокси | GPL; anti-detect; Google-креды; Flowwow нет | **Отклонить** |
| 14 | [ai-wildberries-review-responder](https://github.com/eslazarev/ai-wildberries-review-responder) | eslazarev | 19 | 2026-09-12 | MIT | Python | AI-ответы на отзывы WB: читает, генерирует, публикует | Python, `wildberries-sdk`, `openai`, `pydantic`; Docker/Helm | WB token + LLM key | WB-only; пишет ответы; текст отзыва уходит в LLM и в логи; Flowwow нет | **Адаптировать** только генератор черновиков, без отправки |
| 15 | [EasyFeedback](https://github.com/sosukii/EasyFeedback) | sosukii | 18 | 2025-05-11 | нет | Vue/TypeScript | Веб-панель чтения и ответов на отзывы WB | Vue 3, Quasar, axios; внешний backend | WB token вводится в браузере | Нет лицензии; токен уходит на чужой backend (`easy-feedback.up.railway.app`); WB-only | **Отклонить** по безопасности |
| 16 | [marketplace-parser](https://github.com/krein15/marketplace-parser) | krein15 | 3 | 2026-11-05 | MIT | Python | Windows-парсер карточек, цен и отзывов WB/Ozon/ЯМ + Alibaba в Excel | Python, `customtkinter`, Patchright, `openpyxl`, Pillow | Нет; опционально прокси/Telegram | Windows-only; anti-detect; 3★; Flowwow нет | **Отклонить** для нашего стека; формат отчёта — пример |
| 17 | [WB-OZON-AI-TEAM](https://github.com/codebywater/WB-OZON-AI-TEAM) | codebywater | 2 | 2026-11-02 | MIT | Markdown/Python | 15 skill-файлов: карточка, отзывы, юнит-экономика, цены, конкуренты | Markdown; `install.sh` | Нет | Промпты, не код; 2★; `install.sh` делает `rm -rf`; правила WB/Ozon, не Flowwow | **Взять** только skill-файлы |
| 18 | [seller-skills-ru](https://github.com/ilyautov/seller-skills-ru) | ilyautov | 0 | 2026-09-19 | MIT | Markdown | 6 skill-файлов: карточка, остатки, продажи, юнит-экономика, Авито, прайсы | Markdown; нужен `marketplaces-mcp-ru` | Ключи через MCP | 0★; требует MCP/токены; write через `confirm_write`; правила WB/Ozon | **Взять** как скелет, адаптировать под Flowwow |

## Безопасность

Проверяли статически: чтение секретов, внешние домены, методы записи, запуск процессов/браузера. Код не запускали.

| Инструмент | Секреты | Наружу | Запись в кабинет | Процессы/браузер | Вывод |
|---|---|---|---|---|---|
| `nt-flowwow-seller-client` | JWT передаёт вызывающий | только `apis.flowwow.com` | `hide/unhide`, `stocks/put` | нет | Безопасен как read-only; write-методы не давать |
| `flowwow-shop-stat-go` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | `api.telegram.org` | нет | Chrome через `chromedp` | Публичный скрапер, не кабинет |
| `flowwow_stat` | Telegram-токен из `.env` | Telegram | нет | Puppeteer | Нет лицензии; `.env` читается |
| `flower-catalog-ai` | `YANDEX_CLOUD_API_KEY`, `GEMINI_API_KEY`, `SERPER_API_KEY` | Yandex, Gemini, Serper | нет | Patchright/Scrapling, обход Turnstile | Высокий риск: анти-детект + три внешних API |
| `ru-marketplace-mcp` | нет | 12 площадок | нет (read-only) | `subprocess.Popen` запускает Chrome | Локальный Chrome, Flowwow нет |
| `marketplaces-mcp-ru` | WB/Ozon/YM/Avito токены из env или `~/.marketplace-mcp` | официальные API | да, `write_method`/`write_raw` с `confirm_write` | нет | Write-методы есть; сотруднику не давать |
| `ai-wildberries-review-responder` | WB token + LLM key | WB + LLM | да, `publish_reply` | нет | Текст отзыва уходит в LLM; ответ логируется |
| `BormoStats` | много токенов, admin/DB/Telegram | официальные API | да, dry-run по умолчанию | Docker/скрипты, `subprocess` в perf-скриптах | Тяжёлый; GPL; избыточно |
| `TimNekk` | Google `creds.json`, логины WB/Ozon | Google Sheets + площадки | нет | Playwright/camoufox | Anti-detect; GPL; Google-креды |
| `EasyFeedback` | WB token в браузере | чужой backend | да, ответ на отзыв | нет | Токен третьей стороне — отклонить |
| `krein15` | нет | площадки, Telegram | нет | Patchright | Anti-detect; Windows-only |
| `WB-OZON-AI-TEAM` | нет | нет | нет | `install.sh`, `rm -rf` | Брать только `.md`, установщик не запускать |
| `seller-skills-ru` | нет | через MCP | да, через `confirm_write` | нет | Промпты; ключи и запись — вне контура сотрудника |
| `topq` | нет | GitHub Actions | нет | Actions | Данные без лицензии |

Отдельно:

- **`install.sh` в `WB-OZON-AI-TEAM`** удаляет одноимённые папки в каталоге скиллов: `rm -rf "$DEST_DIR/$name"` (`install.sh#L28`). Если запускать — только с пустым/отдельным каталогом.
- **`EasyFeedback`** принимает WB-токен в веб-форме и отправляет его на сторонний backend. Для нас это готовый пример того, чего делать нельзя.
- **`flower-catalog-ai`** прямо заявляет обход антифрод-систем и Cloudflare Turnstile. Даже если код MIT, использование на Flowwow — риск блокировки и нарушения правил площадки.
- **`marketplaces-mcp-ru`** имеет не только чтение, но и `write_method`, `write_raw`, `delete_method`. Кнопка `confirm_write` защищает от случайной записи, но не от того, что сотрудник её нажмёт.
- **`nt-flowwow-seller-client`** чистый по сети и секретам, но содержит `set_product_active` и `update_stocks`. Если брать — только чтение, write-методы вырезать или не импортировать.
- **`ai-wildberries-review-responder`** логирует сгенерированный ответ (`logger.info("Generated reply {}", reply)`) — это текст, который может содержать данные покупателя.
- **`BormoStats`** по умолчанию dry-run, но включает боевой режим `MARKETPLACE_ACTIONS_ENABLED=true`; это уже не «только аналитика».

## Что реально стоит взять

### 1. `seller-skills-ru` — скелет навыка карточки

MIT, без кода и зависимостей, 6 готовых skill-файлов. `skills/product-listing/SKILL.md` почти один в один совпадает с нашей задачей: собрать карточку, показать черновик до выгрузки, не выдумывать характеристики, писать `[уточнить]`. Берём структуру и дисциплину, меняем площадку и правила на Flowwow. Не подключаем MCP и не даём write-инструменты.

### 2. `WB-OZON-AI-TEAM` — примеры аудита и ответов на отзывы

MIT, 16 навыков и 9 разобранных примеров. Особенно полезны `skills/marketplace-card/SKILL.md` и `docs/examples/07-marketplace-card.md`: формат «было → проблема → стало», проверка капса/запрещённых слов, отдельный блок «что уточнить». Берём только `.md`; `install.sh` не запускаем. Правила WB/Ozon переписываем под Flowwow.

### 3. `nt-flowwow-seller-client` — read-only референс API

MIT, единственный специализированный клиент. Берём не как зависимость (Python/asyncio, 0★, нет reviews/categories), а как карту методов, пагинации, валидации и ошибок. По нему стоит дополнить `flowwow-api.mjs` чтением `categories/subCategoryProperties` и пагинацией отзывов. `products/create|update`, `hide/unhide`, `stocks/put` не переносим.

**Почему не остальные:** парсеры — хрупкие и с ToS-риском; `BormoStats` — инфраструктура не по размеру; `marketplaces-mcp-ru` — чужие кабинеты и write; `topq` — без лицензии; `flower-catalog-ai` — анти-детект и три платных API; `EasyFeedback` — токен у третьей стороны.

## Что придётся написать самим

1. **`tools/inventory.mjs`** — read-only инвентаризация 20–50 карточек: `shops` → `products?shopId=4152&withStats=true` (пагинация по 50), `reviews`, `stocks`; выгрузка в JSON/CSV. Добавить `categories/subCategoryProperties`, чтобы видеть обязательные поля подкатегории.
2. **`tools/card-lint.mjs`** — линтер карточки по правилам из `knowledge.md`: название без капса/цен/эмодзи, описание пятью блоками, обязательные поля, фото (JPEG/PNG, 1200×1200, 1:1, до 6, до 10 МБ), запрещённые фразы. Формат вывода: «было → проблема → стало» + `[уточнить]`.
3. **`tools/review-drafts.mjs`** — чтение отзывов, классификация (оценка/текст/фото), 2–3 варианта ответа. Автоотправки нет: в известной документации API нет метода ответа на отзыв, только `answerShop` в ответе. Черновик отправляет человек в приложении.
4. **`tools/promo-calc.mjs`** — сценарии для 10 000 ₽: CPC, CTR, конверсия, средний чек, комиссия. Комиссия и доставка — **нет данных**, поэтому только диапазоны и пометка «оценка», без гарантий.
5. **Локальное хранилище черновиков** — `research/drafts/*.json` + Markdown. Причина: в API нет статуса «черновик»; `create/update` — это запись в каталог. Черновик живёт у нас, сотрудник переносит его в приложение вручную.
6. **Токен и доступ** — `FLOWWOW_TOKEN` или `~/.config/flowwow/token` с правами 600; отдельный read-only токен, если API позволяет scopes; в клиенте — allowlist методов и запрет `POST/PUT` на write-пути. Токен не передавать в LLM и не логировать.

## План на 2 недели

1. Взять два MIT-навыка, скопировать `LICENSE` и адаптировать `product-listing` под Flowwow (1–2 часа).
2. Добавить в `flowwow-api.mjs` чтение категорий и пагинацию, проверить на токене/скриншотах.
3. Собрать инвентаризацию 20–50 карточек, прогнать линтер, выбрать 5 худших.
4. Переписать 3 карточки целиком, отправить на модерацию вручную, замерить просмотры/корзины за 30 дней.
5. Только после данных — промо-план на 10 000 ₽; тяжёлую аналитику не покупать.

## Найденное, но не вошло в таблицу

- **Организация `flowwow`** — 13 репозиториев, seller SDK нет: [cloudpayments-php-client](https://github.com/flowwow/cloudpayments-php-client) (21★, MIT, платежи), `yii`, terraform-модули, `php-fpm_exporter`, `amocrm-api-php` и т.п.
- [flowwow-feed](https://github.com/AVD-fw/flowwow-feed) — XML-фиды поставщиков цветов, без кода и лицензии; не инструмент, но пример формата фида.
- [flowwow-seller-academy](https://github.com/VasilevaK/flowwow-seller-academy) — только README, кода нет.
- [Danila133/flowwow](https://github.com/Danila133/flowwow) — пустой репозиторий, 11★ (шум поиска).
- [Flowwow-QR](https://github.com/xomke/Flowwow-QR) — генератор QR-ссылок, к карточкам/аналитике не относится.
- [scraping_flowwow_com](https://github.com/webrodda/scraping_flowwow_com) — Python/Selenium 2022, 12 МБ `chromedriver.exe`, без лицензии.
- [flowwow-it-support](https://github.com/ostresh/flowwow-it-support) — тестовое задание «курсы валют», к Flowwow не относится.
- [Avito-Eye-Flowwow-Concept](https://github.com/yurixui/Avito-Eye-Flowwow-Concept) — концепт, не инструмент.
- Тестовые задания Flowwow (PHP/Python, 2022–2026) — не продукты, в сравнение не брались.

## Ограничения

- Звёзды и даты — на 09.11.2026; они быстро меняются.
- README-заявления не проверялись запуском. Оценка «работает/не работает» — только по коду и структуре.
- Комиссия Flowwow, выдача токена, правила промо — **нет данных**; в расчётах это помечено.
- Юридическая оценка лицензий и ToS — не консультация; перед копированием кода/данных нужен юрист.

## Резюме (12 строк)

1. По `flowwow` на GitHub 51 репозиторий, но живого инструмента для seller API почти нет.
2. Официального SDK нет: в org `flowwow` только платежи и инфраструктура.
3. Единственный специализированный клиент — `nt-flowwow-seller-client` (MIT, 0★), без отзывов и категорий.
4. В API есть `products/create` и `products/update`, но поля «черновик» нет — это запись в каталог.
5. Наш `flowwow-api.mjs` уже читает shops/products/reviews/stocks; не хватает категорий.
6. Публичные счётчики парсят два проекта, оба хрупкие и с ToS-риском.
7. `flower-catalog-ai` — идея Wordstat + LLM, но анти-детект и три платных API.
8. `aromatny-flowwow-public-audit` — хороший пример структуры аудита, но без лицензии.
9. Для карточек полезны два MIT-набора: `seller-skills-ru` и `WB-OZON-AI-TEAM`.
10. Брать: эти два навыка + `nt-flowwow-seller-client` как read-only референс.
11. Самим: инвентаризация, линтер карточек, черновики ответов, промо-калькулятор.
12. При 1–3 заказах и 10 000 ₽/мес тяжёлая аналитика не нужна — сначала качество 20–50 карточек.
