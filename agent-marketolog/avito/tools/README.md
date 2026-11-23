# Инструменты заполнения объявлений Авито

Работают через Chrome с отладкой на порту 9224 (профиль `~/.config/dsh-chrome/profile`).

| Файл | Что делает |
|---|---|
| `pick-fields.mjs <draftId>` | ставит «Вид объявления» = «Продаю своё» и «Основной цвет» = «Разноцветный» |
| `full-fields.mjs <draftId>` | то же + отмечает **все** цветы в «Составе букета» по одному, как человек |
| `verify-all.mjs` | проверяет все пять черновиков и печатает значения после перезагрузки |

Запуск:

```
NODE="/Applications/DeepSeek Harness.app/Contents/Resources/runtime/primary-runtime/dependencies/node/bin/node"
"$NODE" agent-marketolog/avito/tools/full-fields.mjs 1851307076
```

Важно: Авито принимает значения только от **настоящих кликов** — программная установка `select.value` не сохраняется. Поэтому инструменты кликают по координатам.
