import prometheus_client as prometheus_client
from nonebot.plugin import PluginMetadata
from prometheus_client import (
    Counter as Counter,
    Gauge as Gauge,
    Histogram as Histogram,
    Summary as Summary,
)

from nonebot_plugin_prometheus import api as api

__plugin_meta__ = PluginMetadata(
    name="Prometheus 集成插件",
    description="为 NoneBot 和其他插件提供 Prometheus 集成支持",
    type="library",
    usage="还不知道",
)

__all__ = [prometheus_client, Counter, Gauge, Histogram, Summary]
