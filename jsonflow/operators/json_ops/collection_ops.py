#!/usr/bin/env python
# coding=utf-8

"""
Collection operators for JSONFlow.
These operators handle transformations between single JSON objects and lists of JSON objects.
"""

from jsonflow.core import JsonOperator

class JsonSplitter(JsonOperator):
    """
    将单个JSON拆分为多个JSON的操作符
    """
    
    def __init__(self, split_field, output_key_map=None, keep_original=False, name=None):
        """
        初始化JsonSplitter
        
        Args:
            split_field (str): 包含要拆分的列表的字段名
            output_key_map (dict, optional): 输出字段映射，用于从原始字段映射到拆分后的新对象
            keep_original (bool, optional): 是否在拆分后的对象中保留其他原始字段
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Split JSON by {split_field} field")
        self.split_field = split_field
        self.output_key_map = output_key_map or {}
        self.keep_original = keep_original
    
    def process_item(self, json_data):
        """
        处理单个JSON数据，按指定字段拆分成多个JSON对象
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            list: 拆分后的JSON对象列表
        """
        if self.split_field not in json_data or not isinstance(json_data[self.split_field], list):
            # 如果没有要拆分的字段或该字段不是列表，则直接返回原对象
            return [json_data]
        
        split_values = json_data[self.split_field]
        results = []
        
        for value in split_values:
            # 创建新对象
            if self.keep_original:
                # 保留原始字段
                new_obj = json_data.copy()
                # 移除要拆分的字段，避免再次拆分
                new_obj.pop(self.split_field, None)
            else:
                # 不保留原始字段，创建空对象
                new_obj = {}
            
            # 设置拆分后的值
            if self.output_key_map:
                # 使用字段映射
                for orig_key, new_key in self.output_key_map.items():
                    if orig_key == self.split_field:
                        new_obj[new_key] = value
                    elif orig_key in json_data:
                        new_obj[new_key] = json_data[orig_key]
            else:
                # 没有字段映射，直接使用拆分字段
                new_obj[self.split_field] = value
            
            results.append(new_obj)
        
        return results


class JsonAggregator(JsonOperator):
    """
    将多个JSON合并为单个JSON的操作符
    通常与Pipeline的nested模式一起使用，或作为独立操作符处理已经是列表的输入
    """
    
    def __init__(self, aggregate_field=None, strategy='list', condition=None, name=None):
        """
        初始化JsonAggregator
        
        Args:
            aggregate_field (str, optional): 合并后的字段名，合并结果将存储在此字段，若为None则整个对象为合并结果
            strategy (str, optional): 合并策略，'list'表示将所有对象合并为列表，'merge'表示合并对象的字段
            condition (callable, optional): 自定义条件函数，决定哪些对象参与合并
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Aggregate JSON objects to {aggregate_field or 'one object'}", supports_batch=True)
        self.aggregate_field = aggregate_field
        self.strategy = strategy
        self.condition = condition
    
    def process_item(self, json_data):
        """
        处理单个JSON数据，基本上此操作符的主要功能是在批处理模式下，因此这个方法只是简单返回输入
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 原JSON数据
        """
        return json_data
    
    def process_batch(self, json_data_list):
        """
        处理JSON列表，将多个对象合并为一个
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            dict: 合并后的单个JSON对象
        """
        # 过滤要合并的对象
        if self.condition:
            items_to_aggregate = [item for item in json_data_list if self.condition(item)]
        else:
            items_to_aggregate = json_data_list
        
        if not items_to_aggregate:
            # 没有符合条件的对象
            return {}
        
        if self.strategy == 'list':
            # 列表合并策略
            if self.aggregate_field:
                # 将列表存储在指定字段
                return {self.aggregate_field: items_to_aggregate}
            else:
                # 直接返回列表
                return items_to_aggregate
        elif self.strategy == 'merge':
            # 对象合并策略
            result = {}
            for item in items_to_aggregate:
                result.update(item)
            
            if self.aggregate_field:
                # 将合并结果存储在指定字段
                return {self.aggregate_field: result}
            else:
                # 直接返回合并结果
                return result
        else:
            raise ValueError(f"Unknown aggregation strategy: {self.strategy}") 