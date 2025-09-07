import asyncio

from nonebot import logger, on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.rule import to_me

from nonebot_plugin_prometheus.utils import MAGIC_PRIORITY

wait = on_command("metrics_test_wait", rule=to_me(), priority=MAGIC_PRIORITY, block=True)


@wait.handle()
async def wait(args: Message = CommandArg()):
    try:
        seconds = int(args.extract_plain_text())
    except (ValueError, TypeError):
        seconds = 3
    await asyncio.sleep(seconds)
    logger.debug(f"Wait for {seconds} seconds successfully")
