from nonebot.drivers.websockets import logger
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="Prometheus 集成插件",
    description="为 NoneBot 和其他插件提供 Prometheus 集成支持",
    type="library",
    usage="还不知道"
)

from nonebot import get_driver
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
from prometheus_client import Counter, generate_latest

from nonebot_plugin_prometheus.config import plugin_config

counter = Counter("nonebot_metrics_requests", "Total number of requests")


async def metrics(request: Request) -> Response:
    counter.inc()
    return Response(200, content=generate_latest())


if plugin_config.prometheus_enable:
    driver = get_driver()
    if not isinstance(driver, ASGIMixin):
        logger.warning("Prometheus 插件未找到支持 ASGI 的驱动器")
    else:
        logger.debug("找到支持 ASGI 的驱动器，Prometheus 插件开始加载")
        driver.setup_http_server(
            HTTPServerSetup(
                path=URL(plugin_config.prometheus_metrics_path),
                method="GET",
                name="metrics",
                handle_func=metrics,
            )
        )
