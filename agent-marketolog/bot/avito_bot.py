#!/usr/bin/env python3
"""Прототип бота для Авито: ведёт диалог до готовой заявки.

Работает без Авито: логика диалога и карточка заявки.
Подключение к Авито — через Messenger API (нужна подписка), адаптер ниже.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
import json, os, re

LEADS_DIR = os.path.join(os.path.dirname(__file__), "..", "leads")
os.makedirs(LEADS_DIR, exist_ok=True)

GREETING = (
    "Здравствуйте! Это Silver Song Flowers 🌷\n"
    "Соберём букет под ваш повод и бюджет. Фото пришлём до отправки.\n\n"
    "Подскажите: какой повод и на какую дату?"
)

QUESTIONS = {
    "occasion": "Какой повод? (свидание, день рождения, извиниться, просто так)",
    "date": "На какую дату и время нужно?",
    "budget": "Какой бюджет? Например: до 2 500, 3 000–4 000, больше 5 000",
    "delivery": "Заберёте сами или нужна доставка? Если доставка — адрес и район.",
    "contact": "Как с вами связаться? Телефон или имя — чтобы менеджер подтвердил заказ.",
}

@dataclass
class Lead:
    source: str = "avito"
    chat_id: str = ""
    occasion: str = ""
    date: str = ""
    budget: str = ""
    delivery: str = ""
    contact: str = ""
    status: str = "собираем"
    created: str = field(default_factory=lambda: datetime.now().isoformat(timespec="minutes"))

    def ready(self) -> bool:
        return all([self.occasion, self.date, self.budget, self.delivery, self.contact])

    def card(self) -> str:
        return (
            "🟦 Заявка · АВИТО\n"
            f"Повод: {self.occasion}\n"
            f"Дата: {self.date}\n"
            f"Бюджет: {self.budget}\n"
            f"Получение: {self.delivery}\n"
            f"Контакт: {self.contact}\n"
            f"Статус: {self.status}\n"
            f"Создана: {self.created}"
        )

    def save(self) -> str:
        name = f"avito-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        path = os.path.join(LEADS_DIR, name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)
        return path

def parse_budget(text: str) -> str:
    nums = re.findall(r"\d[\d\s]{2,}", text)
    if not nums: return text.strip()
    val = int(re.sub(r"\D", "", nums[0]))
    return f"{val:,}".replace(",", " ") + " ₽"

FIELDS = ["occasion", "date", "budget", "delivery", "contact"]

class Bot:
    def __init__(self, lead: Lead | None = None):
        self.lead = lead or Lead()
        self.step = 0

    def start(self) -> str:
        return GREETING + "\n\n" + QUESTIONS[FIELDS[self.step]]

    def handle(self, text: str) -> tuple[str, bool]:
        """Возвращает (ответ, заявка_готова)."""
        text = (text or "").strip()
        if not text:
            return QUESTIONS[FIELDS[self.step]], False
        f = FIELDS[self.step]
        if f == "budget":
            setattr(self.lead, f, parse_budget(text))
        else:
            setattr(self.lead, f, text)
        self.step += 1
        if self.lead.ready():
            self.lead.status = "готова к продаже"
            path = self.lead.save()
            reply = (
                "Спасибо! Записал заявку.\n\n"
                f"{self.lead.card()}\n\n"
                "Менеджер подтвердит наличие и пришлёт фото букета в течение рабочего времени."
            )
            return reply, True
        return QUESTIONS[FIELDS[self.step]], False

if __name__ == "__main__":
    import sys
    bot = Bot()
    print("БОТ:", bot.start(), "\n")
    demo = ["День рождения", "завтра к 18:00", "до 4 000", "доставка, Ленинский 56, кв 12", "Анна, +7 900 000-00-00"]
    for msg in (demo if "--demo" in sys.argv else []):
        print("КЛИЕНТ:", msg)
        reply, ready = bot.handle(msg)
        print("БОТ:", reply, "\n")
        if ready: break
    if "--demo" in sys.argv:
        print("ФАЙЛ:", sorted(os.listdir(LEADS_DIR))[-1])
