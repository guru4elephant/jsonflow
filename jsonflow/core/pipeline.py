"""
管道模块

该模块定义了Pipeline类，用于按顺序执行多个操作符。
"""

class Pipeline:
    """
    操作符的容器，负责按顺序执行操作符
    
    Pipeline类封装了一系列操作符，并按顺序执行它们。
    """
    
    def __init__(self, operators=None):
        """
        初始化Pipeline
        
        Args:
            operators (list, optional): 操作符列表，如果不提供则创建空列表
        """
        self.operators = operators or []
    
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
    
    def process(self, json_data):
        """
        按顺序执行所有操作符
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 所有操作符处理后的JSON数据
        """
        result = json_data
        for op in self.operators:
            result = op.process(result)
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