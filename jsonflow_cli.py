#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSONFlow CLI工具 - 分析JSONL文件的键结构

用法: python jsonflow_cli.py analyze path/to/file.jsonl
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Dict, Any, Set, List

from jsonflow.io import JsonLoader
from jsonflow.operators.json_ops import JsonStructureExtractor
from jsonflow.core import Pipeline


def extract_key_structure(json_data: Dict[str, Any], prefix="") -> Dict[str, Set]:
    """
    递归提取JSON数据的键结构
    
    Args:
        json_data: JSON数据
        prefix: 当前键的前缀
        
    Returns:
        键结构信息字典，包含键的路径和数据类型
    """
    result = defaultdict(set)
    
    if not isinstance(json_data, dict):
        return result
    
    for key, value in json_data.items():
        current_path = f"{prefix}.{key}" if prefix else key
        
        # 记录键的类型
        if value is None:
            result[current_path].add("null")
        elif isinstance(value, bool):
            result[current_path].add("boolean")
        elif isinstance(value, int):
            result[current_path].add("integer")
        elif isinstance(value, float):
            result[current_path].add("number")
        elif isinstance(value, str):
            result[current_path].add("string")
        elif isinstance(value, list):
            result[current_path].add("array")
            
            # 分析数组中的元素类型（只取前10个元素样本）
            array_types = set()
            for i, item in enumerate(value[:10]):
                if isinstance(item, dict):
                    # 递归分析嵌套字典
                    nested_structure = extract_key_structure(item, f"{current_path}[*]")
                    for nested_key, nested_types in nested_structure.items():
                        result[nested_key].update(nested_types)
                else:
                    # 记录数组元素的类型
                    array_types.add(type(item).__name__)
            
            if array_types:
                result[f"{current_path}[*]"].update(array_types)
        elif isinstance(value, dict):
            result[current_path].add("object")
            
            # 递归分析嵌套字典
            nested_structure = extract_key_structure(value, current_path)
            for nested_key, nested_types in nested_structure.items():
                result[nested_key].update(nested_types)
    
    return result


def analyze_jsonl_keys(jsonl_file: str) -> None:
    """
    分析JSONL文件的键结构并打印
    
    Args:
        jsonl_file: JSONL文件路径
    """
    # 使用JsonLoader加载JSONL文件
    loader = JsonLoader(jsonl_file)
    
    # 收集所有键的结构信息
    all_keys = defaultdict(set)
    line_count = 0
    
    print(f"正在分析文件: {jsonl_file}")
    
    try:
        for json_line in loader:
            line_count += 1
            structure = extract_key_structure(json_line)
            
            # 合并键结构信息
            for key, types in structure.items():
                all_keys[key].update(types)
    except Exception as e:
        print(f"处理第 {line_count} 行时出错: {str(e)}")
        return
    
    # 打印键结构信息
    print(f"\n分析完成，共处理 {line_count} 行JSON数据")
    print("\n键结构分析结果:")
    print("=" * 80)
    print(f"{'键路径':<50} | {'数据类型':<30}")
    print("-" * 80)
    
    # 按键路径排序
    sorted_keys = sorted(all_keys.keys())
    for key in sorted_keys:
        types = list(all_keys[key])
        types_str = ", ".join(types)
        print(f"{key:<50} | {types_str:<30}")


def analyze_jsonl_with_pipeline(jsonl_file: str) -> None:
    """
    使用JSONFlow管道分析JSONL文件的键结构
    
    Args:
        jsonl_file: JSONL文件路径
    """
    # 使用JsonLoader加载JSONL文件
    loader = JsonLoader(jsonl_file)
    
    # 创建结构提取器
    structure_extractor = JsonStructureExtractor(extract_types=True, extract_nested=True)
    
    # 创建管道
    pipeline = Pipeline([structure_extractor])
    
    # 合并所有行的结构
    merged_structure = {}
    line_count = 0
    
    print(f"正在使用JSONFlow管道分析文件: {jsonl_file}")
    
    try:
        for json_line in loader:
            line_count += 1
            result = pipeline.process(json_line)
            
            # 合并结构信息
            for key, info in result.get("structure", {}).items():
                if key not in merged_structure:
                    merged_structure[key] = info
                else:
                    # 合并类型信息
                    if "types" in info and "types" in merged_structure[key]:
                        merged_structure[key]["types"].update(info["types"])
    except Exception as e:
        print(f"处理第 {line_count} 行时出错: {str(e)}")
        return
    
    # 打印键结构信息
    print(f"\n分析完成，共处理 {line_count} 行JSON数据")
    print("\n键结构分析结果:")
    print("=" * 80)
    print(f"{'键路径':<50} | {'数据类型':<30}")
    print("-" * 80)
    
    # 按键路径排序
    sorted_keys = sorted(merged_structure.keys())
    for key in sorted_keys:
        types = list(merged_structure[key].get("types", []))
        types_str = ", ".join(types)
        print(f"{key:<50} | {types_str:<30}")


def main():
    """主函数，解析命令行参数并执行相应的功能"""
    parser = argparse.ArgumentParser(description="JSONFlow命令行工具 - 分析JSONL文件的键结构")
    
    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析JSONL文件的键结构")
    analyze_parser.add_argument("jsonl_file", help="JSONL文件路径")
    analyze_parser.add_argument(
        "--method", 
        choices=["basic", "pipeline"], 
        default="pipeline",
        help="分析方法: basic (基本方法) 或 pipeline (使用JSONFlow管道)"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    if args.command == "analyze":
        if args.method == "pipeline":
            analyze_jsonl_with_pipeline(args.jsonl_file)
        else:
            analyze_jsonl_keys(args.jsonl_file)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 