"""
操作符基类模块

该模块定义了所有操作符的基类和接口。
"""

from jsonflow.utils.operator_utils import log_io

class Operator:
    """
    操作符基类，定义处理JSON数据的接口
    
    所有操作符都应该继承这个类，并实现process_item方法或process_batch方法。
    """
    
    def __init__(self, name=None, description=None, supports_batch=False):
        """
        初始化操作符
        
        Args:
            name (str, optional): 操作符名称，如果不提供则使用类名
            description (str, optional): 操作符描述，如果不提供则使用默认描述
            supports_batch (bool, optional): 是否支持批处理JSON列表，默认False
        """
        self.name = name or self.__class__.__name__
        self.description = description or f"{self.name} operator"
        self.supports_batch = supports_batch
    
    @log_io
    def process(self, json_data):
        """
        处理JSON数据的方法，支持单个JSON对象或JSON列表
        
        Args:
            json_data (dict or list): 输入的JSON数据，可以是单个对象或列表
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        if isinstance(json_data, list):
            return self.process_batch(json_data)
        else:
            return self.process_item(json_data)
    
    def process_item(self, json_data):
        """
        处理单个JSON数据的方法，子类通常需要实现此方法
        
        Args:
            json_data (dict): 输入的单个JSON数据
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        
        Raises:
            NotImplementedError: 子类必须实现此方法或process_batch方法
        """
        raise NotImplementedError("Subclasses must implement process_item() or process_batch()")
    
    def process_batch(self, json_data_list):
        """
        处理JSON列表的方法，支持批处理的子类可以重写此方法提供优化实现
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表
            
        Raises:
            NotImplementedError: 如果操作符声明支持批处理但未实现此方法
        """
        if self.supports_batch:
            # 对于显式声明支持批处理的子类，应该提供自己的实现
            raise NotImplementedError("Batch-supporting operators must implement process_batch()")
        else:
            # 默认实现：逐个处理列表中的每个项目
            results = []
            for item in json_data_list:
                result = self.process_item(item)
                if isinstance(result, list):
                    # 如果单个项目的处理结果是列表，则展平
                    results.extend(result)
                else:
                    results.append(result)
            return results
    
    def __call__(self, json_data):
        """
        便捷调用方法，内部调用process
        
        Args:
            json_data (dict or list): 输入的JSON数据，可以是单个对象或列表
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        return self.process(json_data)


class JsonOperator(Operator):
    """
    JSON操作符基类，专门处理JSON数据转换
    
    这个类封装了处理JSON数据的操作符。
    """
    
    def __init__(self, name=None, description=None, supports_batch=False):
        """
        初始化JSON操作符
        
        Args:
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            supports_batch (bool, optional): 是否支持批处理JSON列表，默认False
        """
        super().__init__(name, description or "JSON data operator", supports_batch)


class ModelOperator(Operator):
    """
    模型操作符基类，专门处理模型调用
    
    这个类封装了调用大语言模型的操作符。
    """
    
    def __init__(self, name=None, description=None, supports_batch=False, **model_params):
        """
        初始化模型操作符
        
        Args:
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            supports_batch (bool, optional): 是否支持批处理JSON列表，默认False
            **model_params: 模型参数
        """
        super().__init__(name, description or "Model operator", supports_batch)
        self.model_params = model_params 