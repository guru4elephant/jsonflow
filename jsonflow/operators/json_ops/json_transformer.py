"""
JSON转换操作符模块

该模块定义了JsonTransformer操作符，用于转换JSON数据的结构和内容。
"""

from typing import Dict, Any, List, Optional, Union, Callable, Tuple

from jsonflow.core import JsonOperator

class JsonTransformer(JsonOperator):
    """
    JSON转换操作符
    
    该操作符可以转换JSON数据的结构和内容，如重命名字段、添加新字段、修改字段值等。
    """
    
    def __init__(self, 
                 transforms: Optional[Dict[str, Union[str, Callable]]] = None,
                 rename_fields: Optional[Dict[str, str]] = None,
                 add_fields: Optional[Dict[str, Any]] = None,
                 transform_func: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
                 name: Optional[str] = None, 
                 description: Optional[str] = None):
        """
        初始化JsonTransformer
        
        Args:
            transforms (dict, optional): 字段转换映射，键为字段名，值为转换函数或新字段名
            rename_fields (dict, optional): 字段重命名映射，键为原字段名，值为新字段名
            add_fields (dict, optional): 要添加的字段，键为字段名，值为字段值
            transform_func (callable, optional): 自定义的转换函数，接收一个dict，返回一个dict
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name,
            description or "Transforms JSON data"
        )
        self.transforms = transforms or {}
        self.rename_fields = rename_fields or {}
        self.add_fields = add_fields or {}
        self.transform_func = transform_func
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，应用转换
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 转换后的JSON数据
        """
        if not json_data:
            return json_data
        
        # 如果提供了自定义转换函数，先应用它
        if self.transform_func is not None:
            result = self.transform_func(json_data)
        else:
            result = json_data.copy()
        
        # 应用字段转换
        self._apply_transforms(result)
        
        # 应用字段重命名
        self._apply_rename(result)
        
        # 应用字段添加
        self._apply_add_fields(result)
        
        return result
    
    def _apply_transforms(self, data: Dict[str, Any]) -> None:
        """
        应用字段转换
        
        Args:
            data (dict): 要转换的数据
        """
        for field, transform in self.transforms.items():
            if field in data:
                if callable(transform):
                    data[field] = transform(data[field])
                elif isinstance(transform, str):
                    # 转换为新字段名
                    data[transform] = data.pop(field)
    
    def _apply_rename(self, data: Dict[str, Any]) -> None:
        """
        应用字段重命名
        
        Args:
            data (dict): 要重命名的数据
        """
        for old_name, new_name in self.rename_fields.items():
            if old_name in data:
                data[new_name] = data.pop(old_name)
    
    def _apply_add_fields(self, data: Dict[str, Any]) -> None:
        """
        应用字段添加
        
        Args:
            data (dict): 要添加字段的数据
        """
        for field, value in self.add_fields.items():
            # 如果值是可调用的，调用它并使用返回值
            if callable(value):
                data[field] = value(data)
            else:
                data[field] = value
    
    @classmethod
    def with_function(cls, transform_func: Callable[[Dict[str, Any]], Dict[str, Any]], name: Optional[str] = None) -> 'JsonTransformer':
        """
        创建一个使用自定义函数的转换器
        
        Args:
            transform_func (callable): 转换函数，接收一个dict，返回一个dict
            name (str, optional): 操作符名称
            
        Returns:
            JsonTransformer: 新的JsonTransformer实例
        """
        return cls(transform_func=transform_func, name=name or "FunctionTransformer")
    
    @classmethod
    def rename(cls, rename_mapping: Dict[str, str], name: Optional[str] = None) -> 'JsonTransformer':
        """
        创建一个字段重命名转换器
        
        Args:
            rename_mapping (dict): 重命名映射，键为原字段名，值为新字段名
            name (str, optional): 操作符名称
            
        Returns:
            JsonTransformer: 新的JsonTransformer实例
        """
        return cls(rename_fields=rename_mapping, name=name or "FieldRenamer")
    
    @classmethod
    def add(cls, add_mapping: Dict[str, Any], name: Optional[str] = None) -> 'JsonTransformer':
        """
        创建一个字段添加转换器
        
        Args:
            add_mapping (dict): 添加映射，键为字段名，值为字段值
            name (str, optional): 操作符名称
            
        Returns:
            JsonTransformer: 新的JsonTransformer实例
        """
        return cls(add_fields=add_mapping, name=name or "FieldAdder") 