from nonebot import get_driver
from nonebot.drivers import URL, Request, Response, ASGIMixin, HTTPServerSetup
from nonebot.log import logger
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from nonebot_plugin_prometheus.config import plugin_config
from nonebot_plugin_prometheus.metrics import metrics_request_counter


async def metrics(request: Request) -> Response:
    metrics_request_counter.inc()
    return Response(
        200, headers={"Content-Type": CONTENT_TYPE_LATEST}, content=generate_latest()
    )


def enable_prometheus():
    driver = get_driver()
    if not isinstance(driver, ASGIMixin):
        logger.warning("Prometheus 插件未找到支持 ASGI 的驱动器")
        return

    logger.debug(
        "找到支持 ASGI 的驱动器，Prometheus 插件使用以下配置加载: " + str(plugin_config)
    )
    driver.setup_http_server(
        HTTPServerSetup(
            path=URL(plugin_config.prometheus_metrics_path),
            method="GET",
            name="metrics",
            handle_func=metrics,
        )
    )


driver = get_driver()


@driver.on_startup
def load():
    if plugin_config.prometheus_enable:
        enable_prometheus()
