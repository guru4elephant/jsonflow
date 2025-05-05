"""
管道模块

该模块定义了Pipeline类，用于按顺序执行多个操作符。
"""

class Pipeline:
    """
    操作符的容器，负责按顺序执行操作符
    
    Pipeline类封装了一系列操作符，并按顺序执行它们。
    """
    
    def __init__(self, operators=None, passthrough_fields=None):
        """
        初始化Pipeline
        
        Args:
            operators (list, optional): 操作符列表，如果不提供则创建空列表
            passthrough_fields (list, optional): 需要透传的字段列表
        """
        self.operators = operators or []
        self.passthrough_fields = passthrough_fields or []
    
    def add(self, operator):
        """
        添加操作符到管道中
        
        Args:
            operator: 要添加的操作符，必须实现process方法
            
        Returns:
            Pipeline: 返回self以支持链式调用
        """
        self.operators.append(operator)
        return self
    
    def set_passthrough_fields(self, fields):
        """
        设置需要透传的字段列表
        
        Args:
            fields (list or str): 字段名列表或单个字段名
        
        Returns:
            Pipeline: 返回self以支持链式调用
        """
        if isinstance(fields, str):
            self.passthrough_fields = [fields]
        else:
            self.passthrough_fields = list(fields)
        return self
    
    def process(self, json_data):
        """
        按顺序执行所有操作符，并处理透传字段
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 所有操作符处理后的JSON数据
        """
        # 提取需要透传的字段值
        passthrough_values = {}
        for field in self.passthrough_fields:
            if field in json_data:
                passthrough_values[field] = json_data[field]
        
        # 按顺序执行所有操作符
        result = json_data
        for op in self.operators:
            result = op.process(result)
        
        # 恢复透传字段
        for field, value in passthrough_values.items():
            result[field] = value
        
        return result
    
    def __iter__(self):
        """
        迭代器方法，便于遍历所有操作符
        
        Returns:
            iterator: 操作符迭代器
        """
        return iter(self.operators)
    
    def __len__(self):
        """
        返回管道中操作符的数量
        
        Returns:
            int: 操作符数量
        """
        return len(self.operators) 