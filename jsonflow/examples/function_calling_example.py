#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
函数调用模型示例

这个示例演示如何扩展ModelInvoker创建支持函数调用的FunctionCallingInvoker，
并在实际应用中使用它进行结构化数据提取。
"""

import os
import json
from typing import Dict, Any, List
from jsonflow.operators.model import ModelInvoker
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver


class FunctionCallingInvoker(ModelInvoker):
    """支持函数调用的模型操作符"""
    
    def __init__(self, 
                 model: str,
                 prompt_field: str = "prompt",
                 response_field: str = "response",
                 functions_field: str = "functions",
                 function_results_field: str = "function_results",
                 **kwargs):
        super().__init__(model=model, **kwargs)
        self.prompt_field = prompt_field
        self.response_field = response_field
        self.functions_field = functions_field
        self.function_results_field = function_results_field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理函数调用请求
        
        Args:
            json_data: 包含提示和可用函数的JSON数据
            
        Returns:
            dict: 添加了模型响应和函数调用结果的JSON数据
        """
        if not json_data or self.prompt_field not in json_data:
            return json_data
            
        result = json_data.copy()
        
        # 获取提示和函数定义
        prompt = result[self.prompt_field]
        functions = result.get(self.functions_field, [])
        
        if not functions:
            # 如果没有函数定义，就使用普通的处理逻辑
            messages = [
                {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            response = self.call_llm(messages)
            result[self.response_field] = response
            return result
        
        # 构建带函数定义的请求
        messages = [
            {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        # 添加函数调用相关参数
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
            
        try:
            import openai
            client = openai.OpenAI(**client_kwargs)
            
            # 调用API请求函数调用
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **self.model_params
            )
            
            function_calling_results = []
            
            # 处理函数调用响应
            message = response.choices[0].message
            result[self.response_field] = message.content or ""
            
            # 如果有函数调用
            if hasattr(message, 'function_call') and message.function_call:
                function_call = message.function_call
                function_calling_results.append({
                    "name": function_call.name,
                    "arguments": json.loads(function_call.arguments)
                })
            
            # 存储函数调用结果
            result[self.function_results_field] = function_calling_results
            
        except Exception as e:
            print(f"Error in function calling: {e}")
            messages = [
                {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            # 出错时回退到普通响应
            response = self.call_llm(messages)
            result[self.response_field] = response
        
        return result


def main():
    """
    运行函数调用模型示例。
    
    这个函数：
    1. 创建一个包含结构化数据提取任务的样本JSON数据集
    2. 使用FunctionCallingInvoker处理数据
    3. 输出并保存结构化结果
    """
    # 设置API密钥（或从环境变量中获取）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量。请设置后再运行，或在代码中直接设置。")
        api_key = "your-api-key"  # 替换为你的实际API密钥
    
    # 定义用于提取个人信息的函数模式
    extract_person_function = {
        "name": "extract_person_info",
        "description": "从文本中提取人物信息",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "人物的全名"
                },
                "age": {
                    "type": "integer",
                    "description": "人物的年龄"
                },
                "occupation": {
                    "type": "string",
                    "description": "人物的职业"
                },
                "email": {
                    "type": "string",
                    "description": "人物的电子邮件地址（如果有）"
                },
                "phone": {
                    "type": "string",
                    "description": "人物的电话号码（如果有）"
                },
                "location": {
                    "type": "string",
                    "description": "人物所在的城市或地区（如果提到）"
                }
            },
            "required": ["name"]
        }
    }
    
    # 创建示例数据
    sample_data = [
        {
            "id": "person001",
            "prompt": "张明是一名34岁的软件工程师，他住在上海，邮箱是zhangming@example.com，电话是13812345678。",
            "functions": [extract_person_function],
            "metadata": {"type": "person_info"}
        },
        {
            "id": "person002",
            "prompt": "李华，29岁，现任北京某科技公司的产品经理，联系方式：lihua@example.com",
            "functions": [extract_person_function],
            "metadata": {"type": "person_info"}
        },
        {
            "id": "text001",
            "prompt": "今天天气很好，阳光明媚。",
            "functions": [extract_person_function],
            "metadata": {"type": "no_person_info"}
        }
    ]
    
    # 确保输出目录存在
    os.makedirs("examples/output", exist_ok=True)
    
    # 创建函数调用处理管道
    pipeline = Pipeline([
        FunctionCallingInvoker(
            model="gpt-3.5-turbo",
            api_key=api_key,
            prompt_field="prompt",
            response_field="response",
            functions_field="functions",
            function_results_field="extracted_info",
            system_prompt="你是一个数据提取助手，专门从文本中提取结构化信息。"
        ),
        JsonSaver("examples/output/function_calling_results.jsonl")
    ])
    
    # 处理样本数据
    print("\n=== JSONFlow 函数调用示例 ===")
    results = []
    
    for item in sample_data:
        print(f"\n处理 {item['id']}...")
        try:
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
        
        # 显示函数调用结果
        function_results = result.get("extracted_info", [])
        if function_results:
            for func_result in function_results:
                print(f"函数调用: {func_result['name']}")
                print(f"参数: {json.dumps(func_result['arguments'], ensure_ascii=False, indent=2)}")
        else:
            print(f"响应: {result.get('response', '无响应')}")
    
    print(f"\n结果已保存到 examples/output/function_calling_results.jsonl")


if __name__ == "__main__":
    main() 