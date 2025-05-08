#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Claude 模型调用示例

此示例展示如何使用 jsonflow 的 ModelInvoker 操作符调用 Claude 模型。
"""

from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker
import os
import json


def main():
    """
    展示如何使用 ModelInvoker 调用 Claude 模型的示例
    """
    # 配置 API 参数
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("BASE_URL", "")
    model_name = "claude-3-7-sonnet-20250219"  # 使用claude-3-7-sonnet模型
    
    print(f"使用模型: {model_name}")
    print(f"API端点: {base_url}")

    # 创建一个使用 Claude 模型的 pipeline
    pipeline = Pipeline([
        # 文本标准化，处理 text_fields 指定的字段
        TextNormalizer(
            text_fields=["prompt"],  # 指定要处理的字段
            strip=True,              # 去除两端空白
            remove_extra_spaces=True,# 删除多余空格
        ),
        
        # 使用 ModelInvoker 调用 Claude 模型
        ModelInvoker(
            model=model_name,  # Claude 模型名称
            system_prompt="你是一个专业的助手，请提供简洁有用的回答。",
            prompt_field="prompt",           # 使用 prompt 作为提示字段
            response_field="claude_response", # 将响应存储在 claude_response 字段中
            api_key=api_key,
            temperature=0.7,
            max_tokens=100,  # 限制生成长度，加快响应速度
            openai_params={"base_url": base_url}  # 传递自定义 API 端点
        ),
    ])

    # 创建 JsonSaver 用于保存结果
    output_file = "claude_output.jsonl"
    
    # 处理单个 JSON 示例
    test_json = {
        "prompt": "简单介绍一下你自己",
        "metadata": {
            "query_id": "12345",
            "timestamp": "2023-09-01T12:00:00Z"
        }
    }
    
    print("\n处理单个查询...")
    # 处理并打印结果
    result = pipeline.process(test_json)
    print("\n单个 JSON 处理结果:")
    print(f"{result}\n")
    
    # 保存结果到文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False) + '\n')
    print(f"结果已保存到 {output_file}\n")

    # 处理 JSONL 文件示例
    print("处理批量 JSONL 文件示例:")
    input_file = "input.jsonl"  # 使用现有的 input.jsonl
    output_file = "claude_results.jsonl"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"警告: 输入文件 {input_file} 不存在。创建示例文件...")
        # 创建示例 JSONL 文件
        with open(input_file, "w", encoding="utf-8") as f:
            f.write('{"prompt": "什么是人工智能?", "id": "001"}\n')
            f.write('{"prompt": "简述机器学习和深度学习的区别", "id": "002"}\n')
            f.write('{"prompt": "介绍一下自然语言处理技术", "id": "003"}\n')
        print(f"已创建示例文件 {input_file}")
    else:
        print(f"使用现有文件 {input_file}")

    # 从 JSONL 文件加载数据并处理
    json_loader = JsonLoader(input_file)
    
    # 清空输出文件（用write模式打开并立即关闭）
    with open(output_file, 'w', encoding='utf-8') as f:
        pass
        
    # 创建 JsonSaver - 它会以追加模式保存数据
    json_saver = JsonSaver(output_file)
    
    # 处理每个输入
    results = []
    for i, json_data in enumerate(json_loader):
        print(f"处理第 {i+1} 条数据...")
        try:
            result = pipeline.process(json_data)
            json_saver.write(result)
            results.append(result)
        except Exception as e:
            print(f"处理第 {i+1} 条数据时出错: {e}")
            error_result = json_data.copy()
            error_result["error"] = str(e)
            json_saver.write(error_result)
            results.append(error_result)
    
    print(f"\n处理完成。结果已保存到 {output_file}")
    
    # 打印批处理结果摘要
    print("\n批处理结果摘要:")
    for i, result in enumerate(results):
        if "claude_response" in result:
            response = result["claude_response"]
            # 只展示前80个字符
            print(f"查询 {i+1}: {result.get('prompt', '')[:30]}...")
            print(f"回答: {response[:80]}...\n")
        else:
            print(f"查询 {i+1}: 处理失败 - {result.get('error', '未知错误')}\n")

if __name__ == "__main__":
    main() 