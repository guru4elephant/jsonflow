#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Pipeline Example

这个示例演示如何在JSONFlow中使用大语言模型处理管道。
"""

import os
import json
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

def main():
    """
    运行LLM处理管道示例。
    
    这个函数：
    1. 创建一个包含文本归一化和LLM处理的管道
    2. 处理一组示例JSON数据
    3. 保存处理结果
    """
    # 设置API密钥（或从环境变量中获取）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量。请设置后再运行，或在代码中直接设置。")
        api_key = "your-api-key"  # 替换为你的实际API密钥
    
    # 创建示例数据
    sample_data = [
        {
            "id": "query001",
            "prompt": "解释什么是JSON数据流处理？",
            "metadata": {"category": "technical"}
        },
        {
            "id": "query002",
            "prompt": "用简单的语言描述什么是pipeline模式？",
            "metadata": {"category": "technical"}
        },
        {
            "id": "query003",
            "prompt": "给我一个Python中处理JSON数据的示例代码。",
            "metadata": {"category": "code"}
        }
    ]
    
    # 创建输出目录
    os.makedirs("examples/output", exist_ok=True)
    
    # 保存输入数据
    with open("examples/output/llm_input.jsonl", "w", encoding="utf-8") as f:
        for item in sample_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    
    # 创建处理管道
    pipeline = Pipeline([
        # 文本归一化步骤，清理和格式化文本
        TextNormalizer(text_fields=["prompt"]),
        
        # LLM处理步骤，使用ModelInvoker调用大语言模型
        ModelInvoker(
            model="gpt-3.5-turbo",
            api_key=api_key,
            prompt_field="prompt",
            response_field="response",
            system_prompt="你是一个友好的AI助手，专长于解释技术概念。请用简洁清晰的语言回答问题。",
            max_tokens=500,
            temperature=0.7
        ),
        
        # 保存处理结果
        JsonSaver("examples/output/llm_output.jsonl")
    ])
    
    # 处理示例数据
    print("\n=== JSONFlow LLM Pipeline示例 ===")
    results = []
    
    # 从保存的文件加载数据并处理
    json_loader = JsonLoader("examples/output/llm_input.jsonl")
    
    for item in json_loader:
        print(f"\n处理 {item['id']}...")
        try:
            # 处理单个项目
            result = pipeline.process(item)
            print(f"✓ 处理完成")
            results.append(result)
        except Exception as e:
            print(f"✗ 处理失败: {e}")
    
    # 显示结果
    print("\n=== 处理结果 ===")
    for result in results:
        print(f"\nID: {result['id']}")
        print(f"提示: {result['prompt']}")
        print(f"回复: {result['response'][:100]}..." if len(result.get('response', '')) > 100 else f"回复: {result.get('response', '')}")
    
    print(f"\n结果已保存到 examples/output/llm_output.jsonl")

    # 演示批量处理
    print("\n=== 演示批量处理 ===")
    batch_results = pipeline.process(sample_data)
    print(f"批量处理完成，处理了 {len(batch_results)} 个项目")


if __name__ == "__main__":
    main() 