<!-- markdownlint-disable MD033 MD036 MD041 -->

<p align="center">
  <a href="https://v2.nonebot.dev/"><img src="https://v2.nonebot.dev/logo.png" width="200" height="200" alt="nonebot"></a>
</p>


<div align="center">

# Nonebot Plugin Prometheus

_✨ NoneBot Prometheus 集成插件 ✨_

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

* 自动挂载 `/metrics` 路径，提供 Prometheus 监控数据
* 为其他插件提供统一的数据上报接口

## 安装

- 使用 pip

```sh
pip install nonebot-plugin-prometheus
```

[//]: # ()
[//]: # (## 接入方式)

[//]: # ()
[//]: # (先在插件代码最前面声明依赖)