# -*- coding: utf-8 -*-
"""RoleplayDox — игровая симуляция докса и SWAT. Пометка вынесена в переменную pometka."""
from .. import loader, utils
import random
import asyncio

@loader.tds
class doxingmachine(loader.Module):
    """RoleplayDox — безопасная визуализация. Не собирает реальные данные."""
    # Пометка вынесена в одну переменную. Изменяйте при необходимости.
    pometka = (
        ""
    )

    strings = {
        "name": "Doxxing Machine",
        "usage_dox": "Использование: .dox <юзер>",
        "usage_swat": "Использование: .swat <юзер>",
        "starting": "Запуск симуляции...",
        "stage_tpl": "Этап {i}/{n}: {stage}",
        "final_dox": (
            "Человек задокшен\n\n"
            "Юзер: {user}\n"
            "Имя: {name}\n"
            "Email: {email}\n"
            "Телефон: {phone}\n"
            "IP: {ip}\n"
            "Город: {city}\n\n"
            "{pometka}"
        ),
        "final_swat": (
            "SWAT-отчёт\n\n"
            "Юзер: {user}\n"
            "Операция: {op}\n"
            "Приоритет: {prio}\n"
            "Адрес: {addr}\n\n"
            "{pometka}"
        ),
    }

    async def client_ready(self, client, db):
        self.client = client

    async def doxcmd(self, message):
        """.dox <юзер> — симулирует докс-процесс (игра)."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["usage_dox"])
            return
        user = args.strip()
        msg = await utils.answer(message, self.strings["starting"])
        stages = [
            "Сбор открытых записей",
            "Кросс-проверка соцсетей",
            "Анализ активности",
            "Сбор метаданных",
            "Формирование финального отчёта"
        ]
        for i, stage in enumerate(stages, start=1):
            await asyncio.sleep(random.uniform(0.7, 1.4))
            await msg.edit(self.strings["stage_tpl"].format(i=i, n=len(stages), stage=stage))
        fake = self._fake_profile(user)
        await asyncio.sleep(0.6)
        # передаём pometka в форматирование
        await msg.edit(self.strings["final_dox"].format(user=user, pometka=self.pometka, **fake))

    async def swatcmd(self, message):
        """.swat <юзер> — симулирует SWAT-репорт (игра)."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["usage_swat"])
            return
        user = args.strip()
        msg = await utils.answer(message, "Подготовка симуляции SWAT...")
        stages = ["Оценка угроз", "Определение координат (фиктивно)", "Координация операций"]
        for i, stage in enumerate(stages, start=1):
            await asyncio.sleep(random.uniform(0.5, 1.1))
            await msg.edit(self.strings["stage_tpl"].format(i=i, n=len(stages), stage=stage))
        fake = self._fake_swat(user)
        await asyncio.sleep(0.6)
        await msg.edit(self.strings["final_swat"].format(user=user, pometka=self.pometka, **fake))

    def _fake_profile(self, user):
        first = random.choice(["Алексей","Иван","Дмитрий","Сергей","Никита","Мария","Елена"])
        last = random.choice(["Петров","Иванов","Сидоров","Кузнецов","Смирнов","Ковалёва"])
        name = f"{first} {last}"
        email = f"{user.lower().replace(' ', '')}{random.randint(1,999)}@example.com"
        phone = f"+7{random.randint(900,999)}{random.randint(1000000,9999999)}"
        ip = f"{random.randint(10,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        city = random.choice(["Москва","Санкт-Петербург","Новосибирск","Екатеринбург","Казань","Самара"])
        return {"name": name, "email": email, "phone": phone, "ip": ip, "city": city}

    def _fake_swat(self, user):
        op = random.choice(["Рейд по онлайн-данным","Проверка безопасности","Учебная тревога"])
        prio = random.choice(["Низкий","Средний","Высокий"])
        addr = f"ул. {random.choice(['Ленина','Пушкина','Советская'])}, {random.randint(1,200)}"
        return {"op": op, "prio": prio, "addr": addr}
