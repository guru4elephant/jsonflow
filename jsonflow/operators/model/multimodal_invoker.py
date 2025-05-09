"""
多模态模型调用操作符模块

该模块定义了MultimodalInvoker操作符，用于调用支持图像和文本的多模态大语言模型。
"""

import os
import json
from typing import Dict, Any, List, Optional, Union

from jsonflow.operators.model.model_invoker import ModelInvoker

class MultimodalInvoker(ModelInvoker):
    """
    多模态大语言模型调用操作符
    
    该操作符用于调用支持图像和文本的多模态大语言模型，处理JSON数据中的复杂消息，并将结果存储在JSON中。
    支持包含图像和文本的OpenAI格式消息。
    """
    
    def __init__(self,
                 model: str,
                 message_field: str = "message",
                 response_field: str = "response",
                 api_key: Optional[str] = None,
                 max_tokens: Optional[int] = None,
                 temperature: float = 0.7,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 openai_params: Optional[Dict[str, Any]] = None,
                 **model_params):
        """
        初始化MultimodalInvoker
        
        Args:
            model (str): 模型名称
            message_field (str): 输入消息字段名，默认为"message"，应包含完整的OpenAI格式消息
            response_field (str): 输出字段名，默认为"response"
            api_key (str, optional): API密钥，如果不提供则从环境变量中获取
            max_tokens (int, optional): 生成的最大令牌数
            temperature (float): 采样温度，值越高结果越多样，值越低结果越确定
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            openai_params (dict, optional): OpenAI客户端的额外参数，如base_url等
            **model_params: 其他模型参数
        """
        super().__init__(
            model=model,
            prompt_field=message_field,  # 重用prompt_field作为message_field
            response_field=response_field,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
            name=name or "MultimodalInvoker",
            description=description or f"Invokes {model} model with multimodal input",
            openai_params=openai_params,
            **model_params
        )
        self.message_field = message_field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，调用多模态模型
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data or self.message_field not in json_data:
            return json_data
        
        result = json_data.copy()
        message_data = result[self.message_field]
        
        # 调用多模态模型
        response = self._invoke_multimodal_model(message_data)
        
        # 将结果存储在JSON中
        result[self.response_field] = response
        return result
    
    def _invoke_multimodal_model(self, message_data: str) -> str:
        """
        调用多模态模型的具体实现
        
        Args:
            message_data (str): 包含多模态消息的JSON字符串
            
        Returns:
            str: 模型的响应文本
        """
        try:
            # 解析消息数据
            message = json.loads(message_data) if isinstance(message_data, str) else message_data
            
            # 调用OpenAI兼容接口
            return self._invoke_openai_multimodal(message)
        except Exception as e:
            print(f"Error invoking multimodal model: {e}")
            return f"Error: {str(e)}"
    
    def _invoke_openai_multimodal(self, message: Dict[str, Any]) -> str:
        """
        调用支持OpenAI格式的多模态模型
        
        Args:
            message (dict): OpenAI格式的消息对象，包含role和content字段
            
        Returns:
            str: 模型的响应文本
            
        Raises:
            ImportError: 如果未安装openai包
            Exception: 如果API调用失败
        """
        try:
            import openai
        except ImportError:
            raise ImportError("OpenAI package is not installed. Please install it with 'pip install openai'.")
        
        # 设置API客户端
        client_params = {"api_key": self.api_key}
        # 添加额外的参数，例如base_url
        client_params.update(self.openai_params)
        client = openai.OpenAI(**client_params)
        
        # 构建消息列表
        messages = [message] if isinstance(message, dict) else message
        
        # 调用API
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}") 