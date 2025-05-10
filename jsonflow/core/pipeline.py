"""
管道模块

该模块定义了Pipeline类，用于按顺序执行多个操作符。
"""

class Pipeline:
    """
    操作符的容器，负责按顺序执行操作符
    
    Pipeline类封装了一系列操作符，并按顺序执行它们。
    支持处理单个JSON对象或JSON列表，具有两种集合处理模式。
    """
    
    # 集合处理模式常量
    FLATTEN = 'flatten'  # 展平模式：自动展平操作符返回的列表
    NESTED = 'nested'    # 嵌套模式：保持列表的嵌套结构
    
    def __init__(self, operators=None, passthrough_fields=None, collection_mode=FLATTEN):
        """
        初始化Pipeline
        
        Args:
            operators (list, optional): 操作符列表，如果不提供则创建空列表
            passthrough_fields (list, optional): 需要透传的字段列表
            collection_mode (str, optional): 集合处理模式，'flatten'或'nested'
        """
        self.operators = operators or []
        self.passthrough_fields = passthrough_fields or []
        self.collection_mode = collection_mode
    
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
    
    def set_collection_mode(self, mode):
        """
        设置集合处理模式
        
        Args:
            mode (str): 'flatten'或'nested'
        
        Returns:
            Pipeline: 返回self以支持链式调用
        """
        if mode not in [self.FLATTEN, self.NESTED]:
            raise ValueError(f"Collection mode must be '{self.FLATTEN}' or '{self.NESTED}'")
        self.collection_mode = mode
        return self
    
    def _apply_passthrough(self, original_data, processed_data):
        """
        应用字段透传逻辑
        
        Args:
            original_data (dict): 原始JSON数据
            processed_data (dict): 处理后的JSON数据
            
        Returns:
            dict: 添加了透传字段的JSON数据
        """
        # 提取需要透传的字段值
        passthrough_values = {}
        for field in self.passthrough_fields:
            if field in original_data:
                passthrough_values[field] = original_data[field]
        
        # 将透传字段添加到处理后的数据中
        result = processed_data.copy()
        for field, value in passthrough_values.items():
            result[field] = value
        
        return result
    
    def process(self, json_data):
        """
        按顺序执行所有操作符，并处理透传字段
        
        Args:
            json_data (dict or list): 输入的JSON数据，可以是单个对象或列表
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        # 记录原始输入是否为列表
        is_list_input = isinstance(json_data, list)
        
        # 如果输入是列表，根据集合处理模式处理
        if is_list_input:
            if self.collection_mode == self.NESTED:
                # 嵌套模式：将整个列表作为一个整体传递给操作符链
                result = json_data
                for op in self.operators:
                    result = op.process(result)
                return result
            else:
                # 展平模式：分别处理列表中的每个项目
                results = []
                for item in json_data:
                    # 处理单个项目
                    result = self._process_single_item(item)
                    # 收集结果
                    if isinstance(result, list):
                        results.extend(result)
                    else:
                        results.append(result)
                return results
        else:
            # 单个JSON对象的处理
            return self._process_single_item(json_data)
    
    def _process_single_item(self, json_data):
        """
        处理单个JSON数据项通过所有操作符
        
        Args:
            json_data (dict): 输入的单个JSON数据
            
        Returns:
            dict or list: 处理后的JSON数据，可能是单个对象或列表
        """
        result = json_data
        original_data = json_data.copy()  # 保存原始数据用于透传
        
        for op in self.operators:
            # 处理当前项
            op_result = op.process(result)
            
            # 根据操作符结果类型和集合处理模式决定如何继续
            if isinstance(op_result, list):
                if self.collection_mode == self.NESTED:
                    # 嵌套模式：保持列表结构传递给下一个操作符
                    result = op_result
                else:
                    # 展平模式：处理列表中的每个项目，应用透传，然后返回
                    processed_results = []
                    for item in op_result:
                        # 应用透传字段到列表中的每个项
                        processed_item = self._apply_passthrough(original_data, item)
                        processed_results.append(processed_item)
                    return processed_results
            else:
                # 结果是单个对象，继续处理
                result = op_result
        
        # 如果结果是单个对象，处理透传字段
        if not isinstance(result, list):
            result = self._apply_passthrough(original_data, result)
        
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