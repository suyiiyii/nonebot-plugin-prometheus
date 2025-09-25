from nonebot import get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    prometheus_enable: bool = True
    prometheus_metrics_path: str = "/metrics"
    prometheus_chat_needs_admin: bool = True


plugin_config = get_plugin_config(Config)
