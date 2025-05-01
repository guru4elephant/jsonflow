"""
配置工具模块

该模块提供了用于管理配置的工具类。
"""

import os
import json
import sys
from typing import Dict, Any, Optional, Union

class Config:
    """
    配置管理类
    
    用于加载和管理配置信息，支持从默认配置、配置文件和环境变量中获取配置。
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file (str, optional): 配置文件路径
        """
        self.config = {}
        
        # 加载默认配置
        self._load_default_config()
        
        # 加载配置文件
        if config_file:
            self._load_config_file(config_file)
        
        # 加载环境变量
        self._load_env_vars()
    
    def _load_default_config(self) -> None:
        """
        加载默认配置
        """
        self.config = {
            "log_level": "INFO",
            "logging": {
                "show_operator_io": False,  # 是否显示操作符的输入和输出
                "io_indent": 2,  # 显示输入输出时的缩进空格数
                "truncate_length": 1000  # 截断长输入输出的长度，设为None表示不截断
            },
            "model": {
                "default": "gpt-3.5-turbo",
                "timeout": 30,
                "retries": 3
            },
            "executor": {
                "default_workers": None  # None表示使用系统默认值
            }
        }
    
    def _load_config_file(self, config_file: str) -> None:
        """
        从文件加载配置
        
        Args:
            config_file (str): 配置文件路径
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
    
    def _load_env_vars(self) -> None:
        """
        从环境变量加载配置
        
        环境变量的格式为JSONFLOW_[SECTION]_[KEY]，例如JSONFLOW_MODEL_DEFAULT
        """
        for key, value in os.environ.items():
            if key.startswith("JSONFLOW_"):
                parts = key[9:].lower().split('_')
                self._set_config_by_path(parts, value)
    
    def _set_config_by_path(self, path: list, value: str) -> None:
        """
        根据路径设置配置值
        
        Args:
            path (list): 配置路径，如['model', 'default']
            value (str): 配置值
        """
        config = self.config
        for part in path[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        # 尝试转换值类型
        last_key = path[-1]
        try:
            # 尝试转换为整数
            int_value = int(value)
            config[last_key] = int_value
        except ValueError:
            try:
                # 尝试转换为浮点数
                float_value = float(value)
                config[last_key] = float_value
            except ValueError:
                # 尝试转换为布尔值
                if value.lower() in ('true', 'yes', '1'):
                    config[last_key] = True
                elif value.lower() in ('false', 'no', '0'):
                    config[last_key] = False
                else:
                    # 保持为字符串
                    config[last_key] = value
    
    def _merge_config(self, new_config: Dict[str, Any], base_config: Optional[Dict[str, Any]] = None, path: Optional[list] = None) -> None:
        """
        递归合并配置
        
        Args:
            new_config (dict): 新配置
            base_config (dict, optional): 基础配置，如果为None则使用self.config
            path (list, optional): 当前路径，用于记录合并位置
        """
        if base_config is None:
            base_config = self.config
        
        path = path or []
        
        for key, value in new_config.items():
            current_path = path + [key]
            
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(value, base_config[key], current_path)
            else:
                base_config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key (str): 配置键，支持点号分隔的路径，如'model.default'
            default (Any, optional): 默认值，当配置不存在时返回
            
        Returns:
            Any: 配置值或默认值
        """
        parts = key.split('.')
        config = self.config
        
        for part in parts:
            if part not in config:
                return default
            config = config[part]
        
        return config
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key (str): 配置键，支持点号分隔的路径，如'model.default'
            value (Any): 配置值
        """
        parts = key.split('.')
        config = self.config
        
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典
        
        Returns:
            dict: 配置字典
        """
        return self.config.copy()
    
    def save(self, config_file: str) -> None:
        """
        保存配置到文件
        
        Args:
            config_file (str): 配置文件路径
        """
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2) 