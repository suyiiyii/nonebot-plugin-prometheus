import time
from typing import Any, Dict, Optional

from nonebot import get_driver, logger
from nonebot.adapters import Bot
from nonebot.matcher import Matcher, current_event
from nonebot.message import run_postprocessor
from prometheus_client import Counter, Gauge
from nonebot.message import run_preprocessor

driver = get_driver()
send_msg_apis = ["send", "post", "create", "im/v1/messages", "im/v1/images"]

metrics_request_counter = Counter(
    "nonebot_metrics_requests", "Total number of requests"
)

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
    "nonebot_received_messages",
    "Total number of received messages",
    ["bot_id", "adapter_name", "user_id"],
)

sent_messages_counter = Counter(
    "nonebot_sent_messages",
    "Total number of sent messages",
    ["bot_id", "adapter_name", "user_id"],
)


@Bot.on_calling_api
async def handle_api_call(bot: Bot, api: str, data: Dict[str, Any]):
    if not set(api.split("_")).intersection(send_msg_apis):
        return

    try:
        event = current_event.get()
        sent_messages_counter.labels(
            bot.self_id, bot.adapter.get_name(), event.get_user_id()
        ).inc()
    except LookupError:
        pass
        # 若未获取到 event，说明为用户主动发送消息，不属于统计范围


matcher_calling_counter = Counter(
    "nonebot_matcher_calling",
    "Total number of matcher calling",
    ["plugin_id", "matcher_name", "exception"],
)
from prometheus_client import Histogram

matcher_duration_histogram = Histogram(
    "nonebot_matcher_duration_seconds",
    "Histogram of matcher duration in seconds",
    ["plugin_id", "matcher_name", "exception"],
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.075,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        30.0,
        60.0,
    ),
)


@run_preprocessor
async def handle_preprocessor(matcher: Matcher):
    matcher.state.update({"_prometheus_start_time": time.time()})


@run_postprocessor
async def handle_postprocessor(matcher: Matcher, exception: Optional[Exception]):
    if matcher.plugin_id == "nonebot_plugin_prometheus":
        # 跳过本模块的 matcher
        return
    # 因为一般不会给 matcher 命名，这里使用 module_name + line_number 作为 matcher_name
    matcher_name = f"{matcher.module_name}#L{matcher._source.lineno}"
    has_exception = exception is not None
    duration = time.time() - matcher.state["_prometheus_start_time"]
    logger.debug(
        f"Matcher {matcher_name} duration: {duration}s, has exception {has_exception}"
    )

    matcher_calling_counter.labels(matcher.plugin_id, matcher_name, has_exception).inc()
    matcher_duration_histogram.labels(
        matcher.plugin_id, matcher_name, has_exception
    ).observe(duration)
