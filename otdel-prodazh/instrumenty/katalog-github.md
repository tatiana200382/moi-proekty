# Каталог GitHub: кандидаты для отдела продаж

Цифры — GitHub API, **11.11.2026**. Звёзды и issues меняются ежедневно; перед внедрением перепроверить. Запуском проверялся только API, не сами продукты.

| Репозиторий | Категория | Звёзды | Форки | Последний коммит | Issues | Лицензия | Вердикт |
|---|---|---|---|---|---|---|---|
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | автоматизация | 210 026 | 61 431 | 11.11.2026 | 1 250 | NOASSERTION | ✅ взят |
| [nocodb/nocodb](https://github.com/nocodb/nocodb) | база-таблица | 65 483 | 5 130 | 09.11.2026 | 582 | NOASSERTION | ⏸ позже |
| [twentyhq/twenty](https://github.com/twentyhq/twenty) | CRM | 60 749 | 10 050 | 11.11.2026 | 110 | NOASSERTION | ✅ взят |
| [odoo/odoo](https://github.com/odoo/odoo) | ERP/CRM | 55 700 | 34 271 | 11.11.2026 | 11 298 | NOASSERTION | ❌ слишком тяжёл |
| [metabase/metabase](https://github.com/metabase/metabase) | аналитика | 50 268 | 7 003 | 11.11.2026 | 4 706 | NOASSERTION | ⏸ позже |
| [calcom/cal.com](https://github.com/calcom/cal.com) | запись | 49 903 | 15 604 | 10.11.2026 | 1 624 | MIT | ❌ не наш случай |
| [chatwoot/chatwoot](https://github.com/chatwoot/chatwoot) | единый inbox | 39 581 | 9 609 | 10.11.2026 | 1 591 | NOASSERTION | ✅ взят |
| [activepieces/activepieces](https://github.com/activepieces/activepieces) | автоматизация | 25 469 | 4 450 | 10.11.2026 | 924 | NOASSERTION | ❌ запасной к n8n |
| [knadh/listmonk](https://github.com/knadh/listmonk) | рассылки | 24 245 | 2 779 | 10.11.2026 | 59 | AGPL-3.0 | ➖ зона Марты |
| [krayin/laravel-crm](https://github.com/krayin/laravel-crm) | CRM | 24 133 | 1 682 | 09.11.2026 | 129 | MIT | ❌ запасной |
| [formbricks/formbricks](https://github.com/formbricks/formbricks) | опросы | 13 232 | 2 607 | 10.11.2026 | 163 | NOASSERTION | ➖ зона Марты |
| [WhiskeySockets/Baileys](https://github.com/WhiskeySockets/Baileys) | WhatsApp | 11 596 | 3 502 | 08.11.2026 | 335 | MIT | ❌ риск бана |
| [mautic/mautic](https://github.com/mautic/mautic) | маркетинг | 10 964 | 3 534 | 11.11.2026 | 366 | NOASSERTION | ❌ не продажи |
| [EvolutionAPI/evolution-api](https://github.com/EvolutionAPI/evolution-api) | WhatsApp | 10 084 | 7 451 | 06.11.2026 | 262 | NOASSERTION | ❌ риск бана |
| [evidence-dev/evidence](https://github.com/evidence-dev/evidence) | отчёты | 7 102 | 443 | 10.11.2026 | 36 | MIT | ⏸ позже |
| [baserow/baserow](https://github.com/baserow/baserow) | база-таблица | 6 312 | 784 | 10.11.2026 | 1 192 | NOASSERTION | ⏸ альтернатива Sheets |
| [SuiteCRM/SuiteCRM](https://github.com/SuiteCRM/SuiteCRM) | CRM | 5 857 | 2 444 | 04.11.2026 | 1 372 | AGPL-3.0 | ❌ устарел |
| [erxes/erxes](https://github.com/erxes/erxes) | CRM/inbox | 4 112 | 1 334 | 10.11.2026 | 955 | NOASSERTION | ❌ сырее |
| [frappe/crm](https://github.com/frappe/crm) | CRM | 3 946 | 1 598 | 10.11.2026 | 304 | AGPL-3.0 | ❌ запасной |
| [asterisk/asterisk](https://github.com/asterisk/asterisk) | телефония | 3 679 | 1 356 | 05.11.2026 | 211 | NOASSERTION | ⏸ после решения по звонкам |
| [espocrm/espocrm](https://github.com/espocrm/espocrm) | CRM | 3 571 | 1 030 | 10.11.2026 | 67 | AGPL-3.0 | ❌ запасной |
| [mikopbx/Core](https://github.com/mikopbx/Core) | телефония | 601 | 91 | 10.11.2026 | 86 | GPL-3.0 | ⏸ позже |

## Что это значит

- **Живые и крупные:** n8n, Twenty, Chatwoot — их и берём.
- **Много issues — не приговор:** у n8n 1 250, но релизы каждую неделю. У SuiteCRM 1 372 при редких релизах — приговор.
- **NOASSERTION** — GitHub не распознал лицензию. Это не «без лицензии», а «надо читать». Для коммерческого использования проверить до внедрения.
- **Телефония** (Asterisk, MikoPBX) — не сейчас: сначала решение владельца, будет ли единый номер.
- **WhatsApp-обёртки** (Baileys, Evolution) — не берём: неофициальный протокол, номер могут заблокировать. Официальный WhatsApp Business API — отдельная платная история.

## Как перепроверить

```bash
curl -s https://api.github.com/repos/twentyhq/twenty | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d['stargazers_count'], d['pushed_at'], d['open_issues_count'])"
```

Дата проверки и цифры фиксируются в этом файле, а не в переписке.
