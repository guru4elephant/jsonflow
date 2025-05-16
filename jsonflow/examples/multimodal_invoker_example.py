#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多模态模型示例

这个示例演示如何扩展ModelInvoker创建支持多模态输入（文本+图像）的MultimodalInvoker，
并在实际应用中使用它。
"""

import os
import json
import base64
from typing import Dict, Any, List
from jsonflow.operators.model import ModelInvoker
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver


class MultimodalInvoker(ModelInvoker):
    """支持多模态输入的模型操作符"""
    
    def __init__(self, 
                 model: str,
                 text_field: str = "text",
                 image_field: str = "image_path",
                 response_field: str = "response",
                 **kwargs):
        super().__init__(model=model, **kwargs)
        self.text_field = text_field
        self.image_field = image_field
        self.response_field = response_field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理包含文本和图像输入的请求
        
        Args:
            json_data: 包含文本和图像路径的JSON数据
            
        Returns:
            dict: 添加了模型响应的JSON数据
        """
        if not json_data:
            return json_data
            
        # 如果没有指定的字段，保持原样返回
        if self.text_field not in json_data or self.image_field not in json_data:
            return json_data
            
        result = json_data.copy()
        
        # 获取文本和图像路径
        text = result[self.text_field]
        image_path = result[self.image_field]
        
        # 读取并编码图像
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error reading image: {e}")
            # 如果图像读取失败，使用纯文本请求
            messages = [
                {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": f"[图像读取失败] {text}"}
            ]
            response = self.call_llm(messages)
            result[self.response_field] = response
            return result
        
        # 构建多模态消息
        messages = [
            {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }
        ]
        
        # 调用模型
        try:
            import openai
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
                
            client = openai.OpenAI(**client_kwargs)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **self.model_params
            )
            
            result[self.response_field] = response.choices[0].message.content
        except Exception as e:
            print(f"Error calling model: {e}")
            result[self.response_field] = f"Error: {str(e)}"
        
        return result


def main():
    """
    运行多模态模型示例。
    
    这个函数：
    1. 创建一个样本JSON数据集，包含图像分析任务
    2. 使用MultimodalInvoker处理数据
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
            "id": "img001",
            "text": "请描述这张图片并分析其中的主要内容。",
            "image_path": "examples/data/sample_image1.jpg",
            "metadata": {"type": "image_analysis"}
        },
        {
            "id": "img002",
            "text": "这个图表展示了什么趋势？请做简要分析。",
            "image_path": "examples/data/sample_chart.png",
            "metadata": {"type": "chart_analysis"}
        }
    ]
    
    # 确保数据目录存在
    os.makedirs("examples/data", exist_ok=True)
    os.makedirs("examples/output", exist_ok=True)
    
    # 如果示例图片不存在，提示用户
    if not os.path.exists("examples/data/sample_image1.jpg"):
        print("警告: 示例图片不存在。请将图片放置在 examples/data/ 目录下，并命名为 sample_image1.jpg 和 sample_chart.png。")
        print("或者修改示例数据中的 image_path 字段指向实际图片。")
    
    # 创建多模态处理管道
    pipeline = Pipeline([
        MultimodalInvoker(
            model="gpt-4-vision-preview",  # 确保使用支持视觉的模型
            api_key=api_key,
            text_field="text",
            image_field="image_path",
            response_field="analysis",
            system_prompt="你是一个专业的图像分析助手，善于描述图像内容并提供见解。"
        ),
        JsonSaver("examples/output/multimodal_results.jsonl")
    ])
    
    # 处理样本数据
    print("\n=== JSONFlow 多模态模型示例 ===")
    results = []
    
    for item in sample_data:
        print(f"\n处理 {item['id']}...")
        try:
            result = pipeline.process(item)
            print(f"✓ 分析完成")
            results.append(result)
        except Exception as e:
            print(f"✗ 处理失败: {e}")
    
    # 显示结果
    print("\n=== 处理结果 ===")
    for result in results:
        print(f"\nID: {result['id']}")
        print(f"提示: {result['text']}")
        print(f"分析: {result.get('analysis', '处理失败')}")
    
    print(f"\n结果已保存到 examples/output/multimodal_results.jsonl")


if __name__ == "__main__":
    main() 