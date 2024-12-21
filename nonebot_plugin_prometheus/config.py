from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    prometheus_enable: bool = True
    prometheus_metrics_path: str = "/metrics"


plugin_config = get_plugin_config(Config)
