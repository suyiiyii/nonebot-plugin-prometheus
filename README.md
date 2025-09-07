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
- **新增**：支持通过对话查询指标数据
- **新增**：提供通用指标查询接口，支持任意已注册指标的查询

## 📊支持统计的指标

- Bot 在线状态
- Bot 掉线次数
- Bot 发送和接受消息次数
- Matcher 执行次数
- Matcher 执行耗时分布

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
PROMETHEUS_ENABLE=true
# Prometheus 挂载地址
PROMETHEUS_METRICS_PATH=/metrics
```

> **Note**
>
> 使用插件需要支持 ASGI 的驱动器，例如 `fastapi`

## 💬对话查询功能

本插件现在支持通过对话命令查询指标数据，方便在聊天中快速查看监控信息。

### 基础命令

```bash
# 查看系统概览
/metrics

# 查看机器人状态
/metrics status

# 查看消息统计
/metrics messages

# 查看匹配器统计
/metrics matchers

# 查看系统指标
/metrics system

# 查看运行时间
/metrics uptime

# 查看帮助
/metrics help
```

### 通用指标查询

**新增**：支持查询任意已注册的 Prometheus 指标：

```bash
# 查询特定指标
/metrics query nonebot_received_messages

# 带标签过滤的查询
/metrics query nonebot_received_messages{bot_id="123456"}

# 列出所有可用指标
/metrics list

# 搜索包含关键字的指标
/metrics search matcher
```

### 查询示例

```bash
# 查看接收消息总数
/metrics query nonebot_received_messages

# 查看特定机器人的消息统计
/metrics query nonebot_received_messages{bot_id="72075954", adapter_name="Telegram"}

# 查看匹配器执行情况
/metrics query nonebot_matcher_calls_total

# 搜索所有与匹配器相关的指标
/metrics search matcher
```

### 输出格式

查询结果会以格式化的方式显示，包含：
- 指标类型和描述
- 标签信息
- 指标值
- 适当的单位格式化（如 K、M、B 等）

## 🔧开发者接口

除了对话查询，本插件还提供了编程接口供其他插件使用：

```python
from nonebot_plugin_prometheus.registry import (
    get_metrics,           # 获取所有指标
    get_metrics_by_name,   # 按名称获取指标
    get_metric_values,     # 获取指标值
    list_all_metrics,      # 列出所有指标
    search_metrics,        # 搜索指标
    parse_metric_filter,   # 解析查询字符串
)

# 示例：获取特定指标的值
values = get_metric_values("nonebot_received_messages", {"bot_id": "123456"})
for labels, value in values:
    print(f"Labels: {labels}, Value: {value}")
```

## 📝TODO

- 提供快速上手 docker compose 文件

## 相关仓库

- [NoneBot2](https://github.com/nonebot/nonebot2)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
