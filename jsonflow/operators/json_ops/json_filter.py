"""
JSON过滤操作符模块

该模块定义了JsonFilter操作符，用于根据条件过滤JSON数据。
"""

from typing import Dict, Any, List, Optional, Union, Callable

from jsonflow.core import JsonOperator

class JsonFilter(JsonOperator):
    """
    JSON过滤操作符
    
    该操作符可以根据条件过滤JSON数据，保留或删除特定字段。
    """
    
    def __init__(self, 
                 include_fields: Optional[List[str]] = None,
                 exclude_fields: Optional[List[str]] = None,
                 filter_func: Optional[Callable[[Dict[str, Any]], bool]] = None,
                 name: Optional[str] = None, 
                 description: Optional[str] = None):
        """
        初始化JsonFilter
        
        Args:
            include_fields (list, optional): 要保留的字段列表，为None时保留所有字段
            exclude_fields (list, optional): 要排除的字段列表，为None时不排除任何字段
            filter_func (callable, optional): 自定义的过滤函数，接收一个dict，返回一个布尔值
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name,
            description or "Filters JSON data"
        )
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields
        self.filter_func = filter_func
        
        if include_fields is not None and exclude_fields is not None:
            # 检查是否有冲突的字段
            conflicts = set(include_fields) & set(exclude_fields)
            if conflicts:
                raise ValueError(f"Conflict in include_fields and exclude_fields: {conflicts}")
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，根据条件过滤
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 过滤后的JSON数据
        """
        if not json_data:
            return json_data
        
        # 如果提供了自定义过滤函数，先检查整个JSON是否符合条件
        if self.filter_func is not None and not self.filter_func(json_data):
            return {}
        
        result = json_data.copy()
        
        # 应用字段过滤
        if self.include_fields is not None:
            # 只保留指定字段
            filtered_result = {}
            for field in self.include_fields:
                if field in result:
                    filtered_result[field] = result[field]
            result = filtered_result
        
        if self.exclude_fields is not None:
            # 删除指定字段
            for field in self.exclude_fields:
                if field in result:
                    del result[field]
        
        return result
    
    @classmethod
    def include_only(cls, fields: List[str], name: Optional[str] = None) -> 'JsonFilter':
        """
        创建一个只包含指定字段的过滤器
        
        Args:
            fields (list): 要保留的字段列表
            name (str, optional): 操作符名称
            
        Returns:
            JsonFilter: 新的JsonFilter实例
        """
        return cls(include_fields=fields, name=name or "IncludeOnlyFilter")
    
    @classmethod
    def exclude(cls, fields: List[str], name: Optional[str] = None) -> 'JsonFilter':
        """
        创建一个排除指定字段的过滤器
        
        Args:
            fields (list): 要排除的字段列表
            name (str, optional): 操作符名称
            
        Returns:
            JsonFilter: 新的JsonFilter实例
        """
        return cls(exclude_fields=fields, name=name or "ExcludeFilter")
    
    @classmethod
    def with_predicate(cls, predicate: Callable[[Dict[str, Any]], bool], name: Optional[str] = None) -> 'JsonFilter':
        """
        创建一个使用自定义谓词函数的过滤器
        
        Args:
            predicate (callable): 谓词函数，接收一个dict，返回一个布尔值
            name (str, optional): 操作符名称
            
        Returns:
            JsonFilter: 新的JsonFilter实例
        """
        return cls(filter_func=predicate, name=name or "PredicateFilter") 