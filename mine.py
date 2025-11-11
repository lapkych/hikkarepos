# -*- coding: utf-8 -*-
"""CryptoMineProc — текстовая симуляция майнинга с визуальными процессами (proc#)."""
from .. import loader, utils
import asyncio
import random
import time

@loader.tds
class CryptoMineProcMod(loader.Module):
    """Визуальный симулятор майнинга с процессами."""
    strings = {
        "name": "CryptoMineProc",
        "usage": (
            ".mine <coin> [threads] [duration] — старт (threads 1..16, duration сек)\n"
            ".minestop — остановить симуляцию\n"
            ".minerstatus — статус\n"
            ".mineset pometka <текст> — изменить пометку"
        ),
        "started": "Запуск симуляции майнинга...",
        "already": "Симуляция уже запущена. Останови через .minestop",
        "nostart": "Симуляция не запущена.",
        "stopped": "Симуляция остановлена."
    }

    # обязательная пометка о фиктивности
    pometka = ""

    MAX_THREADS = 16
    DEFAULT_TICK = 1.0

    def __init__(self):
        super().__init__()
        self._running = False
        self._task = None
        self._ctrl = {"run": False}
        self._state = {
            "coin": None,
            "threads": 0,
            "duration": 0,
            "start": None,
            "hashes": 0,
            "accepted": 0,
            "shares": 0,
            "proc": {}  # proc_id -> {"hr":..., "last": "...", "status": "..."}
        }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def minecmd(self, message):
        """.mine <coin> [threads] [duration] — старт симуляции."""
        if self._running:
            await utils.answer(message, self.strings["already"])
            return
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["usage"])
            return
        parts = args.split()
        try:
            coin = parts[0][:16].upper()
            threads = int(parts[1]) if len(parts) > 1 else 4
            duration = int(parts[2]) if len(parts) > 2 else 60
        except Exception:
            await utils.answer(message, self.strings["usage"])
            return
        threads = max(1, min(self.MAX_THREADS, threads))
        duration = max(5, duration)

        # init state
        self._state.update({
            "coin": coin,
            "threads": threads,
            "duration": duration,
            "start": time.time(),
            "hashes": 0,
            "accepted": 0,
            "shares": 0,
            "proc": {}
        })
        # create processes
        for pid in range(1, threads + 1):
            # базовый hr на процесс
            base = random.randint(40, 900)
            self._state["proc"][pid] = {
                "hr": base,
                "last": "idle",
                "status": "running",
                "uptime": 0,
                "nonce": random.randint(1000000, 9999999)
            }

        self._ctrl["run"] = True
        self._running = True
        msg = await utils.answer(message, self.strings["started"])
        self._task = asyncio.create_task(self._run_sim(msg))
        return

    async def minestopcmd(self, message):
        """.minestop — остановить симуляцию."""
        if not self._running:
            await utils.answer(message, self.strings["nostart"])
            return
        self._ctrl["run"] = False
        # подождём немного
        if self._task:
            try:
                await asyncio.wait_for(self._task, timeout=5)
            except Exception:
                pass
        await utils.answer(message, self.strings["stopped"])

    async def minerstatuscmd(self, message):
        """.minerstatus — показать статус."""
        if not self._running:
            await utils.answer(message, self.strings["nostart"])
            return
        st = self._state
        elapsed = int(time.time() - st["start"])
        avg_hr = int((st["hashes"] / elapsed) if elapsed > 0 else 0)
        lines = [
            f"Монета: {st['coin']} | Потоки: {st['threads']} | Время: {elapsed}s/{st['duration']}s",
            f"Всего хэшей: {st['hashes']} | Принято: {st['accepted']} | Шары: {st['shares']} | Ср.HR: {avg_hr} H/s",
            "",
            "Процессы (последнее):"
        ]
        for pid, p in st["proc"].items():
            lines.append(f"[P#{pid:02}] HR:{p['hr']} H/s | {p['last']}")
        await utils.answer(message, "\n".join(lines))

    async def minesetcmd(self, message):
        """.mineset pometka <текст> — изменить пометку."""
        a = utils.get_args_raw(message)
        if not a:
            await utils.answer(message, "Использование: .mineset pometka <текст>")
            return
        k, _, val = a.partition(" ")
        if k.lower() != "pometka" or not val:
            await utils.answer(message, "Синтаксис: .mineset pometka <текст>")
            return
        self.pometka = val.strip()[:400]
        await utils.answer(message, "Пометка сохранена.")

    # внутренняя симуляция
    async def _run_sim(self, message_obj):
        st = self._state
        start = st["start"]
        duration = st["duration"]
        threads = st["threads"]
        tick = 1.0  # обновление в секундах
        last_update = 0

        try:
            while self._ctrl.get("run") and int(time.time() - start) < duration:
                now = time.time()
                # обновляем каждый tick
                for pid, p in st["proc"].items():
                    # случайные события для процесса
                    ev = random.random()
                    # небольшая флуктуация hr
                    jitter = random.uniform(0.85, 1.25)
                    p_hr = max(1, int(p["hr"] * jitter))
                    p["hr_cur"] = p_hr
                    p["uptime"] += tick
                    # событие принятого nonce
                    if ev < 0.015:
                        p["last"] = f"nonce {p['nonce']} accepted"
                        st["accepted"] += 1
                        st["shares"] += 1
                        st["hashes"] += int(p_hr * tick)
                        # случайно сменить nonce
                        p["nonce"] = random.randint(1000000, 9999999)
                    elif ev < 0.08:
                        p["last"] = f"nonce {random.randint(1000000,9999999)} rejected"
                        st["hashes"] += int(p_hr * tick * 0.6)
                    elif ev < 0.18:
                        p["last"] = "adjusting difficulty..."
                        st["hashes"] += int(p_hr * tick * 0.8)
                    else:
                        # обычный прогресс
                        sub = random.randint(0, 9)
                        p["last"] = f"hashing... nonce~{p['nonce']+sub}"
                        st["hashes"] += int(p_hr * tick)

                # формируем визуал
                elapsed = int(now - start)
                perc = int(elapsed / duration * 100)
                if perc < 0: perc = 0
                if perc > 100: perc = 100
                avg_hr = int((st["hashes"] / max(1, elapsed)))
                header = f"Майнинг: {st['coin']} | Потоки: {threads} | Время: {elapsed}s/{duration}s | Ср.HR: {avg_hr} H/s"
                bar = self._progress_bar(perc, 28)
                lines = [header, f"{bar} {perc}%  Всего хэшей: {st['hashes']}  Принято: {st['accepted']}  Шары: {st['shares']}", ""]
                # список процессов — показываем по 1 строке на процесс
                for pid in sorted(st["proc"].keys()):
                    p = st["proc"][pid]
                    hr = p.get("hr_cur", p["hr"])
                    last = p.get("last", "")
                    lines.append(f"[P#{pid:02}] HR:{hr} H/s | {last}")
                # обновляем сообщение раз в tick
                if now - last_update >= tick:
                    try:
                        await message_obj.edit("\n".join(lines))
                    except Exception:
                        pass
                    last_update = now
                await asyncio.sleep(tick * random.uniform(0.8, 1.2))

            # завершение
            elapsed = int(time.time() - start)
            avg_hr = int((st["hashes"] / max(1, elapsed)))
            reward = round((avg_hr * elapsed) / (100000.0 * random.uniform(1.8, 4.2)), 6)
            summary = [
                f"== Сессия завершена: {st['coin']} ==",
                f"Длительность: {elapsed}s  Потоки: {threads}",
                f"Всего хэшей: {st['hashes']}  Принято: {st['accepted']}  Шары: {st['shares']}",
                f"Условная добыча: {reward} {st['coin']}"
            ]
            try:
                await message_obj.edit("\n".join(summary))
            except Exception:
                pass
        finally:
            self._ctrl["run"] = False
            self._running = False
            self._task = None
            # сброс состояния
            self._state = {
                "coin": None,
                "threads": 0,
                "duration": 0,
                "start": None,
                "hashes": 0,
                "accepted": 0,
                "shares": 0,
                "proc": {}
            }

    def _progress_bar(self, perc, length=24):
        filled = int(perc / 100 * length)
        return "[" + "#" * filled + "-" * (length - filled) + "]"
