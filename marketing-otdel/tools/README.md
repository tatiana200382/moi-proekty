# Инструменты отдела: что установлено и как пользоваться

Всё работает на этом Mac без Docker, без Homebrew и без прав администратора. Проверено 11.11.2026.

## Что есть

| Инструмент | Команда | Что делает |
|---|---|---|
| Браузер | `node tools/browser.mjs …` | открывает кабинеты, снимает текст и скриншоты, проверяет входы |
| Отчёт | `python3 tools/report.py` | таблица каналов с CPL/CPA/ROMI из `data/metrics.csv` |
| Дашборд | `python3 tools/dashboard.py` | автономный HTML с заявками по каналам |
| Экономика | `python3 tools/economy.py` | CPL, CPA, ROMI, цена скидки, сколько заявок на бюджет |
| UTM | `python3 tools/utm.py --standard` | готовые размеченные ссылки по каналам |
| Фото | `python3 tools/photo.py --in … --out …` | кроп 4:5, 1080×1350, водяной знак |
| Видео | `./tools/ffmpeg.sh …` | ffmpeg 9.0, бинарник в `~/.local/bin/ffmpeg` |
| Дневной прогон | `./tools/dennoy-progon.sh` | доступы → данные → отчёт → дашборд одной командой |

## Быстрый старт

```bash
cd "marketing-otdel"

# 1. Проверить, что кабинеты открыты
node tools/browser.mjs login-status

# 2. Снять цифры и собрать отчёт
./tools/dennoy-progon.sh

# 3. Открыть дашборд
open results/dashboard.html
```

## Браузер

Нужен Chrome под управлением на порту 9224 и профиль `.chrome-profile` (входы уже сохранены в нём).

```bash
# запуск, если окно закрыто
open -na "Google Chrome" --args --remote-debugging-port=9224 \
  --user-data-dir="$PWD/../.chrome-profile"

node tools/browser.mjs tabs
node tools/browser.mjs text "https://yandex.ru/business/statistic/company/138890152139" --wait 8000 --out /tmp/yandex.txt
node tools/browser.mjs shot /tmp/karta.png --url "https://yandex.ru/maps/org/silver_song_flowers/138890152139/"
node tools/browser.mjs eval "document.title"
```

## Данные

`data/metrics.csv` — одна строка на канал и период:

```
date,channel,spend,impressions,clicks,leads,orders,revenue,source,note
```

Пустая ячейка = «данных нет», а не ноль. Отчёт честно пишет «нет данных», пока заявки не заведены.

## Фото

Нужен Pillow — он есть только во встроенном Python DeepSeek Harness, скрипт сам переключается на него.

```bash
python3 tools/photo.py --in fotki --out gotovye --size 1080x1350 --watermark "Silver Song Flowers"
python3 tools/photo.py --in fotki --out prevyu --thumb      # 400×500
```

Проверено: 3 фото, 1080×1350, водяной знак в правом нижнем углу, ~210–260 КБ.

## Видео

```bash
./tools/ffmpeg.sh -i in.mov -vf "scale=1080:-2" -c:v libx264 -crf 23 out.mp4
./tools/ffmpeg.sh -i in.mp4 -vf "fps=15,scale=480:-1" -loop 0 out.gif
```

## Что не встало и почему

| Пробел | Причина | Замена |
|---|---|---|
| numpy, rembg, matplotlib в отдельном окружении | встроенный Python подписан, сторонние C-расширения не загружаются (Team ID) | Pillow из встроенного Python; вырезка фона — системный Vision (метод Вовы) |
| Metabase, Twenty, n8n | нужен Java/Docker/сервер | отчёт и дашборд на Python, данные в CSV |
| Postiz, Chatwoot, Flowwow API | нужны сервер и токены | публикация вручную после «да», Flowwow — через приложение Seller |
| n8n | тяжёлый и требует постоянного процесса | `dennoy-progon.sh` по расписанию (launchd/cron) |

## Правила

1. Сырые дампы кабинетов — только в `~/.local/state/marketing/`, не в git: там переписка и контакты.
2. Пароли и токены — вне репозитория (`~/.config/...`).
3. Любая запись в кабинеты — после «да» владельца; инструменты только читают.
4. Инструмент без проверки на реальных данных не считается установленным.
