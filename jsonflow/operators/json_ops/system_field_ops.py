"""
系统字段操作符模块

该模块提供添加和管理系统字段的操作符。
"""

from jsonflow.core import JsonOperator
from jsonflow.utils.system_field import SystemField

class IdAdder(JsonOperator):
    """添加ID系统字段的操作符"""
    
    def __init__(self, field_name='id', override=False, name=None):
        """
        初始化IdAdder
        
        Args:
            field_name (str, optional): 字段名，默认为'id'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加ID字段"""
        return SystemField.add_id(json_data, self.field_name, self.override)


class TimestampAdder(JsonOperator):
    """添加时间戳系统字段的操作符"""
    
    def __init__(self, field_name='timestamp', override=False, name=None):
        """
        初始化TimestampAdder
        
        Args:
            field_name (str, optional): 字段名，默认为'timestamp'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加时间戳字段"""
        return SystemField.add_timestamp(json_data, self.field_name, self.override)


class DateTimeAdder(JsonOperator):
    """添加日期时间系统字段的操作符"""
    
    def __init__(self, field_name='datetime', format='%Y-%m-%d %H:%M:%S', override=False, name=None):
        """
        初始化DateTimeAdder
        
        Args:
            field_name (str, optional): 字段名，默认为'datetime'
            format (str, optional): 日期时间格式，默认为'%Y-%m-%d %H:%M:%S'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.format = format
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加日期时间字段"""
        return SystemField.add_datetime(json_data, self.field_name, self.format, self.override)


class CustomFieldAdder(JsonOperator):
    """添加自定义系统字段的操作符"""
    
    def __init__(self, field_name, value, override=False, name=None):
        """
        初始化CustomFieldAdder
        
        Args:
            field_name (str): 字段名
            value: 字段值
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.value = value
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加自定义字段"""
        return SystemField.add_custom_field(json_data, self.field_name, self.value, self.override)


class FieldRemover(JsonOperator):
    """移除字段的操作符"""
    
    def __init__(self, field_name, name=None):
        """
        初始化FieldRemover
        
        Args:
            field_name (str): 字段名
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Remove {field_name} field operator")
        self.field_name = field_name
    
    def process(self, json_data):
        """处理JSON数据，移除指定字段"""
        return SystemField.remove_field(json_data, self.field_name) 