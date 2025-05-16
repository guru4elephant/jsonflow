#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量图像标注示例

这个示例演示如何使用ImageCaptioningInvoker批量处理文件夹中的图像，
生成标注，并将结果保存为JSONL文件。
"""

import os
import json
import glob
import base64
from typing import Dict, Any, List, Optional
from jsonflow.operators.model import ModelInvoker
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver


class ImageCaptioningInvoker(ModelInvoker):
    """图像标注操作符"""
    
    def __init__(self, 
                 model: str,
                 image_field: str = "image_path",
                 caption_field: str = "caption",
                 caption_prompt: str = "请简要描述这张图片的内容。",
                 **kwargs):
        """
        初始化图像标注操作符
        
        Args:
            model: 模型名称（需要支持图像处理，如gpt-4-vision-preview）
            image_field: 输入图像路径的字段名，默认为"image_path"
            caption_field: 输出标注的字段名，默认为"caption"
            caption_prompt: 向模型发送的提示文本，默认为简单的描述请求
            **kwargs: 其他传递给ModelInvoker的参数
        """
        super().__init__(model=model, **kwargs)
        self.image_field = image_field
        self.caption_field = caption_field
        self.caption_prompt = caption_prompt
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理包含图像路径的JSON数据，生成图像标注
        
        Args:
            json_data: 包含图像路径的JSON数据
            
        Returns:
            dict: 添加了图像标注的JSON数据
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
            result[self.caption_field] = f"图像读取错误: {str(e)}"
            return result
        
        # 构建包含图像的消息
        messages = [
            {"role": "system", "content": self.system_prompt or "你是一个图像标注专家，善于准确描述图像内容。"},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": self.caption_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }
        ]
        
        # 调用支持图像的模型
        try:
            response = self.call_llm(messages)
            result[self.caption_field] = response
        except Exception as e:
            result[self.caption_field] = f"模型调用错误: {str(e)}"
        
        return result


def get_image_files(folder_path: str, extensions: List[str] = ['.jpg', '.jpeg', '.png']) -> List[str]:
    """
    获取文件夹中所有图像文件的路径
    
    Args:
        folder_path: 文件夹路径
        extensions: 图像文件扩展名列表
        
    Returns:
        List[str]: 图像文件路径列表
    """
    image_files = []
    for ext in extensions:
        pattern = os.path.join(folder_path, f"*{ext}")
        image_files.extend(glob.glob(pattern))
        # 同时支持大写扩展名
        pattern = os.path.join(folder_path, f"*{ext.upper()}")
        image_files.extend(glob.glob(pattern))
    return sorted(image_files)


def main():
    """
    运行批量图像标注示例。
    
    这个函数:
    1. 扫描指定文件夹中的所有图像
    2. 使用ImageCaptioningInvoker批量处理图像
    3. 保存标注结果为JSONL文件
    """
    # 配置参数
    input_folder = "examples/data/images"  # 输入图像文件夹
    output_file = "examples/output/batch_image_captions.jsonl"  # 输出JSONL文件
    
    # 设置API密钥（或从环境变量中获取）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量。请设置后再运行，或在代码中直接设置。")
        api_key = "your-api-key"  # 替换为你的实际API密钥
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入文件夹 '{input_folder}' 不存在。")
        print(f"创建文件夹 '{input_folder}' 并放入图像文件。")
        os.makedirs(input_folder, exist_ok=True)
        return
    
    # 获取图像文件列表
    image_files = get_image_files(input_folder)
    if not image_files:
        print(f"错误: 文件夹 '{input_folder}' 中没有找到图像文件。")
        return
    
    print(f"\n在 '{input_folder}' 中找到 {len(image_files)} 个图像文件。")
    
    # 创建图像JSON数据
    image_data = []
    for i, image_path in enumerate(image_files):
        filename = os.path.basename(image_path)
        image_data.append({
            "id": f"img{i+1:03d}",
            "image_path": image_path,
            "filename": filename,
            "metadata": {
                "source": input_folder,
                "extension": os.path.splitext(filename)[1].lower()
            }
        })
    
    # 创建图像标注管道
    pipeline = Pipeline([
        ImageCaptioningInvoker(
            model="gpt-4-vision-preview",  # 使用支持图像的模型
            api_key=api_key,
            image_field="image_path",
            caption_field="caption",
            caption_prompt="请详细描述这张图片的内容。",
            system_prompt="你是一个专业的图像描述专家，善于捕捉图像的细节和主要内容。请简洁准确地描述图像。",
            max_tokens=250
        ),
        JsonSaver(output_file)
    ])
    
    # 批量处理图像
    print("\n=== JSONFlow 批量图像标注 ===")
    
    # 处理所有图像
    print(f"\n开始批量处理 {len(image_data)} 个图像...")
    results = pipeline.process(image_data)
    print(f"批量处理完成，成功处理 {len(results)} 个图像。")
    
    # 显示部分结果
    if results:
        print("\n=== 部分标注结果示例 ===")
        for result in results[:3]:  # 只显示前3个结果
            print(f"\nID: {result['id']}")
            print(f"文件名: {result['filename']}")
            caption = result.get('caption', '处理失败')
            if len(caption) > 100:
                print(f"标注: {caption[:100]}...")
            else:
                print(f"标注: {caption}")
    
        if len(results) > 3:
            print(f"\n...还有 {len(results) - 3} 个结果未显示...")
    
    print(f"\n所有结果已保存到 {output_file}")


if __name__ == "__main__":
    main() 