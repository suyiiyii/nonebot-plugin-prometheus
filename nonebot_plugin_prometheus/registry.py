from typing import Any, Dict, List, Tuple, Optional
from prometheus_client import REGISTRY
from nonebot import logger


def get_metrics() -> Dict[str, Any]:
    """
    获取所有 Prometheus 指标的结构化数据
    
    Returns:
        Dict[str, Any]: 包含所有指标的结构化数据
            {
                "metrics": [
                    {
                        "name": "metric_name",
                        "type": "counter|gauge|histogram|summary|untyped",
                        "help": "metric description",
                        "samples": [
                            {
                                "name": "metric_name_total",
                                "labels": [("label1", "value1"), ("label2", "value2")],
                                "value": 42.0,
                                "timestamp": Optional[float]
                            }
                        ]
                    }
                ]
            }
    """
    try:
        result = {"metrics": []}
        
        # 遍历注册表中的所有指标族
        for metric_family in REGISTRY.collect():
            metric_info = {
                "name": metric_family.name,
                "type": metric_family.type,
                "help": metric_family.documentation,
                "samples": []
            }
            
            # 处理每个样本
            for sample in metric_family.samples:
                sample_info = {
                    "name": sample.name,
                    "labels": tuple(sorted(sample.labels.items())),
                    "value": sample.value,
                    "timestamp": sample.timestamp
                }
                metric_info["samples"].append(sample_info)
            
            result["metrics"].append(metric_info)
        
        logger.debug(f"Collected {len(result['metrics'])} metric families")
        return result
        
    except Exception as e:
        logger.error(f"获取指标数据失败: {e}")
        return {"metrics": [], "error": str(e)}


def get_metrics_by_name(metric_name: str) -> Dict[str, Any]:
    """
    根据指标名称获取特定的指标数据
    
    Args:
        metric_name: 指标名称（不包含后缀如 _total, _sum 等）
    
    Returns:
        Dict[str, Any]: 指定指标的结构化数据
    """
    try:
        all_metrics = get_metrics()
        matching_metrics = []
        
        for metric in all_metrics["metrics"]:
            # 检查基础名称是否匹配
            base_name = metric["name"]
            if (base_name == metric_name or 
                base_name.startswith(metric_name + "_") or
                metric_name.startswith(base_name + "_")):
                matching_metrics.append(metric)
        
        return {
            "metric_name": metric_name,
            "metrics": matching_metrics,
            "count": len(matching_metrics)
        }
        
    except Exception as e:
        logger.error(f"获取指标 {metric_name} 失败: {e}")
        return {"metric_name": metric_name, "metrics": [], "error": str(e)}


def get_metrics_by_type(metric_type: str) -> Dict[str, Any]:
    """
    根据指标类型获取指标数据
    
    Args:
        metric_type: 指标类型 (counter, gauge, histogram, summary, untyped)
    
    Returns:
        Dict[str, Any]: 指定类型的所有指标数据
    """
    try:
        all_metrics = get_metrics()
        matching_metrics = []
        
        for metric in all_metrics["metrics"]:
            if metric["type"] == metric_type:
                matching_metrics.append(metric)
        
        return {
            "type": metric_type,
            "metrics": matching_metrics,
            "count": len(matching_metrics)
        }
        
    except Exception as e:
        logger.error(f"获取类型为 {metric_type} 的指标失败: {e}")
        return {"type": metric_type, "metrics": [], "error": str(e)}


def get_metric_values(metric_name: str, labels: Optional[Dict[str, str]] = None) -> List[Tuple[Tuple[Tuple[str, str], ...], float]]:
    """
    获取特定指标的值，返回简化格式
    
    Args:
        metric_name: 指标名称
        labels: 可选的标签过滤条件
    
    Returns:
        List[Tuple[Tuple[Tuple[str, str], ...], float]]: 
            [(((label1, value1), (label2, value2)), value), ...]
    """
    try:
        result = []
        metric_data = get_metrics_by_name(metric_name)
        
        for metric in metric_data["metrics"]:
            for sample in metric["samples"]:
                # 对于 Counter 类型，只包含 _total 指标，排除 _created 指标
                if metric["type"] == "counter" and not sample["name"].endswith("_total"):
                    continue
                
                # 创建标签字典，添加指标名称作为 __name__
                sample_labels_dict = dict(sample["labels"])
                sample_labels_dict['__name__'] = sample["name"]
                
                # 过滤标签
                if labels:
                    match = True
                    for key, value in labels.items():
                        if sample_labels_dict.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                # 添加到结果 - 使用原始标签（不包含 __name__）
                result.append((sample["labels"], sample["value"]))
        
        return result
        
    except Exception as e:
        logger.error(f"获取指标值失败: {e}")
        return []


def list_all_metrics() -> List[Dict[str, str]]:
    """
    列出所有可用的指标
    
    Returns:
        List[Dict[str, str]]: 指标列表，包含名称、类型和描述
    """
    try:
        all_metrics = get_metrics()
        metrics_list = []
        
        for metric in all_metrics["metrics"]:
            metrics_list.append({
                "name": metric["name"],
                "type": metric["type"],
                "help": metric["help"],
                "sample_count": len(metric["samples"])
            })
        
        return sorted(metrics_list, key=lambda x: x["name"])
        
    except Exception as e:
        logger.error(f"列出指标失败: {e}")
        return []


def search_metrics(keyword: str) -> List[Dict[str, str]]:
    """
    搜索包含关键字的指标
    
    Args:
        keyword: 搜索关键字
    
    Returns:
        List[Dict[str, str]]: 匹配的指标列表
    """
    try:
        all_metrics = list_all_metrics()
        keyword_lower = keyword.lower()
        
        matched_metrics = []
        for metric in all_metrics:
            if (keyword_lower in metric["name"].lower() or 
                keyword_lower in metric["help"].lower() or
                keyword_lower in metric["type"].lower()):
                matched_metrics.append(metric)
        
        return matched_metrics
        
    except Exception as e:
        logger.error(f"搜索指标失败: {e}")
        return []


def parse_metric_filter(metric_query: str) -> tuple[str, Dict[str, str]]:
    """
    解析指标查询字符串，提取指标名称和标签过滤条件
    
    Args:
        metric_query: 查询字符串，如 "http_requests_total{method="GET"}"
    
    Returns:
        tuple[str, Dict[str, str]]: (指标名称, 标签过滤条件)
    """
    try:
        # 解析标签过滤
        if '{' in metric_query and '}' in metric_query:
            name_part, filter_part = metric_query.split('{', 1)
            filter_part = filter_part.rstrip('}')
            
            # 解析标签对
            labels = {}
            for pair in filter_part.split(','):
                pair = pair.strip()
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # 去除引号
                    value = value.strip('"\'')
                    labels[key.strip()] = value
            
            return name_part.strip(), labels
        else:
            return metric_query.strip(), {}
            
    except Exception as e:
        logger.error(f"解析指标查询失败: {e}")
        return metric_query.strip(), {}


def debug_metrics():
    """
    调试函数：打印所有指标的概览信息
    """
    try:
        all_metrics = get_metrics()
        print(f"总共收集到 {len(all_metrics['metrics'])} 个指标族")
        
        for metric in all_metrics["metrics"]:
            print(f"指标: {metric['name']} ({metric['type']})")
            print(f"  帮助信息: {metric['help']}")
            print(f"  样本数量: {len(metric['samples'])}")
            
            for sample in metric["samples"][:3]:  # 只显示前3个样本
                print(f"    {sample['name']}: {sample['value']} {dict(sample['labels'])}")
            
            if len(metric["samples"]) > 3:
                print(f"    ... 还有 {len(metric['samples']) - 3} 个样本")
            print()
            
    except Exception as e:
        print(f"调试失败: {e}")