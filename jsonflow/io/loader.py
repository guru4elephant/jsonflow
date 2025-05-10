"""
JSON加载器模块

该模块定义了JsonLoader类，用于从文件或标准输入加载JSON数据。
"""

import json
import sys
from typing import Iterator, List, Dict, Any, Optional, Union, Generator

class JsonLoader:
    """
    从文件或标准输入加载JSON数据
    
    支持从文件或标准输入逐行加载JSON数据，也支持一次性加载所有数据或批量加载。
    """
    
    def __init__(self, source: Optional[str] = None):
        """
        初始化JsonLoader
        
        Args:
            source (str, optional): 数据源，文件路径或None表示从stdin读取
        """
        self.source = source
    
    def load(self) -> List[Dict[str, Any]]:
        """
        加载所有JSON数据到列表
        
        Returns:
            list: JSON数据列表
        """
        return list(self)
    
    def load_batch(self, batch_size: int = 100) -> Generator[List[Dict[str, Any]], None, None]:
        """
        批量加载指定数量的JSON数据
        
        Args:
            batch_size (int): 每批加载的数据量，默认为100
            
        Returns:
            generator: 生成器，每次返回一批JSON数据列表
        
        Yields:
            list: 每批JSON数据列表
        """
        batch = []
        for item in self:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:  # 确保最后一批也能被处理，即使不满batch_size
            yield batch
    
    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """
        迭代器方法，便于逐行加载JSON
        
        Yields:
            dict: 每一行解析后的JSON数据
            
        Raises:
            json.JSONDecodeError: 如果JSON解析失败
        """
        if self.source is None:
            # 从标准输入读取
            for line in sys.stdin:
                if line.strip():
                    yield json.loads(line)
        else:
            # 从文件读取
            with open(self.source, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'JsonLoader':
        """
        从文件创建JsonLoader
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            JsonLoader: JsonLoader实例
        """
        return cls(file_path)
    
    @classmethod
    def from_stdin(cls) -> 'JsonLoader':
        """
        从标准输入创建JsonLoader
        
        Returns:
            JsonLoader: JsonLoader实例
        """
        return cls(None)
    
    @classmethod
    def from_json_string(cls, json_string: str) -> Dict[str, Any]:
        """
        从JSON字符串解析单个JSON对象
        
        Args:
            json_string (str): JSON字符串
            
        Returns:
            dict: 解析后的JSON数据
            
        Raises:
            json.JSONDecodeError: 如果JSON解析失败
        """
        return json.loads(json_string)
    
    @classmethod
    def from_json_strings(cls, json_strings: List[str]) -> List[Dict[str, Any]]:
        """
        从多个JSON字符串解析多个JSON对象
        
        Args:
            json_strings (list): JSON字符串列表
            
        Returns:
            list: 解析后的JSON数据列表
            
        Raises:
            json.JSONDecodeError: 如果任何JSON解析失败
        """
        return [json.loads(s) for s in json_strings if s.strip()] 