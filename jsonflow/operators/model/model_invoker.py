"""
模型调用操作符模块

该模块定义了ModelInvoker操作符，用于调用大语言模型。
"""

import os
import json
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
        response = self._invoke_model(prompt)
        
        # 将结果存储在JSON中
        result[self.response_field] = response
        return result
    
    def _invoke_model(self, prompt: str) -> str:
        """
        调用模型的具体实现
        
        这个示例方法只是返回一个模拟的响应。在实际应用中，这里会连接到
        适当的API，如OpenAI, Anthropic, HuggingFace等。
        
        Args:
            prompt (str): 发送给模型的提示文本
            
        Returns:
            str: 模型的响应文本
        """
        # 这里是模型调用的示例实现
        # 在实际应用中，会替换为对应模型API的调用
        try:
            if self.model.startswith("gpt"):
                return self._invoke_openai(prompt)
            else:
                # 如果不支持该模型，返回一个默认响应
                return f"Model response to: {prompt[:50]}..."
        except Exception as e:
            # 在实际应用中，可能需要更复杂的错误处理
            print(f"Error invoking model: {e}")
            return f"Error: {str(e)}"
    
    def _invoke_openai(self, prompt: str) -> str:
        """
        调用OpenAI模型
        
        注意：这是一个示例方法，在实际应用中需要安装openai包并正确配置API密钥。
        
        Args:
            prompt (str): 发送给模型的提示文本
            
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
        
        # 设置API密钥
        client = openai.OpenAI(api_key=self.api_key)
        
        # 构建消息
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        
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
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    @classmethod
    def with_system_prompt(cls, model: str, system_prompt: str, **kwargs) -> 'ModelInvoker':
        """
        创建一个带有系统提示的ModelInvoker
        
        Args:
            model (str): 模型名称
            system_prompt (str): 系统提示
            **kwargs: 其他参数
            
        Returns:
            ModelInvoker: 新的ModelInvoker实例
        """
        return cls(model=model, system_prompt=system_prompt, **kwargs) 