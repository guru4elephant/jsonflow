#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSON结构提取器操作符

此操作符分析JSON数据，提取其键的结构信息，包括数据类型和嵌套关系。
"""

from typing import Dict, Any, Set, List, Union

from jsonflow.core import JsonOperator


class JsonStructureExtractor(JsonOperator):
    """
    JSON结构提取器操作符
    
    分析JSON数据，提取键的结构信息，包括数据类型和嵌套关系。
    """
    
    def __init__(
        self, 
        extract_types: bool = True, 
        extract_nested: bool = True,
        output_field: str = "structure", 
        include_original: bool = True,
        name: str = None, 
        description: str = None
    ):
        """
        初始化JsonStructureExtractor
        
        Args:
            extract_types: 是否提取字段的数据类型
            extract_nested: 是否提取嵌套字段
            output_field: 输出结构信息的字段名
            include_original: 是否在输出中包含原始JSON数据
            name: 操作符名称
            description: 操作符描述
        """
        super().__init__(
            name or "JsonStructureExtractor",
            description or "Extracts structure information from JSON data"
        )
        self.extract_types = extract_types
        self.extract_nested = extract_nested
        self.output_field = output_field
        self.include_original = include_original
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，提取其结构信息
        
        Args:
            json_data: 输入的JSON数据
            
        Returns:
            包含结构信息的JSON数据
        """
        if not json_data:
            return {self.output_field: {}} if not self.include_original else {self.output_field: {}, **json_data}
        
        # 提取结构信息
        structure = self._extract_structure(json_data)
        
        # 创建输出
        if self.include_original:
            result = json_data.copy()
            result[self.output_field] = structure
        else:
            result = {self.output_field: structure}
        
        return result
    
    def _extract_structure(self, json_data: Dict[str, Any], prefix: str = "") -> Dict[str, Dict[str, Any]]:
        """
        递归提取JSON数据的结构信息
        
        Args:
            json_data: 要分析的JSON数据
            prefix: 当前键的前缀路径
            
        Returns:
            结构信息字典
        """
        structure = {}
        
        if not isinstance(json_data, dict):
            return structure
        
        for key, value in json_data.items():
            current_path = f"{prefix}.{key}" if prefix else key
            
            # 创建当前键的结构信息
            key_info = {
                "path": current_path
            }
            
            # 提取类型信息
            if self.extract_types:
                key_info["types"] = self._get_value_types(value)
            
            # 添加到结构信息
            structure[current_path] = key_info
            
            # 处理嵌套结构
            if self.extract_nested:
                if isinstance(value, dict):
                    # 递归处理嵌套字典
                    nested_structure = self._extract_structure(value, current_path)
                    structure.update(nested_structure)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    # 仅分析数组中的第一个字典对象(作为样本)
                    sample_dict = value[0]
                    array_path = f"{current_path}[*]"
                    nested_structure = self._extract_structure(sample_dict, array_path)
                    structure.update(nested_structure)
        
        return structure
    
    def _get_value_types(self, value: Any) -> Set[str]:
        """
        获取值的数据类型
        
        Args:
            value: 要分析的值
            
        Returns:
            类型名称的集合
        """
        types = set()
        
        if value is None:
            types.add("null")
        elif isinstance(value, bool):
            types.add("boolean")
        elif isinstance(value, int):
            types.add("integer")
        elif isinstance(value, float):
            types.add("number")
        elif isinstance(value, str):
            types.add("string")
        elif isinstance(value, list):
            types.add("array")
            
            # 分析数组元素类型(取样)
            if value:
                for item in value[:5]:  # 只取前5个元素作为样本
                    if isinstance(item, dict):
                        types.add("object_array")
                        break
                    elif isinstance(item, list):
                        types.add("array_array")
                    else:
                        item_type = type(item).__name__
                        types.add(f"{item_type}_array")
        elif isinstance(value, dict):
            types.add("object")
        else:
            types.add(type(value).__name__)
        
        return types 