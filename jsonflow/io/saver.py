"""
JSON保存器模块

该模块定义了JsonSaver类，用于将JSON数据保存到文件或标准输出。
"""

import json
import sys
from typing import List, Dict, Any, Optional, Union, TextIO

class JsonSaver:
    """
    将JSON数据保存到文件或标准输出
    
    支持将JSON数据保存到文件或标准输出，支持一次保存单个数据或批量保存。
    """
    
    def __init__(self, destination: Optional[str] = None):
        """
        初始化JsonSaver
        
        Args:
            destination (str, optional): 目标位置，文件路径或None表示输出到stdout
        """
        self.destination = destination
        self._file = None
    
    def __enter__(self) -> 'JsonSaver':
        """
        上下文管理器入口
        
        Returns:
            JsonSaver: self
        """
        if self.destination is not None:
            self._file = open(self.destination, 'w', encoding='utf-8')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        上下文管理器出口
        
        关闭打开的文件（如果有）。
        """
        if self._file is not None:
            self._file.close()
            self._file = None
    
    def write(self, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        写入JSON数据，支持单个JSON对象或JSON列表
        
        Args:
            json_data (dict or list): 要写入的JSON数据，可以是单个对象或列表
        """
        if isinstance(json_data, list):
            for item in json_data:
                self.write_item(item)
        else:
            self.write_item(json_data)
    
    def write_item(self, json_data: Dict[str, Any]) -> None:
        """
        写入单个JSON数据
        
        Args:
            json_data (dict): 要写入的单个JSON数据
        """
        json_str = json.dumps(json_data, ensure_ascii=False)
        if self.destination is None:
            # 输出到标准输出
            print(json_str)
        else:
            # 输出到文件
            if self._file is None:
                with open(self.destination, 'a', encoding='utf-8') as f:
                    f.write(json_str + '\n')
            else:
                self._file.write(json_str + '\n')
                self._file.flush()
    
    def write_all(self, json_data_list: List[Union[Dict[str, Any], List[Dict[str, Any]]]]) -> None:
        """
        批量写入JSON数据
        
        Args:
            json_data_list (list): 要写入的JSON数据列表，每个元素可以是单个对象或列表
        """
        with self:
            for data in json_data_list:
                self.write(data)
    
    @classmethod
    def to_file(cls, file_path: str, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        将JSON数据保存到文件
        
        Args:
            file_path (str): 文件路径
            json_data (dict or list): 要保存的JSON数据，可以是单个dict或dict列表
        """
        saver = cls(file_path)
            saver.write(json_data)
    
    @classmethod
    def to_stdout(cls, json_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        """
        将JSON数据输出到标准输出
        
        Args:
            json_data (dict or list): 要输出的JSON数据，可以是单个dict或dict列表
        """
        saver = cls(None)
            saver.write(json_data)
    
    @staticmethod
    def to_json_string(json_data: Dict[str, Any], pretty: bool = False) -> str:
        """
        将JSON数据转换为字符串
        
        Args:
            json_data (dict): 要转换的JSON数据
            pretty (bool, optional): 是否美化输出，默认为False
            
        Returns:
            str: JSON字符串
        """
        if pretty:
            return json.dumps(json_data, ensure_ascii=False, indent=2)
        return json.dumps(json_data, ensure_ascii=False) 