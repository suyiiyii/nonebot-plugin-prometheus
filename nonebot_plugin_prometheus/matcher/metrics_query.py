from nonebot import on_command, logger
from nonebot.adapters import Message, Bot, Event
from nonebot.params import CommandArg
from nonebot.matcher import Matcher

from nonebot_plugin_prometheus.formatter import (
    format_bot_status,
    format_custom_metric,
    format_help,
    format_matcher_stats,
    format_message_stats,
    format_metrics_list,
    format_overview,
    format_system_metrics,
)
from nonebot_plugin_prometheus.query import (
    get_bot_status,
    get_matcher_stats,
    get_message_stats,
    get_system_metrics,
    format_large_number,
)
from nonebot_plugin_prometheus.registry import (
    get_metrics_by_name,
    list_all_metrics,
    search_metrics,
    parse_metric_filter,
    get_metric_values,
)
from nonebot_plugin_prometheus.metrics import received_messages_counter
from nonebot_plugin_prometheus.utils import MAGIC_PRIORITY

# 创建 metrics 命令处理器 (传统 on_command，用于对话查询)
metrics_query = on_command(
    "metrics", 
    aliases={"查询指标", "监控数据"}, 
    priority=MAGIC_PRIORITY + 1,  # 使用不同优先级避免冲突
    block=True
)


@metrics_query.handle()
async def handle_metrics_query(bot: Bot, event: Event, matcher: Matcher, args: Message = CommandArg()):
    """处理 metrics 查询命令"""
    # 处理消息计数
    try:
        logger.trace(f"Bot {bot.adapter.get_name()} {bot.self_id} received metrics command")
        received_messages_counter.labels(
            bot.self_id, bot.adapter.get_name(), event.get_user_id()
        ).inc()
    except Exception as e:
        logger.debug(f"Count received message failed: {e}")
    
    # 获取命令参数
    arg_text = args.extract_plain_text().strip().lower()
    
    # 根据参数处理不同的查询类型
    if not arg_text or arg_text in ["", "overview", "概览"]:
        # 显示系统概览
        await handle_overview(matcher)
    elif arg_text in ["status", "状态", "bot", "机器人"]:
        # 显示机器人状态
        await handle_status(matcher)
    elif arg_text in ["messages", "消息", "msg"]:
        # 显示消息统计
        await handle_messages(matcher)
    elif arg_text in ["matchers", "匹配器", "matcher"]:
        # 显示匹配器统计
        await handle_matchers(matcher)
    elif arg_text in ["system", "系统", "sys"]:
        # 显示系统指标
        await handle_system(matcher)
    elif arg_text in ["uptime", "运行时间", "启动时间"]:
        # 显示运行时间
        await handle_uptime(matcher)
    elif arg_text in ["help", "帮助", "h", "?"]:
        # 显示帮助
        await handle_help(matcher)
    elif arg_text.startswith("query "):
        # 查询特定指标
        metric_query = arg_text[6:].strip()
        await handle_query(matcher, metric_query)
    elif arg_text in ["list", "列表", "ls"]:
        # 列出所有指标
        await handle_list(matcher)
    elif arg_text.startswith("search "):
        # 搜索指标
        keyword = arg_text[7:].strip()
        await handle_search(matcher, keyword)
    else:
        # 未知参数，显示帮助
        await matcher.send(f"❌ 未知参数: {arg_text}")
        await handle_help(matcher)


async def handle_overview(matcher: Matcher):
    """处理系统概览"""
    try:
        # 并行获取所有数据
        bot_status = get_bot_status()
        message_stats = get_message_stats()
        matcher_stats = get_matcher_stats(limit=5)
        system_metrics = get_system_metrics()
        
        # 格式化概览
        overview_text = format_overview(bot_status, message_stats, matcher_stats, system_metrics)
        await matcher.send(overview_text)
    except Exception as e:
        await matcher.send(f"❌ 获取系统概览失败: {str(e)}")


async def handle_status(matcher: Matcher):
    """处理机器人状态查询"""
    try:
        bot_status = get_bot_status()
        status_text = format_bot_status(bot_status)
        await matcher.send(status_text)
    except Exception as e:
        await matcher.send(f"❌ 获取机器人状态失败: {str(e)}")


async def handle_messages(matcher: Matcher):
    """处理消息统计查询"""
    try:
        message_stats = get_message_stats()
        message_text = format_message_stats(message_stats)
        await matcher.send(message_text)
    except Exception as e:
        await matcher.send(f"❌ 获取消息统计失败: {str(e)}")


async def handle_matchers(matcher: Matcher):
    """处理匹配器统计查询"""
    try:
        matcher_stats = get_matcher_stats(limit=10)
        matcher_text = format_matcher_stats(matcher_stats)
        await matcher.send(matcher_text)
    except Exception as e:
        await matcher.send(f"❌ 获取匹配器统计失败: {str(e)}")


async def handle_system(matcher: Matcher):
    """处理系统指标查询"""
    try:
        system_metrics = get_system_metrics()
        system_text = format_system_metrics(system_metrics)
        await matcher.send(system_text)
    except Exception as e:
        await matcher.send(f"❌ 获取系统指标失败: {str(e)}")


async def handle_uptime(matcher: Matcher):
    """处理运行时间查询"""
    try:
        system_metrics = get_system_metrics()
        if "error" not in system_metrics:
            uptime_text = "⏱️ 机器人运行时间\n"
            uptime_text += "=" * 30 + "\n"
            uptime_text += f"🚀 启动时间: {system_metrics['start_time']}\n"
            uptime_text += f"⏱️ 运行时长: {system_metrics['uptime']}\n"
            await matcher.send(uptime_text)
        else:
            await matcher.send(f"❌ 获取运行时间失败: {system_metrics['error']}")
    except Exception as e:
        await matcher.send(f"❌ 获取运行时间失败: {str(e)}")


async def handle_help(matcher: Matcher):
    """处理帮助查询"""
    try:
        help_text = format_help()
        await matcher.send(help_text)
    except Exception as e:
        await matcher.send(f"❌ 获取帮助信息失败: {str(e)}")


async def handle_query(matcher: Matcher, metric_query: str):
    """处理自定义指标查询"""
    try:
        # 解析查询字符串
        metric_name, labels = parse_metric_filter(metric_query)
        
        # 获取指标数据
        if labels:
            # 如果有标签过滤，使用 get_metric_values
            metric_values = get_metric_values(metric_name, labels)
            if not metric_values:
                await matcher.send(f"❌ 未找到匹配的指标: {metric_query}")
                return
            
            # 构建结果
            result = f"📊 指标查询: {metric_query}\n"
            result += "=" * 50 + "\n"
            
            for sample_labels, value in metric_values:
                if sample_labels:
                    labels_str = ", ".join([f"{k}=\"{v}\"" for k, v in sample_labels])
                    result += f"   📌 {labels_str}\n"
                else:
                    result += "   📌 (无标签)\n"
                result += f"      值: {format_large_number(value)}\n"
            
            await matcher.send(result)
        else:
            # 如果没有标签过滤，使用 get_metrics_by_name
            metric_data = get_metrics_by_name(metric_name)
            result_text = format_custom_metric(metric_name, metric_data)
            await matcher.send(result_text)
            
    except Exception as e:
        await matcher.send(f"❌ 查询指标失败: {str(e)}")


async def handle_list(matcher: Matcher):
    """处理列出所有指标"""
    try:
        all_metrics = list_all_metrics()
        result_text = format_metrics_list(all_metrics)
        await matcher.send(result_text)
    except Exception as e:
        await matcher.send(f"❌ 列出指标失败: {str(e)}")


async def handle_search(matcher: Matcher, keyword: str):
    """处理搜索指标"""
    try:
        matched_metrics = search_metrics(keyword)
        if not matched_metrics:
            await matcher.send(f"❌ 未找到包含 '{keyword}' 的指标")
            return
        
        title = f"🔍 搜索结果: '{keyword}'"
        result_text = format_metrics_list(matched_metrics, title)
        await matcher.send(result_text)
    except Exception as e:
        await matcher.send(f"❌ 搜索指标失败: {str(e)}")