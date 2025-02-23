import prometheus_client as prometheus_client
from nonebot.plugin import PluginMetadata, require
from prometheus_client import (
    Counter as Counter,
    Gauge as Gauge,
    Histogram as Histogram,
    Summary as Summary,
)

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Command, add_global_extension

from nonebot_plugin_prometheus import api as api
from nonebot_plugin_prometheus.config import Config
from nonebot_plugin_prometheus.extension import MessageCounterExtension

__plugin_meta__ = PluginMetadata(
    name="Prometheus 监控",
    description="为 NoneBot 和其他插件提供 Prometheus 监控支持",
    type="library",
    usage="请参考文档",
    homepage="https://github.com/suyiiyii/nonebot-plugin-prometheus",
    config=Config,
    supported_adapters=None,
)

__all__ = [prometheus_client, Counter, Gauge, Histogram, Summary]

add_global_extension(MessageCounterExtension)

metrics = (
    Command("metrics", help_text="查询指标数据")
    .usage(__plugin_meta__.usage)
    .build(
        block=True,
        use_cmd_start=True,
    )
)
