import logging
from datetime import datetime

import telegram
from bulkmail.models import Bulkmail, Message, SendList
from telegram import Bot

logger = logging.getLogger("bulkmail")


class BulkmailSender:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.fn_map = {
            Message.ContentTypes.PHOTO.value: self._send_photo,
            Message.ContentTypes.ANIMATION.value: self._send_animation,
            Message.ContentTypes.VIDEO.value: self._send_video,
            Message.ContentTypes.EMPTY.value: self._send_message,
        }

    def _send(self, message: Message, entity: SendList) -> SendList.Statuses:
        try:
            if Message.ContentTypes.PHOTO == message.content_type:
                status = self._send_photo(message, entity)
            elif Message.ContentTypes.ANIMATION == message.content_type:
                status = self._send_animation(message, entity)
            elif Message.ContentTypes.VIDEO == message.content_type:
                status = self._send_video(message, entity)
            elif Message.ContentTypes.EMPTY == message.content_type:
                status = self._send_message(message, entity)
            else:
                raise AttributeError
        except telegram.error.Unauthorized:
            entity.user.unauthorizing()
            entity.status = SendList.Statuses.ERROR
            entity.save()
            return SendList.Statuses.ERROR.value

        except (telegram.error.TelegramError, AttributeError) as e:
            logger.error(e)
            entity.status = SendList.Statuses.ERROR
            entity.save()
            return SendList.Statuses.ERROR.value

        entity.status = SendList.Statuses.SUCCESS
        entity.save()
        return status

    def run(self, bulkmail: Bulkmail):
        start = datetime.now()
        stats = {SendList.Statuses.ERROR.value: 0, SendList.Statuses.SUCCESS.value: 0}
        for entity in bulkmail.get_list():
            result = self._send(bulkmail.message, entity)
            stats[result] += 1

        timer = datetime.now() - start
        bulkmail.duration = (datetime.min + timer).time()
        bulkmail.status = Bulkmail.Statuses.SUCCESS
        bulkmail.save()

    def _send_photo(self, message: Message, entity: SendList) -> SendList.Statuses:
        self.bot.send_photo(
            chat_id=entity.user.user_id,
            photo=message.content,
            caption=message.text,
            reply_markup=message.get_keyboard,
        )
        return SendList.Statuses.SUCCESS.value

    def _send_video(self, message: Message, entity: SendList) -> SendList.Statuses:
        self.bot.send_video(
            chat_id=entity.user.user_id,
            video=message.content,
            caption=message.text,
            reply_markup=message.get_keyboard,
        )
        return SendList.Statuses.SUCCESS.value

    def _send_message(self, message: Message, entity: SendList) -> SendList.Statuses:
        self.bot.send_message(
            chat_id=entity.user.user_id,
            text=message.text,
            reply_markup=message.get_keyboard,
        )

        return SendList.Statuses.SUCCESS.value

    def _send_animation(self, message: Message, entity: SendList) -> SendList.Statuses:
        self.bot.send_animation(
            chat_id=entity.user.user_id,
            caption=message.text,
            animation=message.content,
            reply_markup=message.get_keyboard,
        )

        return SendList.Statuses.SUCCESS.value
