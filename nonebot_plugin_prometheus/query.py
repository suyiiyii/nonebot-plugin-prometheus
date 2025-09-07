import time
from datetime import datetime, timedelta
from typing import Any, Dict

from nonebot import logger


def format_large_number(num: float) -> str:
    """格式化大数字，添加K、M、B等单位"""
    if num == 0:
        return "0"
    
    abs_num = abs(num)
    
    if abs_num >= 1_000_000_000:  # 十亿
        return f"{num/1_000_000_000:.1f}B"
    elif abs_num >= 1_000_000:  # 百万
        return f"{num/1_000_000:.1f}M"
    elif abs_num >= 1_000:  # 千
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"



from nonebot_plugin_prometheus.metrics import (
    bot_nums_gauge,
    bot_shutdown_counter,
    matcher_calling_counter,
    matcher_duration_histogram,
    metrics_request_counter,
    nonebot_start_at_gauge,
    received_messages_counter,
    sent_messages_counter,
)


def get_bot_status() -> Dict[str, Any]:
    """获取机器人状态信息"""
    try:
        # 获取所有机器人样本
        bot_samples = list(bot_nums_gauge.collect())[0].samples
        online_bots = [sample for sample in bot_samples if sample.value > 0]
        
        # 获取掉线次数
        shutdown_samples = list(bot_shutdown_counter.collect())[0].samples
        shutdown_counts = {sample.labels['bot_id']: sample.value for sample in shutdown_samples}
        
        status_info = {
            "total_bots": len(online_bots),
            "bots": []
        }
        
        for bot_sample in online_bots:
            bot_id = bot_sample.labels['bot_id']
            adapter_name = bot_sample.labels['adapter_name']
            shutdown_count = shutdown_counts.get(bot_id, 0)
            
            status_info["bots"].append({
                "bot_id": bot_id,
                "adapter": adapter_name,
                "status": "online",
                "shutdown_count": shutdown_count
            })
        
        return status_info
    except Exception as e:
        logger.error(f"获取机器人状态失败: {e}")
        return {"total_bots": 0, "bots": [], "error": str(e)}


def get_message_stats() -> Dict[str, Any]:
    """获取消息统计信息"""
    try:
        # 接收消息统计 - 只获取 _total 指标
        received_metric_data = list(received_messages_counter.collect())
        received_samples = []
        for metric_family in received_metric_data:
            for sample in metric_family.samples:
                # 只包含 _total 指标，排除 _created 指标
                if sample.name.endswith('_total'):
                    received_samples.append(sample)
        
        # 发送消息统计 - 只获取 _total 指标
        sent_metric_data = list(sent_messages_counter.collect())
        sent_samples = []
        for metric_family in sent_metric_data:
            for sample in metric_family.samples:
                # 只包含 _total 指标，排除 _created 指标
                if sample.name.endswith('_total'):
                    sent_samples.append(sample)
        
        received_total = sum(sample.value for sample in received_samples)
        sent_total = sum(sample.value for sample in sent_samples)
        
        # 按机器人和用户分组统计
        received_by_bot = {}
        sent_by_bot = {}
        
        for sample in received_samples:
            bot_id = sample.labels.get('bot_id', 'unknown')
            adapter_name = sample.labels.get('adapter_name', 'unknown')
            bot_key = f"{bot_id}({adapter_name})"
            
            if bot_key not in received_by_bot:
                received_by_bot[bot_key] = {
                    'bot_id': bot_id,
                    'adapter_name': adapter_name,
                    'count': 0
                }
            received_by_bot[bot_key]['count'] += sample.value
        
        for sample in sent_samples:
            bot_id = sample.labels.get('bot_id', 'unknown')
            adapter_name = sample.labels.get('adapter_name', 'unknown')
            bot_key = f"{bot_id}({adapter_name})"
            
            if bot_key not in sent_by_bot:
                sent_by_bot[bot_key] = {
                    'bot_id': bot_id,
                    'adapter_name': adapter_name,
                    'count': 0
                }
            sent_by_bot[bot_key]['count'] += sample.value
        
        logger.debug(f"Message stats - Received: {received_total}, Sent: {sent_total}, Samples: {len(received_samples)}/{len(sent_samples)}")
        
        return {
            "total_received": received_total,
            "total_sent": sent_total,
            "received_by_bot": received_by_bot,
            "sent_by_bot": sent_by_bot
        }
    except Exception as e:
        logger.error(f"获取消息统计失败: {e}")
        return {"total_received": 0, "total_sent": 0, "error": str(e)}


def get_matcher_stats(limit: int = 10) -> Dict[str, Any]:
    """获取匹配器统计信息"""
    try:
        # 获取匹配器调用次数 - 只获取 _total 指标
        calling_metric_data = list(matcher_calling_counter.collect())
        calling_samples = []
        for metric_family in calling_metric_data:
            for sample in metric_family.samples:
                # 只包含 _total 指标
                if sample.name.endswith('_total'):
                    calling_samples.append(sample)
        
        # 获取匹配器执行时间 - 正确处理直方图样本
        duration_metric_data = list(matcher_duration_histogram.collect())
        
        # 统计信息
        matcher_stats = {}
        
        for sample in calling_samples:
            plugin_id = sample.labels.get('plugin_id', 'unknown')
            matcher_name = sample.labels.get('matcher_name', 'unknown')
            has_exception = sample.labels.get('exception', 'False') == 'True'
            call_count = sample.value
            
            key = f"{plugin_id}:{matcher_name}"
            if key not in matcher_stats:
                matcher_stats[key] = {
                    "plugin_id": plugin_id,
                    "matcher_name": matcher_name,
                    "call_count": 0,
                    "error_count": 0,
                    "total_duration": 0,
                    "avg_duration": 0
                }
            
            matcher_stats[key]["call_count"] += call_count
            if has_exception:
                matcher_stats[key]["error_count"] += call_count
        
        # 计算执行时间 - 使用直方图的 _sum 样本
        for metric_family in duration_metric_data:
            for sample in metric_family.samples:
                if sample.name.endswith('_sum'):
                    plugin_id = sample.labels.get('plugin_id', 'unknown')
                    matcher_name = sample.labels.get('matcher_name', 'unknown')
                    key = f"{plugin_id}:{matcher_name}"
                    
                    if key in matcher_stats:
                        # 验证执行时间合理性
                        if sample.value <= 3600 * 24:  # 24小时
                            matcher_stats[key]["total_duration"] += sample.value
        
        # 计算平均执行时间
        for matcher in matcher_stats.values():
            if matcher["call_count"] > 0:
                matcher["avg_duration"] = matcher["total_duration"] / matcher["call_count"]
            else:
                matcher["avg_duration"] = 0
        
        # 按调用次数排序
        sorted_matchers = sorted(
            matcher_stats.values(), 
            key=lambda x: x["call_count"], 
            reverse=True
        )
        
        # 计算总调用次数
        total_calls = sum(m["call_count"] for m in sorted_matchers)
        total_errors = sum(m["error_count"] for m in sorted_matchers)
        
        logger.debug(f"Matcher stats - Total calls: {total_calls}, Total errors: {total_errors}, Matchers: {len(sorted_matchers)}")
        
        return {
            "total_matchers": len(sorted_matchers),
            "top_matchers": sorted_matchers[:limit],
            "total_calls": total_calls,
            "total_errors": total_errors
        }
    except Exception as e:
        logger.error(f"获取匹配器统计失败: {e}")
        return {"total_matchers": 0, "top_matchers": [], "error": str(e)}


def get_system_metrics() -> Dict[str, Any]:
    """获取系统指标"""
    try:
        # 获取启动时间
        start_time_samples = list(nonebot_start_at_gauge.collect())[0].samples
        if start_time_samples:
            start_time = start_time_samples[0].value
            uptime = time.time() - start_time
            uptime_str = str(timedelta(seconds=int(uptime)))
        else:
            uptime_str = "未知"
        
        # 获取指标请求次数
        metrics_requests = list(metrics_request_counter.collect())[0].samples[0].value
        
        return {
            "uptime": uptime_str,
            "metrics_requests": int(metrics_requests),
            "start_time": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S") if start_time_samples else "未知"
        }
    except Exception as e:
        logger.error(f"获取系统指标失败: {e}")
        return {"uptime": "未知", "metrics_requests": 0, "error": str(e)}