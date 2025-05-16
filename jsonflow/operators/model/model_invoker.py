"""
模型调用操作符模块

该模块定义了ModelInvoker操作符，用于调用大语言模型。
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional, Union, Callable

from jsonflow.core import ModelOperator

class ModelInvoker(ModelOperator):
    """
    大语言模型调用操作符
    
    该操作符用于调用大语言模型，处理JSON数据中的文本，并将结果存储在JSON中。
    """
    
    def __init__(self, 
                 model: str,
                 prompt_field: str = "prompt",
                 response_field: str = "response",
                 system_prompt: Optional[str] = None,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 max_tokens: Optional[int] = None,
                 temperature: float = 0.7,
                 name: Optional[str] = None, 
                 description: Optional[str] = None,
                 **model_params):
        """
        初始化ModelInvoker
        
        Args:
            model (str): 模型名称
            prompt_field (str): 输入字段名，默认为"prompt"
            response_field (str): 输出字段名，默认为"response"
            system_prompt (str, optional): 系统提示
            api_key (str, optional): API密钥，如果不提供则从环境变量中获取
            base_url (str, optional): 模型API的基础URL，用于自定义端点
            max_tokens (int, optional): 生成的最大令牌数
            temperature (float): 采样温度，值越高结果越多样，值越低结果越确定
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            **model_params: 其他模型参数
        """
        super().__init__(
            name,
            description or f"Invokes {model} model",
            **model_params
        )
        self.model = model
        self.prompt_field = prompt_field
        self.response_field = response_field
        self.system_prompt = system_prompt
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or "https://api.openai.com/v1/chat/completions"
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，调用模型
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data or self.prompt_field not in json_data:
            return json_data
        
        result = json_data.copy()
        prompt = result[self.prompt_field]
        
        # 调用模型
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.call_llm(messages)
        
        # 将结果存储在JSON中
        result[self.response_field] = response
        return result
    
    def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        使用requests库调用大模型API
        
        此方法接收消息列表格式的输入，使用requests直接调用大模型API，
        支持自定义端点URL。
        
        Args:
            messages (List[Dict[str, str]]): 消息列表，格式为[{"role": "...", "content": "..."}]
            
        Returns:
            str: 模型的响应文本
            
        Raises:
            Exception: 如果API调用失败
        """
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }

        data = {
            'model': self.model,
            'messages': messages,
            'temperature': self.temperature
        }
        
        if self.max_tokens:
            data['max_tokens'] = self.max_tokens
            
        # 添加其他模型参数
        if hasattr(self, 'model_params') and self.model_params:
            data.update(self.model_params)
            
        try:
            print(f"Calling LLM API at: {self.base_url}")
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()  # 检查响应状态码
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                raise Exception(f"Unexpected API response format: {result}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"API call failed: {str(e)}"
            if self.base_url != "https://api.openai.com/v1/chat/completions":
                error_msg = f"Custom API endpoint call failed: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)