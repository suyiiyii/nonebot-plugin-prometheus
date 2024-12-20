from prometheus_client import Counter

counter = Counter("nonebot_metrics_requests", "Total number of requests")
