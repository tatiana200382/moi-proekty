# Flowwow: витрина Silver Song Flowers

Отдельный проект. Ведёт Марк — продавец витрины.

| Что | Где |
|---|---|
| Роль и правила | `AGENTS.md`, `employee.md` |
| Знания о магазине и экономике | `knowledge.md` |
| Схема старта и ежедневный ритм | `start-raboty.md` |
| Навыки: копирайтинг, фото, карточка, отзывы, цены | `skills/` |
| Правила площадки и рынок | `research/` |
| Отчёты, карточки, тексты | `results/` |
| Инструменты: доступ, API, калькулятор | `tools/` |
| Состояние работы | `state.md` |

## Быстрый старт

```bash
cd flowwow-prodavec
node tools/flowwow-auth.mjs open      # открыть кабинет продавца
node tools/flowwow-api.mjs ping       # проверить API
node tools/flowwow-api.mjs products 50582 --stats
node tools/flowwow-calc.mjs 3850 --cost=2100
```

## Цель

10 заказов в неделю. Сейчас 2 заказа в месяц.
