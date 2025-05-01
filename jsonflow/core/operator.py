"""
操作符基类模块

该模块定义了所有操作符的基类和接口。
"""

from jsonflow.utils.operator_utils import log_io

class Operator:
    """
    操作符基类，定义处理JSON数据的接口
    
    所有操作符都应该继承这个类，并实现process方法。
    """
    
    def __init__(self, name=None, description=None):
        """
        初始化操作符
        
        Args:
            name (str, optional): 操作符名称，如果不提供则使用类名
            description (str, optional): 操作符描述，如果不提供则使用默认描述
        """
        self.name = name or self.__class__.__name__
        self.description = description or f"{self.name} operator"
    
    @log_io
    def process(self, json_data):
        """
        处理JSON数据的抽象方法，子类需要实现
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    def __call__(self, json_data):
        """
        便捷调用方法，内部调用process
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        return self.process(json_data)


class JsonOperator(Operator):
    """
    JSON操作符基类，专门处理JSON数据转换
    
    这个类封装了处理JSON数据的操作符。
    """
    
    def __init__(self, name=None, description=None):
        """
        初始化JSON操作符
        
        Args:
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(name, description or "JSON data operator")


class ModelOperator(Operator):
    """
    模型操作符基类，专门处理模型调用
    
    这个类封装了调用大语言模型的操作符。
    """
    
    def __init__(self, name=None, description=None, **model_params):
        """
        初始化模型操作符
        
        Args:
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            **model_params: 模型参数
        """
        super().__init__(name, description or "Model operator")
        self.model_params = model_params 