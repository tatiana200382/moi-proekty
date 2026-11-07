# Сертификаты Минцифры для MAX API

MAX Bot API (`platform-api2.max.ru`) использует сертификат, выданный УЦ Минцифры.
Без доверия к его корню Python и curl отвечают ошибкой проверки TLS, поэтому корневые
сертификаты лежат рядом и подключаются только в `max_client.py`.

Источник: официальные файлы Минцифры
- https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt
- https://gu-st.ru/content/lending/russian_trusted_sub_ca_pem.crt

Файл `max-ca.pem` — оба сертификата, разделённые переводом строки.

| Сертификат | SHA-256 |
|---|---|
| Russian Trusted Root CA | `D2:6D:2D:02:31:B7:C3:9F:92:CC:73:85:12:BA:54:10:35:19:E4:40:5D:68:B5:BD:70:3E:97:88:CA:8E:CF:31` |
| Russian Trusted Sub CA | `BB:BD:E2:10:3E:79:0B:99:9E:C6:2B:D0:3C:F6:25:A5:A2:E7:C3:16:E1:0A:FE:6A:49:0E:ED:EA:D8:B3:FD:9B` |

Это публичные сертификаты, не секреты. Токен бота здесь не хранится.
