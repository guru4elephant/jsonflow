"""
系统字段管理模块

该模块提供系统字段的创建和管理功能，如ID、时间戳等。
"""

import uuid
import time
import datetime

class SystemField:
    """系统字段管理类，用于创建和管理系统字段"""
    
    @staticmethod
    def add_id(json_data, field_name='id', override=False):
        """
        添加UUID字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str, optional): 字段名，默认为'id'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了ID字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = str(uuid.uuid4())
        return result
    
    @staticmethod
    def add_timestamp(json_data, field_name='timestamp', override=False):
        """
        添加时间戳字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str, optional): 字段名，默认为'timestamp'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了时间戳字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = int(time.time())
        return result
    
    @staticmethod
    def add_datetime(json_data, field_name='datetime', format='%Y-%m-%d %H:%M:%S', override=False):
        """
        添加日期时间字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str, optional): 字段名，默认为'datetime'
            format (str, optional): 日期时间格式，默认为'%Y-%m-%d %H:%M:%S'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了日期时间字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = datetime.datetime.now().strftime(format)
        return result
    
    @staticmethod
    def add_custom_field(json_data, field_name, value, override=False):
        """
        添加自定义字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str): 字段名
            value: 字段值
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了自定义字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = value
        return result
    
    @staticmethod
    def remove_field(json_data, field_name):
        """
        移除字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str): 字段名
            
        Returns:
            dict: 移除了指定字段的JSON数据
        """
        result = json_data.copy()
        if field_name in result:
            del result[field_name]
        return result 