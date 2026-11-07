"""Заявка с площадки: единый формат и карточка для MAX."""
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import os

LEADS_DIR = os.path.join(os.path.dirname(__file__), "..", "leads")


@dataclass
class Lead:
    source: str              # avito | vk | yandex
    client: str              # имя или ник
    question: str            # что спросил
    answer: str = ""         # черновик ответа
    status: str = "новая"    # новая | отвечено | ждёт_менеджера | закрыта
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))
    link: str = ""

    def card(self) -> str:
        icons = {"avito": "🟦", "vk": "🟪", "yandex": "🟨"}
        lines = [
            f"{icons.get(self.source, '⬜')} Заявка · {self.source.upper()}",
            f"Клиент: {self.client}",
            f"Вопрос: {self.question}",
        ]
        if self.answer:
            lines.append(f"Ответ: {self.answer}")
        lines.append(f"Статус: {self.status}")
        if self.link:
            lines.append(f"Ссылка: {self.link}")
        lines.append(f"Время: {self.created}")
        return "\n".join(lines)

    def save(self):
        os.makedirs(LEADS_DIR, exist_ok=True)
        name = f"{self.created.replace(':','').replace('-','')}-{self.source}.json"
        with open(os.path.join(LEADS_DIR, name), "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=1)
        return name


if __name__ == "__main__":
    demo = Lead(
        source="avito",
        client="Ирина",
        question="Букет белых роз 80 см есть сегодня к 18:00?",
        answer="Да, соберём к 18:00. Пришлём фото до отправки, при получении проверите — если что-то не так, заменим на месте.",
        link="https://www.avito.ru/profile/messenger",
    )
    print(demo.card())
    print("сохранено:", demo.save())
