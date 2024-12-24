import prometheus_client as prometheus_client
from nonebot.plugin import PluginMetadata
from prometheus_client import (
    Counter as Counter,
    Gauge as Gauge,
    Histogram as Histogram,
    Summary as Summary,
)

from nonebot_plugin_prometheus import api as api
from nonebot_plugin_prometheus.config import Config

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
