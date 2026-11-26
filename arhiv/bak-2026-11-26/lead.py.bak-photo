"""Заявка с площадки: единый формат, карточка для MAX, хранение.

Файл заявки: ../leads/<время>-<источник>-<номер>.json
Время — московское (Europe/Moscow, UTC+3).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone

MSK = timezone(timedelta(hours=3))
LEADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "leads"))
OUTBOX_DIR = os.path.join(LEADS_DIR, "outbox")

SOURCE_NAMES = {"avito": "Авито", "vk": "ВКонтакте", "yandex": "Яндекс.Карты"}
SOURCE_ICONS = {"avito": "🟦", "vk": "🟪", "yandex": "🟨"}


def now_msk() -> datetime:
    return datetime.now(MSK)


def fmt_dt(value: str) -> str:
    """ISO-время → «07.11.2026 20:30» по Москве. Ошибку не прячем: вернём как есть."""
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return value or "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=MSK)
    return dt.astimezone(MSK).strftime("%d.%m.%Y %H:%M")


def _safe(value: str, limit: int = 40) -> str:
    value = re.sub(r"[^0-9A-Za-zА-Яа-яЁё._-]+", "-", str(value)).strip("-")
    return value[:limit]


@dataclass
class Lead:
    source: str                     # avito | vk | yandex
    client: str                     # имя или ник
    question: str = ""              # что спросил / что заказал
    answer: str = ""                # черновик ответа
    status: str = "новая"           # новая | отправлена | отвечено | закрыта | старая
    created: str = field(default_factory=lambda: now_msk().isoformat(timespec="seconds"))
    link: str = ""
    external_id: str = ""           # номер заявки на площадке
    contact: str = ""               # телефон
    email: str = ""
    amount: str = ""                # сумма заказа
    items: list = field(default_factory=list)
    comment: str = ""
    notified: bool = False          # карточка ушла в MAX
    sent_at: str = ""               # когда карточка ушла в MAX
    max_mid: str = ""               # id сообщения в MAX
    baseline: bool = False          # историческая заявка до запуска бота

    @property
    def key(self) -> str:
        return f"{self.source}:{self.external_id}" if self.external_id else ""

    def card(self) -> str:
        icon = SOURCE_ICONS.get(self.source, "⬜")
        name = SOURCE_NAMES.get(self.source, self.source)
        lines = [f"{icon} Заявка · {name}"]
        if self.external_id:
            lines.append(f"№ {self.external_id} · {fmt_dt(self.created)}")
        else:
            lines.append(f"Время: {fmt_dt(self.created)}")
        lines.append(f"Клиент: {self.client}")
        if self.contact:
            lines.append(f"Телефон: {self.contact}")
        if self.email:
            lines.append(f"Почта: {self.email}")
        if self.items:
            lines.append("Заказ:")
            lines.extend(f"• {item}" for item in self.items)
        elif self.question:
            lines.append(f"Вопрос: {self.question}")
        if self.amount:
            lines.append(f"Сумма: {self.amount}")
        if self.comment:
            lines.append(f"Комментарий: {self.comment}")
        if self.answer:
            lines.append("")
            lines.append(f"Черновик ответа: {self.answer}")
        lines.append(f"Статус: {self.status}")
        if self.link:
            lines.append(f"Ссылка: {self.link}")
        return "\n".join(lines)[:4000]

    def filename(self) -> str:
        stamp = self.created.replace(":", "").replace("-", "")[:15]
        parts = [stamp, self.source]
        if self.external_id:
            parts.append(_safe(self.external_id))
        return "-".join(parts) + ".json"

    def save(self, directory: str = LEADS_DIR) -> str:
        os.makedirs(directory, mode=0o700, exist_ok=True)
        os.chmod(directory, 0o700)
        path = os.path.join(directory, self.filename())
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=1)
        os.chmod(path, 0o600)
        return path


def load_all(directory: str = LEADS_DIR) -> list:
    """Все заявки из папки, свежие первыми. Битые файлы пропускаем, но считаем."""
    leads = []
    if not os.path.isdir(directory):
        return leads
    for name in os.listdir(directory):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(directory, name), encoding="utf-8") as f:
                leads.append(Lead(**json.load(f)))
        except (OSError, ValueError, TypeError):
            continue
    leads.sort(key=lambda x: x.created, reverse=True)
    return leads


if __name__ == "__main__":
    demo = Lead(
        source="yandex",
        client="Елена Братухина",
        external_id="1494024",
        question="Заказ с Яндекс.Карт",
        items=['1 × Букет цветов "Аромат" — 3 200 ₽'],
        amount="3 200 ₽",
        contact="+7 911 164 95 99",
        email="bratukhinale@yandex.ru",
        answer="Здравствуйте, Елена! Спасибо за заказ № 1494024: "
               'Букет цветов "Аромат", 3 200 ₽. Подтвердите, пожалуйста, дату и время. '
               "Наш телефон: 8 905 218-88-57.",
        link="https://yandex.ru/business/crm/company/138890152139/requests/list",
    )
    print(demo.card())
    print("\nЭто пример карточки. В базу не сохраняю, чтобы демо не ушло в MAX как заявка.")
