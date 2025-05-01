#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSON结构分析示例

此示例展示如何使用JsonStructureExtractor操作符分析JSON数据的结构。
"""

import json
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import JsonStructureExtractor


def set_to_list(obj):
    """
    将JSON对象中的set转换为list，以便JSON序列化
    
    Args:
        obj: 要转换的对象
        
    Returns:
        转换后的对象
    """
    if isinstance(obj, dict):
        return {k: set_to_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [set_to_list(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    else:
        return obj


def main():
    """
    展示如何使用JsonStructureExtractor分析JSON结构
    """
    # 示例JSON数据
    sample_data = {
        "id": 12345,
        "title": "JSON结构分析示例",
        "user": {
            "name": "张三",
            "email": "zhangsan@example.com",
            "role": "admin",
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        },
        "items": [
            {
                "id": 1,
                "name": "物品1",
                "price": 99.9
            },
            {
                "id": 2,
                "name": "物品2",
                "price": 199.9
            }
        ],
        "tags": ["json", "analysis", "example"],
        "active": True,
        "created_at": "2023-01-01T12:00:00Z"
    }
    
    # 创建结构提取器
    structure_extractor = JsonStructureExtractor(
        extract_types=True,
        extract_nested=True,
        include_original=False
    )
    
    # 创建管道
    pipeline = Pipeline([structure_extractor])
    
    # 处理数据
    result = pipeline.process(sample_data)
    
    # 打印结果
    print("JSON结构分析结果:")
    print("=" * 80)
    print(f"{'键路径':<50} | {'数据类型':<30}")
    print("-" * 80)
    
    # 按键路径排序
    sorted_keys = sorted(result["structure"].keys())
    for key in sorted_keys:
        key_info = result["structure"][key]
        types = list(key_info.get("types", []))
        types_str = ", ".join(types)
        print(f"{key:<50} | {types_str:<30}")
    
    # 将结果中的set转换为list，以便JSON序列化
    serializable_result = set_to_list(result)
    
    # 保存结果为JSON文件(可选)
    with open("structure_analysis_result.json", "w", encoding="utf-8") as f:
        json.dump(serializable_result, f, ensure_ascii=False, indent=2)
    
    print("\n结构分析结果已保存到 structure_analysis_result.json")


if __name__ == "__main__":
    main() 