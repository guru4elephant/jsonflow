"""
操作符工具模块

该模块提供了操作符相关的工具函数，如日志装饰器等。
"""

import json
import functools
from typing import Any, Callable, Dict, Optional

from jsonflow.utils.logger import get_logger
from jsonflow.utils.config import Config

# 全局配置实例
_config = Config()
# 全局日志实例
_logger = get_logger("operator_utils")

def log_io(func: Callable) -> Callable:
    """
    装饰器：记录操作符的输入和输出
    
    根据全局配置决定是否打印操作符的输入和输出信息。
    
    Args:
        func: 要装饰的函数，通常是操作符的process方法
        
    Returns:
        Callable: 装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        # 检查全局配置是否启用了操作符IO日志
        show_io = _config.get("logging.show_operator_io", False)
        
        if show_io:
            indent = _config.get("logging.io_indent", 2)
            truncate_length = _config.get("logging.truncate_length", None)
            
            # 准备输入的JSON字符串
            input_json = json.dumps(json_data, ensure_ascii=False, indent=indent)
            if truncate_length and len(input_json) > truncate_length:
                input_json = input_json[:truncate_length] + "... (truncated)"
            
            _logger.info(f"\n[{self.name}] 输入:\n{input_json}")
        
        # 调用原始函数
        result = func(self, json_data)
        
        if show_io:
            # 准备输出的JSON字符串
            output_json = json.dumps(result, ensure_ascii=False, indent=indent)
            if truncate_length and len(output_json) > truncate_length:
                output_json = output_json[:truncate_length] + "... (truncated)"
            
            _logger.info(f"[{self.name}] 输出:\n{output_json}")
        
        return result
    
    return wrapper

def enable_operator_io_logging(enable: bool = True) -> None:
    """
    启用或禁用操作符输入输出日志
    
    Args:
        enable (bool): 是否启用日志，默认为True
    """
    _config.set("logging.show_operator_io", enable)
    _logger.info(f"操作符输入输出日志已{'启用' if enable else '禁用'}")

def set_io_log_indent(indent: int) -> None:
    """
    设置输入输出日志的缩进空格数
    
    Args:
        indent (int): 缩进空格数
    """
    _config.set("logging.io_indent", indent)

def set_io_log_truncate_length(length: Optional[int]) -> None:
    """
    设置输入输出日志的截断长度
    
    Args:
        length (int or None): 截断长度，None表示不截断
    """
    _config.set("logging.truncate_length", length) 