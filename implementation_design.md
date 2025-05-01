# JSONFlow 实现设计

## 1. 项目结构

```
jsonflow/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── operator.py       # 操作符基类
│   ├── pipeline.py       # 管道类
│   └── executor.py       # 执行器类
├── io/
│   ├── __init__.py
│   ├── loader.py         # JSON加载器
│   └── saver.py          # JSON保存器
├── operators/
│   ├── __init__.py
│   ├── json_ops/         # JSON操作相关操作符
│   │   ├── __init__.py
│   │   ├── text_normalizer.py
│   │   ├── json_filter.py
│   │   └── json_transformer.py
│   └── model/            # 模型相关操作符
│       ├── __init__.py
│       └── model_invoker.py
├── utils/
│   ├── __init__.py
│   ├── logger.py         # 日志工具
│   └── config.py         # 配置工具
└── examples/
    ├── simple_pipeline.py
    └── concurrent_processing.py
```

## 2. 核心组件实现

### 2.1 Operator (core/operator.py)

```python
class Operator:
    """操作符基类，定义处理JSON数据的接口"""
    
    def __init__(self, name=None, description=None):
        self.name = name or self.__class__.__name__
        self.description = description or f"{self.name} operator"
    
    def process(self, json_data):
        """
        处理JSON数据的抽象方法，子类需要实现
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    def __call__(self, json_data):
        """便捷调用方法，内部调用process"""
        return self.process(json_data)


class JsonOperator(Operator):
    """JSON操作符基类，专门处理JSON数据转换"""
    
    def __init__(self, name=None, description=None):
        super().__init__(name, description or "JSON data operator")


class ModelOperator(Operator):
    """模型操作符基类，专门处理模型调用"""
    
    def __init__(self, name=None, description=None, **model_params):
        super().__init__(name, description or "Model operator")
        self.model_params = model_params
```

### 2.2 Pipeline (core/pipeline.py)

```python
class Pipeline:
    """操作符的容器，负责按顺序执行操作符"""
    
    def __init__(self, operators=None):
        self.operators = operators or []
    
    def add(self, operator):
        """添加操作符到管道中"""
        self.operators.append(operator)
        return self
    
    def process(self, json_data):
        """按顺序执行所有操作符"""
        result = json_data
        for op in self.operators:
            result = op.process(result)
        return result
    
    def __iter__(self):
        """迭代器方法，便于遍历所有操作符"""
        return iter(self.operators)
```

### 2.3 Executor (core/executor.py)

```python
import concurrent.futures

class Executor:
    """执行器基类"""
    
    def __init__(self, pipeline):
        self.pipeline = pipeline
    
    def execute(self, json_data):
        """执行Pipeline处理单个JSON数据"""
        return self.pipeline.process(json_data)
    
    def execute_all(self, json_data_list):
        """批量执行Pipeline处理多个JSON数据"""
        results = []
        for data in json_data_list:
            results.append(self.execute(data))
        return results


class SyncExecutor(Executor):
    """同步执行器"""
    pass


class AsyncExecutor(Executor):
    """异步执行器"""
    
    def execute_all(self, json_data_list):
        """异步批量执行"""
        # 具体实现将在完成代码时提供
        pass


class MultiThreadExecutor(Executor):
    """多线程执行器"""
    
    def __init__(self, pipeline, max_workers=None):
        super().__init__(pipeline)
        self.max_workers = max_workers
    
    def execute_all(self, json_data_list):
        """使用多线程批量执行"""
        results = [None] * len(json_data_list)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.execute, data): i 
                for i, data in enumerate(json_data_list)
            }
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                results[index] = future.result()
        return results


class MultiProcessExecutor(Executor):
    """多进程执行器"""
    
    def __init__(self, pipeline, max_workers=None):
        super().__init__(pipeline)
        self.max_workers = max_workers
    
    def execute_all(self, json_data_list):
        """使用多进程批量执行"""
        results = [None] * len(json_data_list)
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.execute, data): i 
                for i, data in enumerate(json_data_list)
            }
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                results[index] = future.result()
        return results
```

### 2.4 JsonLoader (io/loader.py)

```python
import json
import sys

class JsonLoader:
    """从文件或标准输入加载JSON数据"""
    
    def __init__(self, source=None):
        """
        初始化JsonLoader
        
        Args:
            source (str, optional): 数据源，文件路径或None表示从stdin读取
        """
        self.source = source
    
    def load(self):
        """加载所有JSON数据到列表"""
        return list(self)
    
    def __iter__(self):
        """迭代器方法，便于逐行加载JSON"""
        if self.source is None:
            # 从标准输入读取
            for line in sys.stdin:
                if line.strip():
                    yield json.loads(line)
        else:
            # 从文件读取
            with open(self.source, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
```

### 2.5 JsonSaver (io/saver.py)

```python
import json
import sys

class JsonSaver:
    """将JSON数据保存到文件或标准输出"""
    
    def __init__(self, destination=None):
        """
        初始化JsonSaver
        
        Args:
            destination (str, optional): 目标位置，文件路径或None表示输出到stdout
        """
        self.destination = destination
        self._file = None
    
    def __enter__(self):
        if self.destination is not None:
            self._file = open(self.destination, 'w', encoding='utf-8')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file is not None:
            self._file.close()
    
    def write(self, json_data):
        """写入单个JSON数据"""
        json_str = json.dumps(json_data, ensure_ascii=False)
        if self.destination is None:
            # 输出到标准输出
            print(json_str)
        else:
            # 输出到文件
            if self._file is None:
                with open(self.destination, 'a', encoding='utf-8') as f:
                    f.write(json_str + '\n')
            else:
                self._file.write(json_str + '\n')
                self._file.flush()
    
    def write_all(self, json_data_list):
        """批量写入JSON数据"""
        with self:
            for data in json_data_list:
                self.write(data)
```

### 2.6 日志工具 (utils/logger.py 和 utils/operator_utils.py)

```python
import logging
import functools
import json
from typing import Callable, Dict, Any

# logger.py
def get_logger(name):
    """创建或获取日志记录器"""
    logger = logging.getLogger(name)
    # 设置日志格式和级别
    return logger

# operator_utils.py
def log_io(func: Callable) -> Callable:
    """操作符输入输出日志装饰器"""
    @functools.wraps(func)
    def wrapper(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        # 检查是否需要记录日志
        show_io = config.get("logging.show_operator_io", False)
        
        if show_io:
            # 记录输入
            logger.info(f"[{self.name}] 输入:\n{json.dumps(json_data, indent=2)}")
        
        # 调用原始函数
        result = func(self, json_data)
        
        if show_io:
            # 记录输出
            logger.info(f"[{self.name}] 输出:\n{json.dumps(result, indent=2)}")
        
        return result
    
    return wrapper

def enable_operator_io_logging(enable=True):
    """启用或禁用操作符输入输出日志"""
    config.set("logging.show_operator_io", enable)
```

### 2.7 JSON字段操作符 (operators/json_ops/json_field_ops.py)

```python
class JsonFieldSelector(JsonOperator):
    """选择JSON字段操作符"""
    
    def __init__(self, fields=None, exclude_fields=None, name=None):
        """
        初始化JsonFieldSelector
        
        Args:
            fields (list, optional): 需要保留的字段列表
            exclude_fields (list, optional): 需要排除的字段列表
            name (str, optional): 操作符名称
        """
        super().__init__(name, "Select JSON fields operator")
        self.fields = fields or []
        self.exclude_fields = exclude_fields or []
    
    def process(self, json_data):
        """处理JSON数据，仅保留指定字段"""
        if not json_data:
            return {}
        
        result = {}
        if self.fields:
            # 包含模式：仅保留指定字段
            for field in self.fields:
                if field in json_data:
                    result[field] = json_data[field]
        else:
            # 排除模式：排除指定字段
            result = json_data.copy()
            for field in self.exclude_fields:
                if field in result:
                    del result[field]
        
        return result

class JsonPathOperator(JsonOperator):
    """JSON路径操作符基类"""
    
    def __init__(self, name=None, description=None):
        super().__init__(name, description or "JSON path operator")
    
    def _get_value_by_path(self, data, path):
        """通过路径获取值"""
        if not path:
            return data
        
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _set_value_by_path(self, data, path, value):
        """通过路径设置值"""
        if not path:
            return
        
        parts = path.split('.')
        current = data
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
```

### 2.8 JSON表达式操作符 (operators/json_ops/json_expr_ops.py)

```python
class JsonExpressionOperator(JsonOperator):
    """JSON表达式操作符"""
    
    def __init__(self, expressions, name=None, description=None):
        """
        初始化JsonExpressionOperator
        
        Args:
            expressions (dict): 表达式映射，键为目标字段，值为表达式字符串或函数
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(name or "JsonExpressionOperator", description or "Applies expressions to JSON data")
        self.expressions = expressions
    
    def process(self, json_data):
        """处理JSON数据，应用表达式"""
        if not json_data:
            return {}
        
        result = json_data.copy()
        
        for target_field, expression in self.expressions.items():
            try:
                # 处理函数表达式
                if callable(expression):
                    value = expression(json_data)
                    self._set_nested_value(result, target_field, value)
                    continue
                
                # 处理字符串表达式
                value = self._evaluate_expression(expression, json_data)
                self._set_nested_value(result, target_field, value)
            except Exception as e:
                # 表达式求值失败时忽略，可以选择记录错误
                print(f"表达式求值错误(字段: {target_field}): {str(e)}")
                continue
        
        return result
    
    def _evaluate_expression(self, expression, json_data):
        """求值表达式"""
        # 替换表达式中的字段引用
        expr = self._replace_field_references(expression, json_data)
        
        # 创建安全的本地环境
        safe_locals = {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "sum": sum,
            "min": min,
            "max": max,
            # ...更多安全函数
        }
        
        # 使用eval求值表达式
        return eval(expr, {"__builtins__": {}}, safe_locals)
    
    def _replace_field_references(self, expression, json_data):
        """替换表达式中的字段引用"""
        # 查找所有字段引用，支持点号路径
        pattern = r'\$\.[a-zA-Z0-9_.[\]]+|\$\[[\'"]([^\'"]+)[\'"]\]'
        
        # ...实现字段引用替换的逻辑
        
        return replaced_expression
```

### 2.9 配置系统 (utils/config.py)

```python
class Config:
    """配置管理类"""
    
    def __init__(self, config_file=None):
        """
        初始化配置
        
        Args:
            config_file (str, optional): 配置文件路径
        """
        self.config = {}
        
        # 加载默认配置
        self._load_default_config()
        
        # 加载配置文件
        if config_file:
            self._load_config_file(config_file)
        
        # 加载环境变量
        self._load_env_vars()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.config = {
            "log_level": "INFO",
            "logging": {
                "show_operator_io": False,  # 是否显示操作符的输入和输出
                "io_indent": 2,  # 显示输入输出时的缩进空格数
                "truncate_length": 1000  # 截断长输入输出的长度，设为None表示不截断
            },
            "model": {
                "default": "gpt-3.5-turbo",
                "timeout": 30,
                "retries": 3
            },
            "executor": {
                "default_workers": None  # None表示使用系统默认值
            }
        }
    
    def get(self, key, default=None):
        """获取配置值"""
        parts = key.split('.')
        config = self.config
        
        for part in parts:
            if part not in config:
                return default
            config = config[part]
        
        return config
    
    def set(self, key, value):
        """设置配置值"""
        parts = key.split('.')
        config = self.config
        
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
```

### 2.10 其他JSON操作符

```python
class JsonStringOperator(JsonOperator):
    """JSON字符串操作符"""
    
    def __init__(self, field_path, operation, name=None, **operation_params):
        """
        初始化JsonStringOperator
        
        Args:
            field_path (str): 要操作的字段路径，支持点号分隔的路径
            operation (str or callable): 要执行的字符串操作，可以是预定义操作名称或自定义函数
            name (str, optional): 操作符名称
            **operation_params: 操作的附加参数
        """
        super().__init__(name or "JsonStringOperator", f"String operation on {field_path}")
        self.field_path = field_path
        self.operation = operation
        self.operation_params = operation_params
    
    def process(self, json_data):
        """处理JSON数据，对指定字段执行字符串操作"""
        result = json_data.copy()
        
        # 获取字段值
        value = self._get_value_by_path(result, self.field_path)
        
        # 如果值不是字符串，尝试转换
        if value is not None and not isinstance(value, str):
            value = str(value)
        
        # 应用操作
        if value is not None:
            if callable(self.operation):
                # 使用自定义函数
                new_value = self.operation(value, **self.operation_params)
            elif self.operation == "upper":
                new_value = value.upper()
            elif self.operation == "lower":
                new_value = value.lower()
            elif self.operation == "title":
                new_value = value.title()
            elif self.operation == "strip":
                new_value = value.strip()
            elif self.operation == "replace":
                old = self.operation_params.get("old", "")
                new = self.operation_params.get("new", "")
                new_value = value.replace(old, new)
            elif self.operation == "truncate":
                length = self.operation_params.get("length", 100)
                suffix = self.operation_params.get("suffix", "...")
                if len(value) > length:
                    new_value = value[:length] + suffix
                else:
                    new_value = value
            else:
                # 未知操作，保持原值
                new_value = value
            
            # 设置新值
            self._set_value_by_path(result, self.field_path, new_value)
        
        return result


class JsonArrayOperator(JsonOperator):
    """JSON数组操作符"""
    
    def __init__(self, array_path, operation, name=None, **operation_params):
        """
        初始化JsonArrayOperator
        
        Args:
            array_path (str): 数组字段的路径，支持点号分隔的路径
            operation (str or callable): 要执行的数组操作，可以是预定义操作名称或自定义函数
            name (str, optional): 操作符名称
            **operation_params: 操作的附加参数
        """
        super().__init__(name or "JsonArrayOperator", f"Array operation on {array_path}")
        self.array_path = array_path
        self.operation = operation
        self.operation_params = operation_params
    
    def process(self, json_data):
        """处理JSON数据，对指定数组字段执行操作"""
        result = json_data.copy()
        
        # 获取数组
        array = self._get_value_by_path(result, self.array_path)
        
        # 确保是数组
        if array is None:
            array = []
        elif not isinstance(array, list):
            array = [array]
        
        # 应用操作
        if callable(self.operation):
            # 使用自定义函数
            new_array = self.operation(array, **self.operation_params)
        elif self.operation == "filter":
            # 过滤数组元素
            field = self.operation_params.get("field")
            value = self.operation_params.get("value")
            operator = self.operation_params.get("operator", "eq")
            
            if field and value is not None:
                new_array = []
                for item in array:
                    if isinstance(item, dict) and field in item:
                        item_value = item[field]
                        if operator == "eq" and item_value == value:
                            new_array.append(item)
                        elif operator == "neq" and item_value != value:
                            new_array.append(item)
                        elif operator == "gt" and item_value > value:
                            new_array.append(item)
                        elif operator == "gte" and item_value >= value:
                            new_array.append(item)
                        elif operator == "lt" and item_value < value:
                            new_array.append(item)
                        elif operator == "lte" and item_value <= value:
                            new_array.append(item)
                        elif operator == "contains" and value in item_value:
                            new_array.append(item)
            else:
                new_array = array
        elif self.operation == "map":
            # 映射数组元素
            field = self.operation_params.get("field")
            if field:
                new_array = []
                for item in array:
                    if isinstance(item, dict) and field in item:
                        new_array.append(item[field])
                    else:
                        new_array.append(None)
            else:
                new_array = array
        elif self.operation == "sort":
            # 排序数组
            field = self.operation_params.get("field")
            reverse = self.operation_params.get("reverse", False)
            
            if field:
                # 按字段排序
                new_array = sorted(
                    array,
                    key=lambda x: x.get(field) if isinstance(x, dict) else None,
                    reverse=reverse
                )
            else:
                # 直接排序
                new_array = sorted(array, reverse=reverse)
        elif self.operation == "slice":
            # 切片数组
            start = self.operation_params.get("start", 0)
            end = self.operation_params.get("end", None)
            new_array = array[start:end]
        elif self.operation == "uniq":
            # 去重
            try:
                new_array = list(dict.fromkeys(array))
            except TypeError:
                # 如果元素不可哈希，退回到原数组
                new_array = array
        else:
            # 未知操作，保持原数组
            new_array = array
        
        # 设置新数组
        self._set_value_by_path(result, self.array_path, new_array)
        
        return result


class DebugOperator(JsonOperator):
    """调试操作符，打印当前的JSON数据和处理信息"""
    
    def __init__(self, name=None, label=None):
        """
        初始化DebugOperator
        
        Args:
            name (str, optional): 操作符名称
            label (str, optional): 调试标签
        """
        super().__init__(name or "DebugOperator", "Print debug information")
        self.label = label or "DEBUG"
    
    def process(self, json_data):
        """处理JSON数据，打印调试信息"""
        print(f"[{self.label}] JSON Data:")
        print(json.dumps(json_data, indent=2, ensure_ascii=False))
        return json_data


class MockModelOperator(ModelOperator):
    """模拟模型操作符，用于测试和开发"""
    
    def __init__(self, response=None, name=None):
        """
        初始化MockModelOperator
        
        Args:
            response (dict or callable, optional): 预定义的响应或响应生成函数
            name (str, optional): 操作符名称
        """
        super().__init__(name or "MockModelOperator", "Mock model for testing")
        self.response = response
    
    def process(self, json_data):
        """处理JSON数据，返回模拟的模型响应"""
        result = json_data.copy()
        
        if callable(self.response):
            # 使用函数生成响应
            model_response = self.response(json_data)
        elif self.response is not None:
            # 使用预定义响应
            model_response = self.response
        else:
            # 默认响应
            model_response = {
                "model": "mock-model",
                "response": f"This is a mock response for: {json_data.get('text', '')}",
                "processed_at": datetime.datetime.now().isoformat()
            }
        
        # 将模型响应合并到结果中
        if isinstance(model_response, dict):
            result.update(model_response)
        else:
            result["model_response"] = model_response
        
        return result
```

### 2.11 JSON模板操作符

```python
class JsonTemplateOperator(JsonOperator):
    """JSON模板操作符"""
    
    def __init__(self, templates, name=None, description=None):
        """
        初始化JsonTemplateOperator
        
        Args:
            templates (dict): 模板映射，键为目标字段，值为模板字符串
                模板字符串中可以使用 {field.path} 格式引用JSON字段
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonTemplateOperator",
            description or "Applies string templates to JSON data"
        )
        self.templates = templates
    
    def process(self, json_data):
        """处理JSON数据，应用模板"""
        if not json_data:
            return {}
        
        result = json_data.copy()
        
        for target_field, template in self.templates.items():
            try:
                # 解析模板并替换字段引用
                value = self._render_template(template, json_data)
                
                # 设置目标字段
                self._set_nested_value(result, target_field, value)
            except Exception as e:
                # 模板渲染失败时忽略
                print(f"模板渲染错误(字段: {target_field}): {str(e)}")
                continue
        
        return result
    
    def _render_template(self, template, json_data):
        """渲染模板"""
        # 查找所有字段引用
        pattern = r'\{([^{}|]+)(?:\|([^{}]+))?\}'
        
        def replace_field(match):
            field_path = match.group(1).strip()
            modifiers = match.group(2).strip() if match.group(2) else None
            
            # 获取字段值
            value = self._get_by_path(json_data, field_path)
            
            # 应用修饰符
            if modifiers:
                for mod in modifiers.split('|'):
                    if ':' in mod:
                        mod_name, mod_arg = mod.split(':', 1)
                    else:
                        mod_name, mod_arg = mod, None
                    
                    # 应用各种修饰符
                    if mod_name == 'upper' and isinstance(value, str):
                        value = value.upper()
                    elif mod_name == 'lower' and isinstance(value, str):
                        value = value.lower()
                    # ... 更多修饰符
            
            return str(value) if value is not None else ""
        
        return re.sub(pattern, replace_field, template)
    
    def _get_by_path(self, data, path):
        """通过路径获取值"""
        if not path:
            return data
        
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, data, path, value):
        """设置嵌套字段的值"""
        if '.' not in path:
            data[path] = value
            return
        
        parts = path.split('.')
        current = data
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
```

## 3. 操作符实现

### 3.1 TextNormalizer (operators/json_ops/text_normalizer.py)

```python
from jsonflow.core import JsonOperator

class TextNormalizer(JsonOperator):
    """文本规范化操作符"""
    
    def __init__(self, text_fields=None, name=None, description=None):
        """
        初始化TextNormalizer
        
        Args:
            text_fields (list, optional): 要规范化的文本字段列表，为None时处理所有字符串字段
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name,
            description or "Normalizes text fields in JSON data"
        )
        self.text_fields = text_fields
    
    def process(self, json_data):
        """处理JSON数据，规范化文本字段"""
        if not json_data:
            return json_data
        
        result = json_data.copy()
        self._normalize_fields(result)
        return result
    
    def _normalize_fields(self, data, path=""):
        """递归处理字段"""
        if isinstance(data, dict):
            for key, value in list(data.items()):
                current_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    if self.text_fields is None or current_path in self.text_fields:
                        data[key] = self._normalize_text(value)
                elif isinstance(value, (dict, list)):
                    self._normalize_fields(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, str):
                    if self.text_fields is None:
                        data[i] = self._normalize_text(item)
                elif isinstance(item, (dict, list)):
                    self._normalize_fields(item, path)
    
    def _normalize_text(self, text):
        """执行文本规范化"""
        # 基本的文本规范化规则
        return text.strip()
```

### 3.2 ModelInvoker (operators/model/model_invoker.py)

```python
from jsonflow.core import ModelOperator

class ModelInvoker(ModelOperator):
    """大语言模型调用操作符"""
    
    def __init__(self, model, prompt_field="prompt", response_field="response", name=None, description=None, **model_params):
        """
        初始化ModelInvoker
        
        Args:
            model (str): 模型名称
            prompt_field (str): 输入字段名
            response_field (str): 输出字段名
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            **model_params: 模型参数
        """
        super().__init__(
            name,
            description or f"Invokes {model} model",
            **model_params
        )
        self.model = model
        self.prompt_field = prompt_field
        self.response_field = response_field
    
    def process(self, json_data):
        """处理JSON数据，调用模型"""
        if not json_data or self.prompt_field not in json_data:
            return json_data
        
        result = json_data.copy()
        prompt = result[self.prompt_field]
        
        # 这里是模型调用的实现，具体代码将在完整实现时提供
        response = self._invoke_model(prompt)
        
        result[self.response_field] = response
        return result
    
    def _invoke_model(self, prompt):
        """调用模型的具体实现"""
        # 在实际实现中，这里会连接到各种LLM API
        # 例如OpenAI, Anthropic, HuggingFace等
        # 示例实现将在完整代码中提供
        return f"Model response to: {prompt}"
```

## 4. 工具实现

### 4.1 Logger (utils/logger.py)

```python
import logging
import sys

def get_logger(name, level=None):
    """获取配置好的logger实例"""
    logger = logging.getLogger(name)
    
    # 设置日志级别
    level = level or logging.INFO
    logger.setLevel(level)
    
    # 添加控制台处理器
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
```

### 4.2 Config (utils/config.py)

```python
import os
import json

class Config:
    """配置管理类"""
    
    def __init__(self, config_file=None):
        """
        初始化配置
        
        Args:
            config_file (str, optional): 配置文件路径
        """
        self.config = {}
        
        # 加载默认配置
        self._load_default_config()
        
        # 加载配置文件
        if config_file:
            self._load_config_file(config_file)
        
        # 加载环境变量
        self._load_env_vars()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.config = {
            "log_level": "INFO",
            "model": {
                "default": "gpt-3.5-turbo",
                "timeout": 30,
                "retries": 3
            },
            "executor": {
                "default_workers": None  # None表示使用系统默认值
            }
        }
    
    def _load_config_file(self, config_file):
        """从文件加载配置"""
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading config file: {e}", file=sys.stderr)
    
    def _load_env_vars(self):
        """从环境变量加载配置"""
        # 示例: JSONFLOW_LOG_LEVEL 会覆盖 config["log_level"]
        if "JSONFLOW_LOG_LEVEL" in os.environ:
            self.config["log_level"] = os.environ["JSONFLOW_LOG_LEVEL"]
        
        # 示例: JSONFLOW_MODEL_DEFAULT 会覆盖 config["model"]["default"]
        if "JSONFLOW_MODEL_DEFAULT" in os.environ:
            self.config["model"]["default"] = os.environ["JSONFLOW_MODEL_DEFAULT"]
    
    def _merge_config(self, new_config, base_config=None, path=None):
        """递归合并配置"""
        if base_config is None:
            base_config = self.config
        
        path = path or []
        
        for key, value in new_config.items():
            current_path = path + [key]
            
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._merge_config(value, base_config[key], current_path)
            else:
                base_config[key] = value
    
    def get(self, key, default=None):
        """获取配置值"""
        parts = key.split('.')
        config = self.config
        
        for part in parts:
            if part not in config:
                return default
            config = config[part]
        
        return config
```

## 5. 示例实现

### 5.1 简单管道 (examples/simple_pipeline.py)

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

def run_simple_pipeline():
    # 创建一个简单管道
    pipeline = Pipeline([
        TextNormalizer(),
        ModelInvoker(model="gpt-3.5-turbo"),
    ])
    
    # 从文件加载JSON数据
    loader = JsonLoader("input.jsonl")
    
    # 保存处理结果
    saver = JsonSaver("output.jsonl")
    
    # 处理每一行JSON数据
    for json_line in loader:
        result = pipeline.process(json_line)
        saver.write(result)

if __name__ == "__main__":
    run_simple_pipeline()
```

### 5.2 并发处理 (examples/concurrent_processing.py)

```python
from jsonflow.core import Pipeline
from jsonflow.core import MultiThreadExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

def run_concurrent_pipeline():
    # 创建一个管道
    pipeline = Pipeline([
        TextNormalizer(),
        ModelInvoker(model="gpt-3.5-turbo"),
    ])
    
    # 创建一个多线程执行器
    executor = MultiThreadExecutor(pipeline, max_workers=4)
    
    # 从文件加载所有JSON数据
    loader = JsonLoader("input.jsonl")
    json_data_list = loader.load()
    
    # 并发处理所有数据
    results = executor.execute_all(json_data_list)
    
    # 保存处理结果
    saver = JsonSaver("output.jsonl")
    saver.write_all(results)

if __name__ == "__main__":
    run_concurrent_pipeline()
```

## 6. 单元测试设计

单元测试将覆盖以下几个方面：

1. 核心组件测试
   - Operator基类测试
   - Pipeline测试
   - 各类Executor测试

2. IO组件测试
   - JsonLoader测试
   - JsonSaver测试

3. 操作符测试
   - TextNormalizer测试
   - ModelInvoker测试

4. 集成测试
   - 简单管道测试
   - 并发处理测试

具体的测试代码将在实现过程中提供。

## 3. 使用示例

### 3.1 基本使用

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

# 创建一个简单管道
pipeline = Pipeline([
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo"),
])

# 从文件加载JSON数据
loader = JsonLoader("input.jsonl")

# 保存处理结果
saver = JsonSaver("output.jsonl")

# 处理每一行JSON数据
for json_line in loader:
    result = pipeline.process(json_line)
    saver.write(result)
```

### 3.2 表达式操作示例

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import JsonExpressionOperator

# 创建表达式操作符
expr_op = JsonExpressionOperator({
    # 使用Lambda函数计算总金额
    "total_amount": lambda d: sum(order["price"] * order["quantity"] for order in d["orders"]),
    
    # 提取字段并格式化
    "summary": lambda d: f"{d['user']['name']}的订单总金额为¥{sum(o['price'] * o['quantity'] for o in d['orders']):.2f}",
    
    # 创建嵌套字段
    "customer.full_name": lambda d: f"{d['user']['first_name']} {d['user']['last_name']}",
    
    # 数组处理
    "product_names": lambda d: [item["name"] for item in d["items"]]
})

# 创建数据
data = {
    "user": {"name": "张三", "first_name": "张", "last_name": "三"},
    "orders": [
        {"id": "1", "product": "手机", "price": 5999, "quantity": 1},
        {"id": "2", "product": "耳机", "price": 999, "quantity": 2}
    ],
    "items": [
        {"id": "1", "name": "iPhone"},
        {"id": "2", "name": "AirPods"}
    ]
}

# 处理数据
result = expr_op.process(data)
print(result["total_amount"])  # 输出: 7997
print(result["summary"])       # 输出: 张三的订单总金额为¥7997.00
print(result["product_names"]) # 输出: ['iPhone', 'AirPods']
```

### 3.3 带操作符日志的使用示例

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer, JsonExpressionOperator
from jsonflow.utils import enable_operator_io_logging, get_logger

# 获取日志记录器
logger = get_logger("example")

# 启用操作符输入输出日志
enable_operator_io_logging(True)

# 创建并运行管道
pipeline = Pipeline([
    TextNormalizer(),
    JsonExpressionOperator({
        "processed_text": lambda d: f"处理后的文本: {d.get('text', '')}"
    })
])

# 处理数据
result = pipeline.process({"text": "示例文本"})
logger.info(f"处理结果: {result}")

# 禁用操作符日志
enable_operator_io_logging(False)
``` 