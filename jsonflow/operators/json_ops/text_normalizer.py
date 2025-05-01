"""
文本规范化操作符模块

该模块定义了TextNormalizer操作符，用于规范化JSON数据中的文本字段。
"""

import re
from typing import Dict, Any, List, Optional, Union, Callable

from jsonflow.core import JsonOperator

class TextNormalizer(JsonOperator):
    """
    文本规范化操作符
    
    该操作符可以对JSON数据中的文本字段进行规范化处理，如去除多余的空格、统一大小写等。
    """
    
    def __init__(self, 
                 text_fields: Optional[List[str]] = None, 
                 normalize_func: Optional[Callable[[str], str]] = None,
                 strip: bool = True,
                 lower_case: bool = False,
                 upper_case: bool = False,
                 remove_extra_spaces: bool = True,
                 name: Optional[str] = None, 
                 description: Optional[str] = None):
        """
        初始化TextNormalizer
        
        Args:
            text_fields (list, optional): 要规范化的文本字段列表，为None时处理所有字符串字段
            normalize_func (callable, optional): 自定义的文本规范化函数，接收一个字符串，返回一个字符串
            strip (bool): 是否去除字符串两端的空白字符，默认为True
            lower_case (bool): 是否转换为小写，默认为False
            upper_case (bool): 是否转换为大写，默认为False
            remove_extra_spaces (bool): 是否移除多余的空格，默认为True
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name,
            description or "Normalizes text fields in JSON data"
        )
        self.text_fields = text_fields
        self.normalize_func = normalize_func
        self.strip = strip
        self.lower_case = lower_case
        self.upper_case = upper_case
        self.remove_extra_spaces = remove_extra_spaces
        
        if self.lower_case and self.upper_case:
            raise ValueError("lower_case and upper_case cannot both be True")
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，规范化文本字段
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data:
            return json_data
        
        result = json_data.copy()
        self._normalize_fields(result)
        return result
    
    def _normalize_fields(self, data: Union[Dict[str, Any], List[Any]], path: str = "") -> None:
        """
        递归处理字段
        
        Args:
            data (dict or list): 要处理的数据
            path (str): 当前字段的路径，用于检查是否在text_fields中
        """
        if isinstance(data, dict):
            for key, value in list(data.items()):
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    if self.text_fields is None or current_path in self.text_fields:
                        data[key] = self._normalize_text(value)
                elif isinstance(value, (dict, list)):
                    self._normalize_fields(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    if self.text_fields is None:
                        data[i] = self._normalize_text(item)
                elif isinstance(item, (dict, list)):
                    self._normalize_fields(item, path)
    
    def _normalize_text(self, text: str) -> str:
        """
        执行文本规范化
        
        Args:
            text (str): 要规范化的文本
            
        Returns:
            str: 规范化后的文本
        """
        if self.normalize_func is not None:
            return self.normalize_func(text)
        
        # 应用内置的规范化规则
        result = text
        
        if self.strip:
            result = result.strip()
        
        if self.lower_case:
            result = result.lower()
        
        if self.upper_case:
            result = result.upper()
        
        if self.remove_extra_spaces:
            result = re.sub(r'\s+', ' ', result)
        
        return result 