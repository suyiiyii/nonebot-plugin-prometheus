import prometheus_client as prometheus_client
from nonebot.plugin import PluginMetadata, require
from prometheus_client import (
    Counter as Counter,
)
from prometheus_client import (
    Gauge as Gauge,
)
from prometheus_client import (
    Histogram as Histogram,
)
from prometheus_client import (
    Summary as Summary,
)

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import Command

from nonebot_plugin_prometheus import api as api
from nonebot_plugin_prometheus.config import Config
from nonebot_plugin_prometheus.extension import MessageReceiveCounter

# Import to register the metrics query command matcher
import nonebot_plugin_prometheus.matcher.metrics_query  # noqa: F401

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

metrics_counter = (
    Command("metrics_counter", help_text="查询指标数据")
    .usage(__plugin_meta__.usage)
    .build(block=True, use_cmd_start=True, extensions=[MessageReceiveCounter()])
)
