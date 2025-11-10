# -*- coding: utf-8 -*-
"""AccountRaze — визуальная симуляция «сноса аккаунта» с замазкой (zamazka)."""
from .. import loader, utils
import asyncio
import random
import time

@loader.tds
class AccountRazeMod(loader.Module):
    """AccountRaze — симуляция визуала 'снос аккаунта'. ВСЕ ДАННЫЕ ВЫМЫШЛЕНЫ."""
    strings = {
        "name": "AccountRaze",
        "usage": "Использование: .raze <юзер>\nНастройки: .razeset zam <текст_замазки>",
        "start": "Инициализация операции...",
        "progress_tpl": "[{bar}] {perc}% — {stage}",
        "final_title": "АККАУНТ УНИЧТОЖЕН",
        "final_tpl": (
            "=== {title} ===\n\n"
            "ЦЕЛЬ: {user}\n"
            "СТАТУС: {status}\n"
            "КОД ОПЕРАЦИИ: {op}\n"
            "ПРИМЕЧАНИЕ: {note}\n"
            "\n[{zam}]\n"
        ),
        "set_ok": "Параметр сохранён.",
        "fake_note": "Cn0c Akkaynta"
    }

    # переменные конфигурации в памяти (лёгкие)
    zamazka = "sn0c"   # текст замазки по умолчанию
    default_stages = [
        "Сбор метаданных",
        "Нарезка сессий",
        "Сброс токенов",
        "Обход кешей",
        "Финализация"
    ]

    async def client_ready(self, client, db):
        # db используется только если нужно; оставим пустым — всё в памяти
        self.client = client
        self.db = db

    async def razecmd(self, message):
        """.raze <юзер> — визуальный «снос аккаунта» (симуляция)."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["usage"])
            return
        user = args.strip()
        m = await utils.answer(message, self.strings["start"])

        # короткая анимация прогресса
        total = len(self.default_stages)
        for i, stage in enumerate(self.default_stages, start=1):
            perc = int(i / total * 100)
            bar = self._progress_bar(perc, length=18)
            await asyncio.sleep(random.uniform(0.6, 1.3))
            await m.edit(self.strings["progress_tpl"].format(bar=bar, perc=perc, stage=stage))

        # эффект "взлома" — несколько случайных строк
        hack_lines = self._make_hack_lines(user, self.zamazka)
        for line in hack_lines:
            await asyncio.sleep(random.uniform(0.12, 0.28))
            await m.edit(line)

        # финальный блок
        op_code = self._gen_op_code()
        final = self.strings["final_tpl"].format(
            title=self.strings["final_title"],
            user=self._obf_user(user, self.zamazka),
            status="COMPLETE",
            op=op_code,
            note=self.strings["fake_note"],
            zam=self.zamazka
        )
        await asyncio.sleep(0.5)
        await m.edit(final)

    async def razesetcmd(self, message):
        """.razeset zam <текст> — установить текст замазки (zamazka)."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "Требуется ключ и значение. Пример: .razeset zam sn0c")
            return
        parts = args.split(None, 1)
        if len(parts) < 2 or parts[0].lower() != "zam":
            await utils.answer(message, "Неверный синтаксис. Пример: .razeset zam sn0c")
            return
        self.zamazka = parts[1].strip()[:40]
        await utils.answer(message, self.strings["set_ok"])

    # --- вспомогательные функции ---

    def _progress_bar(self, perc, length=18):
        filled = int(perc / 100 * length)
        return "#" * filled + "-" * (length - filled)

    def _gen_op_code(self):
        t = int(time.time())
        r = random.randint(1000, 9999)
        return f"RAZE-{t % 100000}-{r}"

    def _obf_user(self, user, zam):
        # заменяет середину имени замазкой, сохраняет крайние символы
        if not user:
            return zam
        u = user.strip()
        if len(u) <= 4:
            return zam
        left = u[:2]
        right = u[-2:]
        return f"{left}{zam}{right}"

    def _make_hack_lines(self, user, zam):
        # формирует список строк для последовательного редактирования сообщения
        u_obf = self._obf_user(user, zam)
        lines = []
        templates = [
            f"Инициируем операцию по цели: {u_obf}",
            "Копирование профиля...",
            "Удаление бэкапов...",
            "Сброс сессионных ключей...",
            "Перезапись данных...",
            "Закрытие входов...",
            "Очистка логов...",
            "Завершение..."
        ]
        # случайная длина анимации
        for t in templates:
            noise = self._random_noise_line()
            lines.append(f"{t}\n{noise}")
        return lines

    def _random_noise_line(self, length=48):
        # симуляция «хакерского» шума
        chars = "01abxyz!@#%$^&*()-=[]{}<>;:,."
        return "".join(random.choice(chars) for _ in range(length))
