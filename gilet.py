import logging
import typing
from datetime import datetime, timedelta, timezone

from telethon.tl import types
from telethon.tl.functions import channels, messages

from .. import loader, utils

logger = logging.getLogger("ChatModule")


@loader.tds
class ChatModuleMod(loader.Module):
    strings = {
        "name": "ChatModule",
    }

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self.xdlib = await self.import_lib(
            "https://raw.githubusercontent.com/coddrago/modules/refs/heads/main/libs/xdlib.py",
            suspend_on_error=True,
        )

    # ==========================================================
    # UNIVERSAL USER RESOLVER (reply / id / @username)
    # ==========================================================
    async def _get_user_any(self, message, opts):
        reply = await message.get_reply_message()
        user = opts.get("u") or opts.get("user") or (reply.sender_id if reply else None)

        if not user:
            return None

        try:
            if isinstance(user, str) and user.isdigit():
                user = int(user)
            return await self._client.get_entity(user)
        except Exception as e:
            logger.error(e)
            return None

    # ==========================================================
    # ID
    # ==========================================================
    @loader.command(ru_doc="[reply] - Узнать ID")
    async def id(self, message):
        ids = [self.strings["my_id"].format(id=self.tg_id)]
        if message.is_private:
            ids.append(self.strings["user_id"].format(id=message.to_id.user_id))
            return await utils.answer(message, "\n".join(ids))
        ids.append(self.strings["chat_id"].format(id=message.chat_id))
        reply = await message.get_reply_message()
        if reply and reply.sender_id:
            ids.append(self.strings["user_id"].format(id=reply.sender_id))
        return await utils.answer(message, "\n".join(ids))

    # ==========================================================
    # BAN
    # ==========================================================
    @loader.command(ru_doc="[-u id/@user] [-t] [-r] Забанить")
    @loader.tag("no_pm")
    async def ban(self, message):
        opts = self.xdlib.parse.opts(utils.get_args(message))
        reason = opts.get("r")

        user = await self._get_user_any(message, opts)
        if not user:
            return await utils.answer(message, self.strings["no_user"])

        seconds = self.xdlib.parse.time(opts.get("t")) if opts.get("t") else None
        until_date = (
            datetime.now(timezone.utc) + timedelta(seconds=seconds)
            if seconds else None
        )

        try:
            await self._client.edit_permissions(
                message.chat,
                user,
                until_date=until_date,
                view_messages=False,
            )
        except Exception as e:
            logger.error(e)
            return await utils.answer(message, self.strings["error"])

        text = self.strings["user_is_banned"].format(
            id=user.id,
            name=user.first_name,
            time_info=self.xdlib.format.time(seconds) if seconds else self.strings["forever"],
        )

        if reason:
            text += "\n" + self.strings["reason"].format(reason=reason)

        return await utils.answer(message, text)

    # ==========================================================
    # UNBAN
    # ==========================================================
    @loader.command(ru_doc="[-u id/@user] Разбанить")
    @loader.tag("no_pm")
    async def unban(self, message):
        opts = self.xdlib.parse.opts(utils.get_args(message))
        user = await self._get_user_any(message, opts)

        if not user:
            return await utils.answer(message, self.strings["no_user"])

        try:
            await self._client.edit_permissions(
                message.chat,
                user,
                view_messages=True,
            )
        except Exception as e:
            logger.error(e)
            return await utils.answer(message, self.strings["error"])

        return await utils.answer(
            message,
            self.strings["user_is_unbanned"].format(
                id=user.id,
                name=user.first_name,
            ),
        )

    # ==========================================================
    # MUTE
    # ==========================================================
    @loader.command(ru_doc="[-u id/@user] [-t] [-r] Замутить")
    @loader.tag("no_pm")
    async def mute(self, message):
        opts = self.xdlib.parse.opts(utils.get_args(message))
        reason = opts.get("r")

        user = await self._get_user_any(message, opts)
        if not user:
            return await utils.answer(message, self.strings["no_user"])

        seconds = self.xdlib.parse.time(opts.get("t")) if opts.get("t") else None
        until_date = (
            datetime.now(timezone.utc) + timedelta(seconds=seconds)
            if seconds else None
        )

        try:
            await self._client.edit_permissions(
                message.chat,
                user,
                until_date=until_date,
                send_messages=False,
            )
        except Exception as e:
            logger.error(e)
            return await utils.answer(message, self.strings["error"])

        text = self.strings["user_is_muted"].format(
            id=user.id,
            name=user.first_name,
            time_info=self.xdlib.format.time(seconds) if seconds else self.strings["forever"],
        )

        if reason:
            text += "\n" + self.strings["reason"].format(reason=reason)

        return await utils.answer(message, text)

    # ==========================================================
    # UNMUTE
    # ==========================================================
    @loader.command(ru_doc="[-u id/@user] Размутить")
    @loader.tag("no_pm")
    async def unmute(self, message):
        opts = self.xdlib.parse.opts(utils.get_args(message))
        user = await self._get_user_any(message, opts)

        if not user:
            return await utils.answer(message, self.strings["no_user"])

        try:
            await self._client.edit_permissions(
                message.chat,
                user,
                send_messages=True,
            )
        except Exception as e:
            logger.error(e)
            return await utils.answer(message, self.strings["error"])

        return await utils.answer(
            message,
            self.strings["user_is_unmuted"].format(
                id=user.id,
                name=user.first_name,
            ),
        )

    # ==========================================================
    # KICK
    # ==========================================================
    @loader.command(ru_doc="[-u id/@user] [-r] Кикнуть")
    @loader.tag("no_pm")
    async def kick(self, message):
        opts = self.xdlib.parse.opts(utils.get_args(message))
        reason = opts.get("r")

        user = await self._get_user_any(message, opts)
        if not user:
            return await utils.answer(message, self.strings["no_user"])

        try:
            await self._client.kick_participant(message.chat, user)
        except Exception as e:
            logger.error(e)
            return await utils.answer(message, self.strings["error"])

        text = self.strings["user_is_kicked"].format(
            id=user.id,
            name=user.first_name,
        )

        if reason:
            text += "\n" + self.strings["reason"].format(reason=reason)

        return await utils.answer(message, text)
