"""
日志工具模块

该模块提供了用于记录日志的工具函数。
"""

import logging
import sys
from typing import Optional, Union, Dict, Any

def get_logger(name: str, level: Optional[Union[int, str]] = None) -> logging.Logger:
    """
    获取配置好的logger实例
    
    Args:
        name (str): logger名称
        level (int or str, optional): 日志级别，可以是logging模块的常量（如logging.INFO）
                                   或者字符串（如'INFO'），默认为INFO
    
    Returns:
        logging.Logger: 配置好的logger实例
    """
    # 获取logger实例
    logger = logging.getLogger(name)
    
    # 设置日志级别
    if level is None:
        level = logging.INFO
    elif isinstance(level, str):
        level = getattr(logging, level.upper())
    
    logger.setLevel(level)
    
    # 如果logger没有处理器，添加一个控制台处理器
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def configure_logging(level: Optional[Union[int, str]] = None, 
                     format_str: Optional[str] = None,
                     log_file: Optional[str] = None) -> None:
    """
    配置全局的日志设置
    
    Args:
        level (int or str, optional): 日志级别，可以是logging模块的常量（如logging.INFO）
                                   或者字符串（如'INFO'），默认为INFO
        format_str (str, optional): 日志格式字符串，默认为'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_file (str, optional): 日志文件路径，如果提供则同时输出到文件
    """
    # 设置日志级别
    if level is None:
        level = logging.INFO
    elif isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # 设置日志格式
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_str)
    
    # 配置根logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler) 