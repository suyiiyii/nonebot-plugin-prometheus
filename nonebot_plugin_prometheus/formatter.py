from typing import Any, Dict, List

from nonebot_plugin_prometheus.query import format_large_number


def format_bot_status(status_data: Dict[str, Any]) -> str:
    """格式化机器人状态信息"""
    if "error" in status_data:
        return f"❌ 获取机器人状态失败: {status_data['error']}"
    
    if status_data["total_bots"] == 0:
        return "🤖 当前没有在线的机器人"
    
    result = f"🤖 机器人状态 ({status_data['total_bots']} 台在线)\n"
    result += "=" * 40 + "\n"
    
    for bot in status_data["bots"]:
        status_emoji = "✅" if bot["status"] == "online" else "❌"
        result += f"{status_emoji} {bot['bot_id']} ({bot['adapter']})\n"
        result += f"   掉线次数: {bot['shutdown_count']}\n"
    
    return result


def format_message_stats(message_data: Dict[str, Any]) -> str:
    """格式化消息统计信息"""
    if "error" in message_data:
        return f"❌ 获取消息统计失败: {message_data['error']}"
    
    result = "📊 消息统计\n"
    result += "=" * 40 + "\n"
    result += f"📥 接收消息: {format_large_number(message_data['total_received'])} 条\n"
    result += f"📤 发送消息: {format_large_number(message_data['total_sent'])} 条\n"
    total_messages = message_data['total_received'] + message_data['total_sent']
    result += f"📈 总计消息: {format_large_number(total_messages)} 条\n"
    
    if message_data["received_by_bot"]:
        result += "\n📥 各机器人接收消息:\n"
        for bot_key, bot_info in message_data["received_by_bot"].items():
            result += f"   {bot_key}: {format_large_number(bot_info['count'])} 条\n"
    
    if message_data["sent_by_bot"]:
        result += "\n📤 各机器人发送消息:\n"
        for bot_key, bot_info in message_data["sent_by_bot"].items():
            result += f"   {bot_key}: {format_large_number(bot_info['count'])} 条\n"
    
    return result


def format_matcher_stats(matcher_data: Dict[str, Any]) -> str:
    """格式化匹配器统计信息"""
    if "error" in matcher_data:
        return f"❌ 获取匹配器统计失败: {matcher_data['error']}"
    
    if matcher_data["total_matchers"] == 0:
        return "🔍 暂无匹配器统计数据"
    
    result = f"🔍 匹配器统计 (共 {matcher_data['total_matchers']} 个匹配器)\n"
    result += "=" * 40 + "\n"
    result += f"📞 总调用次数: {format_large_number(matcher_data['total_calls'])}\n"
    result += f"❌ 错误次数: {format_large_number(matcher_data['total_errors'])}\n"
    success_rate = ((matcher_data['total_calls'] - matcher_data['total_errors']) / matcher_data['total_calls'] * 100) if matcher_data['total_calls'] > 0 else 0
    result += f"✅ 成功率: {success_rate:.1f}%\n"
    
    if matcher_data["top_matchers"]:
        result += f"\n🏆 热门匹配器 (前 {len(matcher_data['top_matchers'])} 个):\n"
        for i, matcher in enumerate(matcher_data["top_matchers"], 1):
            error_rate = (matcher["error_count"] / matcher["call_count"] * 100) if matcher["call_count"] > 0 else 0
            avg_time = matcher.get("avg_duration", 0)
            
            result += f"\n{i}. {matcher['matcher_name']}\n"
            result += f"   插件: {matcher['plugin_id']}\n"
            result += f"   调用次数: {format_large_number(matcher['call_count'])}\n"
            result += f"   错误率: {error_rate:.1f}%\n"
            if avg_time > 0:
                result += f"   平均耗时: {avg_time:.3f}s\n"
    
    return result


def format_system_metrics(system_data: Dict[str, Any]) -> str:
    """格式化系统指标"""
    if "error" in system_data:
        return f"❌ 获取系统指标失败: {system_data['error']}"
    
    result = "⚙️ 系统指标\n"
    result += "=" * 40 + "\n"
    result += f"⏱️ 运行时间: {system_data['uptime']}\n"
    result += f"🚀 启动时间: {system_data['start_time']}\n"
    result += f"📊 指标请求次数: {system_data['metrics_requests']}\n"
    
    return result


def format_help() -> str:
    """格式化帮助信息"""
    result = "📋 Prometheus 监控查询帮助\n"
    result += "=" * 50 + "\n\n"
    
    result += "🔧 可用命令:\n"
    result += "• metrics              - 显示系统概览\n"
    result += "• metrics status       - 机器人状态\n"
    result += "• metrics messages     - 消息统计\n"
    result += "• metrics matchers     - 匹配器统计\n"
    result += "• metrics system       - 系统指标\n"
    result += "• metrics uptime       - 运行时间\n"
    result += "• metrics query <name> - 查询指定指标\n"
    result += "• metrics list         - 列出所有指标\n"
    result += "• metrics search <key> - 搜索指标\n"
    result += "• metrics help         - 显示此帮助\n\n"
    
    result += "💡 使用示例:\n"
    result += "• /metrics\n"
    result += "• /metrics messages\n"
    result += "• /metrics matchers\n"
    result += "• /metrics query nonebot_received_messages\n"
    result += "• /metrics query nonebot_received_messages{method=\"GET\"}\n"
    result += "• /metrics list\n"
    result += "• /metrics search matcher\n\n"
    
    result += "📊 支持的指标:\n"
    result += "• 机器人在线状态和连接数\n"
    result += "• 消息收发统计\n"
    result += "• 匹配器执行次数和耗时\n"
    result += "• 系统运行时间和指标请求次数\n"
    result += "• 其他已注册的自定义指标\n"
    
    return result


def format_overview(bot_status: Dict[str, Any], message_stats: Dict[str, Any], 
                   matcher_stats: Dict[str, Any], system_metrics: Dict[str, Any]) -> str:
    """格式化系统概览"""
    result = "📊 Prometheus 监控概览\n"
    result += "=" * 50 + "\n\n"
    
    # 机器人状态
    if "error" not in bot_status:
        result += f"🤖 机器人: {bot_status['total_bots']} 台在线\n"
    
    # 消息统计
    if "error" not in message_stats:
        total_messages = message_stats['total_received'] + message_stats['total_sent']
        result += f"💬 消息: {format_large_number(total_messages)} 条 (收{format_large_number(message_stats['total_received'])}/发{format_large_number(message_stats['total_sent'])})\n"
    
    # 匹配器统计
    if "error" not in matcher_stats:
        success_rate = ((matcher_stats['total_calls'] - matcher_stats['total_errors']) / 
                       matcher_stats['total_calls'] * 100) if matcher_stats['total_calls'] > 0 else 0
        result += f"🔍 匹配器: {format_large_number(matcher_stats['total_calls'])} 次调用 (成功率 {success_rate:.1f}%)\n"
    
    # 系统指标
    if "error" not in system_metrics:
        result += f"⏱️ 运行时间: {system_metrics['uptime']}\n"
    
    result += "\n💡 使用 'metrics help' 查看详细帮助"
    
    return result


def format_custom_metric(metric_name: str, metric_data: Dict[str, Any]) -> str:
    """格式化自定义指标查询结果"""
    if "error" in metric_data:
        return f"❌ 查询指标失败: {metric_data['error']}"
    
    if not metric_data["metrics"]:
        return f"❌ 未找到指标: {metric_name}"
    
    result = f"📊 指标查询: {metric_name}\n"
    result += "=" * 50 + "\n"
    
    for metric in metric_data["metrics"]:
        result += f"📋 指标类型: {metric['type']}\n"
        result += f"📝 描述: {metric['help']}\n"
        result += f"🔢 样本数量: {len(metric['samples'])}\n\n"
        
        # 根据指标类型进行不同的格式化
        if metric["type"] in ["counter", "gauge"]:
            result += format_simple_metric_samples(metric["samples"])
        elif metric["type"] in ["histogram", "summary"]:
            result += format_complex_metric_samples(metric["samples"], metric["type"])
        else:
            result += format_simple_metric_samples(metric["samples"])
        
        result += "\n" + "-" * 50 + "\n"
    
    return result


def format_simple_metric_samples(samples: List[Dict[str, Any]]) -> str:
    """格式化简单指标（Counter, Gauge）的样本"""
    result = ""
    
    # 按标签分组显示
    samples_by_labels = {}
    for sample in samples:
        labels_key = sample["labels"]  # 已经是 tuple 了
        if labels_key not in samples_by_labels:
            samples_by_labels[labels_key] = []
        samples_by_labels[labels_key].append(sample)
    
    for labels, sample_group in samples_by_labels.items():
        if labels:
            labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in labels])
            result += f"   📌 {labels_str}\n"
        else:
            result += "   📌 (无标签)\n"
        
        for sample in sample_group:
            result += f"      {sample['name']}: {format_large_number(sample['value'])}\n"
    
    return result


def format_complex_metric_samples(samples: List[Dict[str, Any]], metric_type: str) -> str:
    """格式化复杂指标（Histogram, Summary）的样本"""
    result = ""
    
    # 分组样本类型
    sum_samples = []
    count_samples = []
    bucket_samples = []
    quantile_samples = []
    other_samples = []
    
    for sample in samples:
        name = sample["name"]
        if name.endswith("_sum"):
            sum_samples.append(sample)
        elif name.endswith("_count"):
            count_samples.append(sample)
        elif "_bucket" in name:
            bucket_samples.append(sample)
        elif metric_type == "summary" and any(q in name for q in ["0.5", "0.9", "0.95", "0.99"]):
            quantile_samples.append(sample)
        else:
            other_samples.append(sample)
    
    # 显示总和和计数
    if sum_samples:
        result += "   📈 总和:\n"
        for sample in sum_samples:
            labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in sample["labels"]])
            result += f"      {labels_str}: {sample['value']:.6f}\n"
    
    if count_samples:
        result += "   🔢 计数:\n"
        for sample in count_samples:
            labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in sample["labels"]])
            result += f"      {labels_str}: {format_large_number(sample['value'])}\n"
    
    # 显示分位数（Summary）
    if quantile_samples:
        result += "   📊 分位数:\n"
        for sample in quantile_samples:
            labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in sample["labels"]])
            result += f"      {labels_str}: {sample['value']:.6f}\n"
    
    # 显示桶信息（Histogram）
    if bucket_samples:
        result += "   🪣 分桶:\n"
        for sample in bucket_samples:
            labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in sample["labels"]])
            result += f"      {labels_str}: {format_large_number(sample['value'])}\n"
    
    # 显示其他样本
    if other_samples:
        result += "   📋 其他:\n"
        for sample in other_samples:
            labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in sample["labels"]])
            result += f"      {labels_str}: {sample['value']}\n"
    
    return result


def format_metrics_list(metrics: List[Dict[str, str]], title: str = "📋 可用指标列表") -> str:
    """格式化指标列表"""
    if not metrics:
        return "❌ 未找到任何指标"
    
    result = f"{title}\n"
    result += "=" * 50 + "\n"
    result += f"📊 总共找到 {len(metrics)} 个指标\n\n"
    
    for metric in metrics:
        result += f"🔸 {metric['name']} ({metric['type']})\n"
        result += f"   📝 {metric['help'][:80]}{'...' if len(metric['help']) > 80 else ''}\n"
        result += f"   🔢 {metric['sample_count']} 个样本\n\n"
    
    return result