#!/usr/bin/env python
# coding=utf-8

"""
集合处理示例

演示如何使用JsonFlow处理JSON集合（列表），包括拆分和合并操作。
"""

import json
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonSplitter, JsonAggregator
from jsonflow.operators.model import ModelInvoker

def run_json_splitter_example():
    """演示拆分JSON操作"""
    
    # 创建示例数据
    input_data = {
        "id": "12345",
        "items": [
            {"text": "First item text"},
            {"text": "Second item text"},
            {"text": "Third item text"}
        ],
        "metadata": {
            "source": "example",
            "created_at": "2023-05-01"
        }
    }
    
    # 创建管道，使用展平模式
    pipeline = Pipeline([
        # 拆分阶段：将'items'字段拆分为多个独立JSON对象
        JsonSplitter(split_field='items', keep_original=True),
        
        # 处理阶段：对拆分后的每个项目进行处理
        TextNormalizer(),
    ], collection_mode=Pipeline.FLATTEN)  # 使用展平模式处理列表
    
    # 处理数据
    results = pipeline.process(input_data)
    
    # 打印结果
    print("拆分后的结果 (共 {} 个独立对象):".format(len(results)))
    for i, result in enumerate(results):
        print(f"结果 {i+1}:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print()
    
    return results

def run_aggregator_example(split_results):
    """演示合并JSON操作"""
    
    # 创建管道，使用嵌套模式
    pipeline = Pipeline([
        # 合并阶段：将所有对象合并到一个列表中
        JsonAggregator(aggregate_field='processed_items', strategy='list')
    ], collection_mode=Pipeline.NESTED)  # 使用嵌套模式保持列表结构
    
    # 处理数据（传入上一阶段的列表结果）
    result = pipeline.process(split_results)
    
    # 打印结果
    print("合并后的结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    
    return result

def run_batch_processing_example():
    """演示批量处理JSON数据"""
    
    # 创建一些示例数据
    input_data = [
        {"id": "1", "text": "First sample text"},
        {"id": "2", "text": "Second sample text"},
        {"id": "3", "text": "Third sample text"},
        {"id": "4", "text": "Fourth sample text"},
        {"id": "5", "text": "Fifth sample text"}
    ]
    
    # 创建支持批处理的管道，使用嵌套模式
    pipeline = Pipeline([
        TextNormalizer(),  # 处理文本（不支持批处理，但Pipeline会自动处理）
        # 可以添加支持批处理的自定义操作符
    ], collection_mode=Pipeline.NESTED)
    
    # 处理数据（作为批次一次性处理）
    results = pipeline.process(input_data)
    
    # 打印结果
    print("批量处理结果 (共 {} 个对象):".format(len(results)))
    for i, result in enumerate(results):
        print(f"结果 {i+1}: {json.dumps(result, ensure_ascii=False)}")
    
    return results

def run_complete_example():
    """运行完整示例流程"""
    print("=== 1. 拆分JSON示例 ===")
    split_results = run_json_splitter_example()
    
    print("\n=== 2. 合并JSON示例 ===")
    run_aggregator_example(split_results)
    
    print("\n=== 3. 批量处理示例 ===")
    run_batch_processing_example()
    
    print("\n=== 4. 通过JsonLoader批量加载示例 ===")
    # 在实际场景中，可以使用JsonLoader的load_batch方法批量加载数据
    print("示例代码:")
    print("""
    loader = JsonLoader("input.jsonl")
    saver = JsonSaver("output.jsonl")
    
    # 使用load_batch方法批量加载和处理
    for batch in loader.load_batch(batch_size=100):
        results = pipeline.process(batch)
        saver.write(results)
    """)

if __name__ == "__main__":
    run_complete_example() 