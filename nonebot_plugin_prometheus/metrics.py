from typing import Dict, Any

from nonebot import get_driver
from nonebot.adapters import Bot
from nonebot.matcher import Matcher
from nonebot.message import run_postprocessor
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


bot_nums_gauge = Gauge(
    "nonebot_bot_nums", "Total number of bots", ["bot_id", "adapter_name"]
)
bot_shutdown_counter = Counter(
    "nonebot_bot_shutdown", "Total number of bots shutdown", ["bot_id", "adapter_name"]
)


@driver.on_bot_connect
async def handle_bot_connect(bot: Bot):
    bot_nums_gauge.labels(bot.self_id, bot.adapter.get_name()).inc()


@driver.on_bot_disconnect
async def handle_bot_disconnect(bot: Bot):
    bot_nums_gauge.labels(bot.self_id, bot.adapter.get_name()).dec()
    bot_shutdown_counter.labels(bot.self_id, bot.adapter.get_name()).inc()


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


matcher_calling_counter = Counter(
    "nonebot_matcher_calling",
    "Total number of matcher calling",
    ["plugin_id", "matcher_name"],
)


@run_postprocessor
async def do_something(matcher: Matcher):
    if matcher.plugin_id == "nonebot_plugin_prometheus":
        # 跳过本模块的 matcher
        return
    # 因为一般不会给 matcher 命名，这里使用 module_name + line_number 作为 matcher_name
    matcher_name = f"{matcher.module_name}#L{matcher._source.lineno}"
    matcher_calling_counter.labels(matcher.plugin_id, matcher_name).inc()
