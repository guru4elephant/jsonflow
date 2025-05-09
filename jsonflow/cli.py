#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JSONFlow命令行接口

提供命令行工具来执行常见的JSONFlow操作。
"""

import argparse
import sys
import json
from typing import List, Dict, Any

from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonFilter
from jsonflow.operators.model import ModelInvoker


def main():
    """JSONFlow命令行工具的主函数"""
    parser = argparse.ArgumentParser(description="JSONFlow命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="要执行的命令")

    # 版本信息
    parser.add_argument("--version", action="store_true", help="显示版本信息")

    # 规范化JSON文件
    normalize_parser = subparsers.add_parser("normalize", help="规范化JSON文件")
    normalize_parser.add_argument("input", help="输入JSONL文件路径")
    normalize_parser.add_argument("output", help="输出JSONL文件路径")
    normalize_parser.add_argument("--fields", nargs="+", help="要规范化的字段，不指定则处理所有文本字段")
    normalize_parser.add_argument("--lower", action="store_true", help="转换为小写")
    normalize_parser.add_argument("--upper", action="store_true", help="转换为大写")

    # 调用模型
    model_parser = subparsers.add_parser("model", help="使用模型处理JSON文件")
    model_parser.add_argument("input", help="输入JSONL文件路径")
    model_parser.add_argument("output", help="输出JSONL文件路径")
    model_parser.add_argument("--model", default="gpt-3.5-turbo", help="模型名称")
    model_parser.add_argument("--prompt-field", default="prompt", help="提示字段名")
    model_parser.add_argument("--response-field", default="response", help="响应字段名")
    model_parser.add_argument("--system-prompt", help="系统提示")
    model_parser.add_argument("--api-key", help="API密钥，不提供则从环境变量中获取")
    model_parser.add_argument("--base-url", help="API基础URL，适用于自定义端点")
    
    # 过滤JSON文件
    filter_parser = subparsers.add_parser("filter", help="过滤JSON文件")
    filter_parser.add_argument("input", help="输入JSONL文件路径")
    filter_parser.add_argument("output", help="输出JSONL文件路径")
    filter_parser.add_argument("--condition", required=True, help="过滤条件，Python表达式")

    args = parser.parse_args()

    # 显示版本信息
    if args.version:
        from importlib.metadata import version
        print(f"JSONFlow版本: {version('jsonflow')}")
        return 0

    # 处理命令
    if args.command == "normalize":
        return normalize_command(args)
    elif args.command == "model":
        return model_command(args)
    elif args.command == "filter":
        return filter_command(args)
    else:
        parser.print_help()
        return 1


def normalize_command(args):
    """规范化JSON文件"""
    # 创建文本规范化操作符
    normalizer = TextNormalizer(
        text_fields=args.fields if args.fields else None,
        lower_case=args.lower,
        upper_case=args.upper,
    )
    
    # 创建pipeline
    pipeline = Pipeline([normalizer])
    
    # 处理文件
    process_jsonl(args.input, args.output, pipeline)
    return 0


def model_command(args):
    """使用模型处理JSON文件"""
    # 准备OpenAI参数
    openai_params = {}
    if args.base_url:
        openai_params["base_url"] = args.base_url
    
    # 创建模型调用操作符
    model_invoker = ModelInvoker(
        model=args.model,
        prompt_field=args.prompt_field,
        response_field=args.response_field,
        system_prompt=args.system_prompt,
        api_key=args.api_key,
        openai_params=openai_params if openai_params else None,
    )
    
    # 创建pipeline
    pipeline = Pipeline([model_invoker])
    
    # 处理文件
    process_jsonl(args.input, args.output, pipeline)
    return 0


def filter_command(args):
    """过滤JSON文件"""
    # 创建过滤操作符
    json_filter = JsonFilter(args.condition)
    
    # 创建pipeline
    pipeline = Pipeline([json_filter])
    
    # 处理文件
    process_jsonl(args.input, args.output, pipeline)
    return 0


def process_jsonl(input_path: str, output_path: str, pipeline: Pipeline):
    """处理JSONL文件"""
    # 加载JSON数据
    json_loader = JsonLoader(input_path)
    json_saver = JsonSaver(output_path)
    
    # 处理每个JSON对象
    count = 0
    for json_data in json_loader:
        result = pipeline.process(json_data)
        json_saver.write(result)
        count += 1
    
    print(f"已处理 {count} 条JSON数据，结果保存到 {output_path}")


if __name__ == "__main__":
    sys.exit(main()) 