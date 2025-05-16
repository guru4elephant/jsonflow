#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高级图像分析示例

这个示例演示如何扩展ModelInvoker创建一个高级图像分析操作符，
可以同时生成多种类型的图像分析结果，包括简短标题、详细描述和结构化分析。
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional, Union
from jsonflow.operators.model import ModelInvoker
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver


class AdvancedImageAnalyzer(ModelInvoker):
    """高级图像分析操作符，可以生成多种类型的图像分析结果"""
    
    def __init__(self, 
                 model: str,
                 image_field: str = "image_path",
                 analysis_types: List[str] = ["caption"],
                 output_fields: Optional[Dict[str, str]] = None,
                 prompts: Optional[Dict[str, str]] = None,
                 **kwargs):
        """
        初始化高级图像分析操作符
        
        Args:
            model: 模型名称（需要支持图像处理，如gpt-4-vision-preview）
            image_field: 输入图像路径的字段名，默认为"image_path"
            analysis_types: 需要生成的分析类型列表，可选值包括：
                            - "caption": 简短的图像标题
                            - "description": 详细的图像描述
                            - "objects": 检测到的物体列表
                            - "content_analysis": 内容分析（场景、情感等）
            output_fields: 各个分析类型的输出字段名映射，如不指定则使用默认值
            prompts: 各个分析类型的提示文本映射，如不指定则使用默认值
            **kwargs: 其他传递给ModelInvoker的参数
        """
        super().__init__(model=model, **kwargs)
        self.image_field = image_field
        self.analysis_types = analysis_types
        
        # 设置默认输出字段
        self.default_output_fields = {
            "caption": "caption",
            "description": "description",
            "objects": "objects",
            "content_analysis": "content_analysis"
        }
        self.output_fields = self.default_output_fields.copy()
        if output_fields:
            self.output_fields.update(output_fields)
        
        # 设置默认提示文本
        self.default_prompts = {
            "caption": "为这张图片创建一个简短的标题（20字以内）。",
            "description": "详细描述这张图片的内容，包括主要对象、场景和细节。",
            "objects": "列出图片中可以识别的所有物体，返回一个JSON数组格式。",
            "content_analysis": "分析这张图片的内容，包括场景类型、主要主题、情感基调和可能的用途。"
        }
        self.prompts = self.default_prompts.copy()
        if prompts:
            self.prompts.update(prompts)
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理包含图像路径的JSON数据，生成多种类型的图像分析结果
        
        Args:
            json_data: 包含图像路径的JSON数据
            
        Returns:
            dict: 添加了图像分析结果的JSON数据
        """
        if not json_data or self.image_field not in json_data:
            return json_data
            
        result = json_data.copy()
        image_path = result[self.image_field]
        
        # 读取并编码图像
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            error_msg = f"图像读取错误: {str(e)}"
            for analysis_type in self.analysis_types:
                output_field = self.output_fields.get(analysis_type)
                if output_field:
                    result[output_field] = error_msg
            return result
        
        # 为每种分析类型生成结果
        for analysis_type in self.analysis_types:
            output_field = self.output_fields.get(analysis_type)
            if not output_field:
                continue
                
            prompt = self.prompts.get(analysis_type, self.default_prompts.get(analysis_type, "分析这张图片。"))
            
            # 针对不同分析类型的系统提示和格式要求
            system_prompt = self.system_prompt or "你是一个专业的图像分析专家，善于准确、详细地分析图像内容。"
            if analysis_type == "caption":
                system_prompt = "你是一个专业的图像标题生成专家。请提供简短、精确、有吸引力的标题。不要使用句号结尾。"
            elif analysis_type == "objects":
                system_prompt = "你是一个专业的物体检测专家。请以JSON数组格式返回图像中检测到的所有物体，每个物体包含名称和可信度。"
                prompt = "识别并列出图片中所有可见的物体，以JSON数组格式返回，格式为[{\"name\": \"物体名称\", \"confidence\": \"高/中/低\"}]。"
            elif analysis_type == "content_analysis":
                system_prompt = "你是一个专业的图像内容分析专家，善于解读图像的场景、主题、情感和用途。"
            
            # 构建消息
            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                    ]
                }
            ]
            
            # 调用模型
            try:
                response = self.call_llm(messages)
                
                # 对于objects分析类型，尝试解析JSON
                if analysis_type == "objects" and response:
                    try:
                        # 提取JSON部分（可能包含在文本中）
                        json_start = response.find('[')
                        json_end = response.rfind(']') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_str = response[json_start:json_end]
                            result[output_field] = json.loads(json_str)
                        else:
                            result[output_field] = response
                    except json.JSONDecodeError:
                        result[output_field] = response
                else:
                    result[output_field] = response
                    
            except Exception as e:
                result[output_field] = f"分析错误 ({analysis_type}): {str(e)}"
        
        return result


def main():
    """
    运行高级图像分析示例。
    
    这个函数:
    1. 创建一个AdvancedImageAnalyzer实例
    2. 处理一张示例图像，生成多种分析结果
    3. 保存分析结果
    """
    # 设置API密钥（或从环境变量中获取）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量。请设置后再运行，或在代码中直接设置。")
        api_key = "your-api-key"  # 替换为你的实际API密钥
    
    # 创建示例数据目录
    os.makedirs("examples/data/images", exist_ok=True)
    os.makedirs("examples/output", exist_ok=True)
    
    # 示例图像路径
    image_path = "examples/data/images/sample.jpg"
    
    # 确认图像是否存在
    if not os.path.exists(image_path):
        print(f"警告: 示例图像不存在: {image_path}")
        print("请将一张图像文件放置在此路径，或修改代码中的图像路径。")
        return
    
    # 创建示例数据
    sample_data = {
        "id": "img001",
        "image_path": image_path,
        "filename": os.path.basename(image_path),
        "metadata": {"analyzed_at": "2023-06-01"}
    }
    
    # 创建图像分析管道
    pipeline = Pipeline([
        AdvancedImageAnalyzer(
            model="gpt-4-vision-preview",  # 使用支持图像的模型
            api_key=api_key,
            image_field="image_path",
            analysis_types=["caption", "description", "objects", "content_analysis"],
            system_prompt="你是一个专业的图像分析专家，能够精确分析图像内容和含义。",
            max_tokens=500,
            temperature=0.5
        ),
        JsonSaver("examples/output/advanced_image_analysis.json")
    ])
    
    # 处理图像
    print("\n=== JSONFlow 高级图像分析示例 ===")
    print(f"\n分析图像: {image_path}")
    
    try:
        result = pipeline.process(sample_data)
        print("✓ 分析完成")
        
        # 显示结果
        print("\n=== 分析结果 ===")
        if "caption" in result:
            print(f"\n标题: {result['caption']}")
        
        if "description" in result:
            description = result["description"]
            print(f"\n描述: {description[:150]}..." if len(description) > 150 else f"\n描述: {description}")
        
        if "objects" in result:
            objects = result["objects"]
            if isinstance(objects, list):
                print(f"\n检测到的物体: ({len(objects)}个)")
                for obj in objects[:5]:  # 只显示前5个
                    if isinstance(obj, dict):
                        print(f"- {obj.get('name', 'Unknown')} (置信度: {obj.get('confidence', '未知')})")
            else:
                print(f"\n物体列表: {str(objects)[:100]}...")
        
        if "content_analysis" in result:
            analysis = result["content_analysis"]
            print(f"\n内容分析: {analysis[:150]}..." if len(analysis) > 150 else f"\n内容分析: {analysis}")
        
        print(f"\n完整结果已保存到 examples/output/advanced_image_analysis.json")
        
    except Exception as e:
        print(f"✗ 处理失败: {e}")


if __name__ == "__main__":
    main() 