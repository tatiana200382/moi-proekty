# Выбор инструментов для контента и дизайна — 2026-11-07

Задача владельца: сравнить ~30 решений для маркетинговых постов (продающих и не очень) и визуала, взять лучшие в работу.

Правило: `PRAVILA.md`, раздел «Выбор инструментов». Данные — GitHub API и `raw` файлы, сняты 2026-11-07.

## Критерии

Звёзды и форки · последний коммит (не старше 6 месяцев) · лицензия · открытые issues · документация · вес и зависимости · безопасность.

## Кандидаты и вердикты

### Тексты и посты

| Репозиторий | ★ | Обновлён | Лицензия | Вердикт |
|---|---:|---|---|---|
| [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | 59 021 | 2026-11-06 | MIT | **выбран** — 53 навыка, есть `social` и `copywriting` |
| [Nutlope/hallmark](https://github.com/Nutlope/hallmark) | 50 047 | 2026-11-05 | MIT | **выбран** — анти-AI-slop: проверки «так пишет нейросеть» |
| [heydamir/unslop](https://github.com/heydamir/unslop) | 11 178 | 2026-11-01 | CC-BY-4.0 | отклонён: CC-BY требует атрибуции в каждом посте, дублирует hallmark |
| [rediumvex/social-media-caption-generator-claude](https://github.com/rediumvex/social-media-caption-generator-claude) | 147 | 2026-08-11 | MIT | отклонён: узко и слабее `social` |
| [hookradar/hookradar-agent-skill](https://github.com/hookradar/hookradar-agent-skill) | 4 | 2026-06-17 | MIT | отклонён: 4 звезды, один автор |
| [owainlewis/vertica](https://github.com/owainlewis/vertica) | 18 | 2026-10-15 | MIT | отклонён: карусели, но сырой и без примеров |
| [floger/antigravity-awesome-skills](https://github.com/floger/antigravity-awesome-skills) | каталог | — | — | отклонён: список ссылок, не навык |
| [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills) | каталог | — | — | отклонён: то же |
| [djsydney04/agent-skills](https://github.com/djsydney04/agent-skills) | каталог | — | — | отклонён: то же |
| [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | — | — | — | отклонён: не прочитан, повторов хватает |
| [obra/superpowers](https://github.com/obra/superpowers) | — | — | — | отклонён: инженерные навыки, не маркетинг |

### Дизайн и визуал

| Репозиторий | ★ | Обновлён | Лицензия | Вердикт |
|---|---:|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 188 503 | 2026-11-06 | Apache 2.0 | **выбран** — `canvas-design`: как строить постер и статичную графику |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | 146 445 | 2026-11-07 | MIT | отклонён: про UI и веб, тянет CLI и Python-зависимости |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | 105 291 | 2026-11-07 | Apache 2.0 | отклонён: 23 команды для интерфейсов, избыточно |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | 54 305 | 2026-11-04 | MIT | отклонён: анимации и UI-полировка |
| [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | 28 936 | 2026-11-04 | MIT | отклонён: PPTX/веб, документация на китайском |
| [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 14 598 | 2026-10-25 | MIT | отклонён: общий набор, китайский |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 8 691 | 2026-08-17 | Apache 2.0 | отклонён: работает только с сервисом Stitch |
| [MengTo/Skills](https://github.com/MengTo/Skills) | 7 292 | 2026-11-05 | MIT | отклонён: веб-дизайн, не соцсети |
| [boraoztunc/skills](https://github.com/boraoztunc/skills) | 452 | 2026-11-04 | Apache 2.0 | отклонён: мало звёзд, дублирует выбранное |

### Рендер картинок

| Решение | ★ | Обновлён | Лицензия | Вердикт |
|---|---:|---|---|---|
| **Chrome headless** (уже стоит) | — | — | бесплатно | **выбран** — HTML/CSS в PNG без установки, шрифты и `₽` на месте |
| [vercel/satori](https://github.com/vercel/satori) | 14 167 | 2026-11-06 | MPL-2.0 | отклонён: нужен npm-стек и подгрузка шрифтов |
| [microsoft/playwright](https://github.com/microsoft/playwright) | 99 525 | 2026-11-07 | Apache 2.0 | отклонён: 300+ МБ, для скриншота хватает Chrome |
| [puppeteer/puppeteer](https://github.com/puppeteer/puppeteer) | 95 810 | 2026-11-07 | Apache 2.0 | отклонён: то же |
| [vercel/og-image](https://github.com/vercel/og-image) | 4 035 | **2023-01-20** | MIT | отклонён: заброшен больше года |
| [lovell/sharp](https://github.com/lovell/sharp) | 32 830 | 2026-11-05 | Apache 2.0 | отклонён: сжатие делает Chrome и Pillow |
| [danielgatis/rembg](https://github.com/danielgatis/rembg) | 25 374 | 2026-11-06 | MIT | отклонён: вырезка уже работает через системный Vision, без установки |
| [withoutbg/withoutbg-python](https://github.com/withoutbg/withoutbg-python) | 1 303 | 2026-11-04 | NOASSERTION | отклонён: лицензия неясна |
| [lucide-icons/lucide](https://github.com/lucide-icons/lucide) | — | — | ISC | кандидат на будущее: иконки в SVG |
| [google/fonts](https://github.com/google/fonts) | — | — | OFL | кандидат: шрифты под кириллицу (Golos Text, Playfair Display) |

## Что взято в работу

| Инструмент | Зачем | Файл |
|---|---|---|
| `social` (marketingskills) | посты, карусели, хуки, что публиковать | `skills/social.md` |
| `image` (marketingskills) | графика под пост, сжатие, форматы | `skills/image.md` |
| `marketing-ideas` (marketingskills) | идеи, когда «что ещё попробовать» | `skills/marketing-ideas.md` |
| `canvas-design` (anthropics) | как строить постер и статичную графику | `skills/canvas-design.md` |
| `hallmark` (Nutlope) | проверка «выглядит как нейросеть» и анти-слоп | `skills/hallmark.md` |
| рендер HTML→PNG | типографика, `₽`, шрифты без установки | `tools/render.sh` + `templates/post-card.html` |

## Проверка

Собрана карточка поста: `results/post-card-demo.png` — 1080×1350, палитра бренда, знак `₽` рисуется, шрифт Georgia. Раньше такое собиралось только в Pillow, теперь — правкой HTML.

Лицензии и источники — `skills/NOTICE.md`.

## Что дальше

1. Шаблон «фото + текст» — сейчас демо без фото.
2. Шаблон сторис 1080×1920.
3. Проверить `hallmark` на реальном посте: прогнать текст и макет по его проверкам.
