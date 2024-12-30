from typing import Dict, Any

from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.plugin.on import on_message
from prometheus_client import Counter, Gauge

metrics_request_counter = Counter(
    "nonebot_metrics_requests", "Total number of requests"
)

driver = get_driver()

nonebot_start_at_gauge = Gauge("nonebot_start_at", "Start time of the bot")


@driver.on_startup
def handle_startup():
    nonebot_start_at_gauge.set_to_current_time()


bot_nums_gauge = Gauge("nonebot_bot_nums", "Total number of bots", ["bot_id"])
bot_shutdown_counter = Counter(
    "nonebot_bot_shutdown", "Total number of bots shutdown", ["bot_id"]
)


@driver.on_bot_connect
async def handle_bot_connect(bot: Bot):
    bot_nums_gauge.labels(bot.self_id).inc()


@driver.on_bot_disconnect
async def handle_bot_disconnect(bot: Bot):
    bot_nums_gauge.labels(bot.self_id).dec()
    bot_shutdown_counter.labels(bot.self_id).inc()


received_messages_counter = Counter(
    "nonebot_received_messages", "Total number of received messages", ["bot_id"]
)


@on_message(block=False).handle()
async def handle_message(bot: Bot):
    received_messages_counter.labels(bot.self_id).inc()


sent_messages_counter = Counter(
    "nonebot_sent_messages", "Total number of sent messages", ["bot_id", "user_id"]
)


@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: Dict[str, Any]):
    if api == "send_msg":
        sent_messages_counter.labels(bot.self_id, data["user_id"]).inc()
