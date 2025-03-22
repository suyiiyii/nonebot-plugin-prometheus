<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://github.com/suyiiyii/nonebot-plugin-prometheus"><img src="https://github.com/suyiiyii/nonebot-plugin-prometheus/blob/main/nonebot-plugin-prometheus.png" width="200" height="200" alt="nonebot"></a>
</p>

<div align="center">

# Nonebot Plugin Prometheus

_✨ NoneBot Prometheus 监控插件 ✨_

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/suyiiyii/nonebot-plugin-prometheus/main/LICENSE">
    <img src="https://img.shields.io/github/license/suyiiyii/nonebot-plugin-prometheus.svg" alt="license">
  </a>
  <a href="https://pypi.python.org/pypi/nonebot-plugin-prometheus">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-prometheus.svg" alt="pypi">
  </a>
</p>


## ✨功能

- 自动挂载 `/metrics` 路径，提供 Prometheus 监控数据
- 为其他插件提供统一的数据上报接口

## 📊支持统计的指标

- Bot 在线状态
- Bot 掉线次数
- Bot 发送和接受消息次数
- Matcher 执行次数

## ♿官方提供 Grafana 面板
[23060](https://grafana.com/grafana/dashboards/23060-nonebot-status-overview/)

![图片](https://github.com/user-attachments/assets/641d8637-cca8-462e-99ed-96eac6588086)

## 📦 安装

- 使用 nb-cli

```sh
nb plugin install nonebot-plugin-prometheus
```

- 使用 uv

```sh
uv add nonebot-plugin-prometheus
```

- 使用 poetry

```sh
poetry add nonebot-plugin-prometheus
```

- 使用 pip

```sh
pip install nonebot-plugin-prometheus
```

## 🔌接入方式

先在插件代码最前面声明依赖

```python
from nonebot import require

require("nonebot_plugin_prometheus")
```

然后可以从插件导入相关指标对象使用，详情请参考 [Prometheus Python Client 官方文档](https://prometheus.github.io/client_python/)

```python
from nonebot_plugin_prometheus import Gauge, Counter, Histogram, Summary

# Request counter
request_counter = Counter(
    "request_counter", "The number of requests"
)
request_counter.inc()
```

> **Tips**
>
> 为了统计 matcher 运行时间，本插件会自动在 `Matcher.state` 中插入 `_prometheus_start_time` 字段。

## 🔧配置

```ini
# 是否开启 Prometheus 插件
prometheus_enable = True
# Prometheus 挂载地址
prometheus_metrics_path = "/metrics"
```

> **Note**
>
> 使用插件需要支持 ASGI 的驱动器，例如 `fastapi`

## 📝TODO

- 提供快速上手 docker compose 文件
- 支持通过对话查询指标数据

## 相关仓库

- [NoneBot2](https://github.com/nonebot/nonebot2)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
