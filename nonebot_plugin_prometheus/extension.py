from nonebot import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import Alconna, Extension, UniMessage

from nonebot_plugin_prometheus.metrics import (
    received_messages_counter,
)


class MessageReceiveCounter(Extension):
    @property
    def priority(self) -> int:
        return 15

    @property
    def id(self) -> str:
        return "MessageReceiveCounter"

    async def receive_wrapper(
        self, bot: Bot, event: Event, command: Alconna, receive: UniMessage
    ) -> UniMessage:
        logger.trace(f"Bot {bot.adapter.get_name()} {bot.self_id} received msg")
        received_messages_counter.labels(
            bot.self_id, bot.adapter.get_name(), event.get_user_id()
        ).inc()
        return receive
