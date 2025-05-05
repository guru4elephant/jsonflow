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
│   ├── config.py         # 配置工具
│   └── system_field.py   # 系统字段管理
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
    
    def __init__(self, operators=None, passthrough_fields=None):
        """
        初始化Pipeline
        
        Args:
            operators (list, optional): 操作符列表
            passthrough_fields (list, optional): 需要透传的字段列表
        """
        self.operators = operators or []
        self.passthrough_fields = passthrough_fields or []
    
    def add(self, operator):
        """添加操作符到管道中"""
        self.operators.append(operator)
        return self
    
    def set_passthrough_fields(self, fields):
        """
        设置需要透传的字段列表
        
        Args:
            fields (list): 字段名列表
        
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
            dict: 处理后的JSON数据
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

### 2.6 系统字段管理 (utils/system_field.py)

```python
import uuid
import time
import datetime

class SystemField:
    """系统字段管理类，用于创建和管理系统字段"""
    
    @staticmethod
    def add_id(json_data, field_name='id', override=False):
        """
        添加UUID字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str, optional): 字段名，默认为'id'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了ID字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = str(uuid.uuid4())
        return result
    
    @staticmethod
    def add_timestamp(json_data, field_name='timestamp', override=False):
        """
        添加时间戳字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str, optional): 字段名，默认为'timestamp'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了时间戳字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = int(time.time())
        return result
    
    @staticmethod
    def add_datetime(json_data, field_name='datetime', format='%Y-%m-%d %H:%M:%S', override=False):
        """
        添加日期时间字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str, optional): 字段名，默认为'datetime'
            format (str, optional): 日期时间格式，默认为'%Y-%m-%d %H:%M:%S'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了日期时间字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = datetime.datetime.now().strftime(format)
        return result
    
    @staticmethod
    def add_custom_field(json_data, field_name, value, override=False):
        """
        添加自定义字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str): 字段名
            value: 字段值
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            
        Returns:
            dict: 添加了自定义字段的JSON数据
        """
        result = json_data.copy()
        if field_name not in result or override:
            result[field_name] = value
        return result
    
    @staticmethod
    def remove_field(json_data, field_name):
        """
        移除字段
        
        Args:
            json_data (dict): 输入的JSON数据
            field_name (str): 字段名
            
        Returns:
            dict: 移除了指定字段的JSON数据
        """
        result = json_data.copy()
        if field_name in result:
            del result[field_name]
        return result
```

### 2.7 系统字段操作符 (operators/json_ops/system_field_ops.py)

```python
from jsonflow.core import JsonOperator
from jsonflow.utils.system_field import SystemField

class IdAdder(JsonOperator):
    """添加ID系统字段的操作符"""
    
    def __init__(self, field_name='id', override=False, name=None):
        """
        初始化IdAdder
        
        Args:
            field_name (str, optional): 字段名，默认为'id'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加ID字段"""
        return SystemField.add_id(json_data, self.field_name, self.override)


class TimestampAdder(JsonOperator):
    """添加时间戳系统字段的操作符"""
    
    def __init__(self, field_name='timestamp', override=False, name=None):
        """
        初始化TimestampAdder
        
        Args:
            field_name (str, optional): 字段名，默认为'timestamp'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加时间戳字段"""
        return SystemField.add_timestamp(json_data, self.field_name, self.override)


class DateTimeAdder(JsonOperator):
    """添加日期时间系统字段的操作符"""
    
    def __init__(self, field_name='datetime', format='%Y-%m-%d %H:%M:%S', override=False, name=None):
        """
        初始化DateTimeAdder
        
        Args:
            field_name (str, optional): 字段名，默认为'datetime'
            format (str, optional): 日期时间格式，默认为'%Y-%m-%d %H:%M:%S'
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.format = format
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加日期时间字段"""
        return SystemField.add_datetime(json_data, self.field_name, self.format, self.override)


class CustomFieldAdder(JsonOperator):
    """添加自定义系统字段的操作符"""
    
    def __init__(self, field_name, value, override=False, name=None):
        """
        初始化CustomFieldAdder
        
        Args:
            field_name (str): 字段名
            value: 字段值
            override (bool, optional): 是否覆盖已存在的字段，默认为False
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Add {field_name} field operator")
        self.field_name = field_name
        self.value = value
        self.override = override
    
    def process(self, json_data):
        """处理JSON数据，添加自定义字段"""
        return SystemField.add_custom_field(json_data, self.field_name, self.value, self.override)


class FieldRemover(JsonOperator):
    """移除字段的操作符"""
    
    def __init__(self, field_name, name=None):
        """
        初始化FieldRemover
        
        Args:
            field_name (str): 字段名
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Remove {field_name} field operator")
        self.field_name = field_name
    
    def process(self, json_data):
        """处理JSON数据，移除指定字段"""
        return SystemField.remove_field(json_data, self.field_name)
```

## 5. 示例实现

### 5.1 透传字段示例 (examples/passthrough_fields_example.py)

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

def run_passthrough_example():
    """演示字段透传功能"""
    
    # 创建一个带有透传字段的管道
    pipeline = Pipeline([
        TextNormalizer(),
        ModelInvoker(model="gpt-3.5-turbo"),
    ])
    
    # 设置需要透传的字段
    pipeline.set_passthrough_fields(['id', 'metadata'])
    
    # 从文件加载JSON数据
    loader = JsonLoader("input.jsonl")
    
    # 保存处理结果
    saver = JsonSaver("output.jsonl")
    
    # 处理每一行JSON数据
    for json_line in loader:
        result = pipeline.process(json_line)
        saver.write(result)
        
    print("处理完成，透传字段'id'和'metadata'已保留")

if __name__ == "__main__":
    run_passthrough_example()
```

### 5.2 系统字段示例 (examples/system_fields_example.py)

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.json_ops.system_field_ops import IdAdder, TimestampAdder
from jsonflow.operators.model import ModelInvoker
from jsonflow.utils.system_field import SystemField

def run_system_fields_example():
    """演示系统字段功能"""
    
    # 创建一个包含系统字段操作符的管道
    pipeline = Pipeline([
        IdAdder(),  # 添加UUID作为id字段
        TimestampAdder(),  # 添加时间戳
        TextNormalizer(),
        ModelInvoker(model="gpt-3.5-turbo"),
    ])
    
    # 从文件加载JSON数据
    loader = JsonLoader("input.jsonl")
    
    # 保存处理结果
    saver = JsonSaver("output.jsonl")
    
    # 处理每一行JSON数据
    for json_line in loader:
        # 直接使用SystemField工具类添加自定义字段
        json_line = SystemField.add_custom_field(json_line, 'source', 'example')
        
        # 通过管道处理数据
        result = pipeline.process(json_line)
        saver.write(result)
        
    print("处理完成，已添加系统字段'id'、'timestamp'和'source'")

if __name__ == "__main__":
    run_system_fields_example()
```

## 6. 单元测试设计

### 6.1 透传字段测试 (tests/test_passthrough_fields.py)

```python
import unittest
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer

class MockOperator:
    """用于测试的模拟操作符"""
    def process(self, json_data):
        # 简单返回一个新对象，不保留原有字段
        return {"result": "processed"}

class PassthroughFieldsTest(unittest.TestCase):

    def test_passthrough_single_field(self):
        """测试单个字段透传"""
        pipeline = Pipeline([MockOperator()])
        pipeline.set_passthrough_fields(['id'])
        
        input_data = {"id": "12345", "text": "test data"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["result"], "processed")
        self.assertNotIn("text", result)
    
    def test_passthrough_multiple_fields(self):
        """测试多个字段透传"""
        pipeline = Pipeline([MockOperator()])
        pipeline.set_passthrough_fields(['id', 'metadata'])
        
        input_data = {"id": "12345", "metadata": {"source": "test"}, "text": "test data"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["metadata"]["source"], "test")
        self.assertEqual(result["result"], "processed")
        self.assertNotIn("text", result)
    
    def test_passthrough_nonexistent_field(self):
        """测试不存在的字段透传"""
        pipeline = Pipeline([MockOperator()])
        pipeline.set_passthrough_fields(['id', 'nonexistent'])
        
        input_data = {"id": "12345", "text": "test data"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["result"], "processed")
        self.assertNotIn("nonexistent", result)
        self.assertNotIn("text", result)
    
    def test_passthrough_with_real_operator(self):
        """测试与真实操作符的集成"""
        pipeline = Pipeline([TextNormalizer()])
        pipeline.set_passthrough_fields(['id'])
        
        input_data = {"id": "12345", "text": "TEST DATA"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["text"], "test data")

if __name__ == '__main__':
    unittest.main()
```

### 6.2 系统字段测试 (tests/test_system_fields.py)

```python
import unittest
import re
from jsonflow.utils.system_field import SystemField
from jsonflow.operators.json_ops.system_field_ops import IdAdder, TimestampAdder, DateTimeAdder, CustomFieldAdder, FieldRemover

class SystemFieldTest(unittest.TestCase):

    def test_add_id(self):
        """测试添加ID字段"""
        data = {"text": "test data"}
        result = SystemField.add_id(data)
        
        self.assertIn("id", result)
        self.assertIsInstance(result["id"], str)
        # 验证格式为UUID
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.assertTrue(re.match(uuid_pattern, result["id"]))
    
    def test_add_timestamp(self):
        """测试添加时间戳字段"""
        data = {"text": "test data"}
        result = SystemField.add_timestamp(data)
        
        self.assertIn("timestamp", result)
        self.assertIsInstance(result["timestamp"], int)
    
    def test_add_datetime(self):
        """测试添加日期时间字段"""
        data = {"text": "test data"}
        result = SystemField.add_datetime(data)
        
        self.assertIn("datetime", result)
        self.assertIsInstance(result["datetime"], str)
        # 验证格式为日期时间
        datetime_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        self.assertTrue(re.match(datetime_pattern, result["datetime"]))
    
    def test_add_custom_field(self):
        """测试添加自定义字段"""
        data = {"text": "test data"}
        result = SystemField.add_custom_field(data, "source", "test")
        
        self.assertIn("source", result)
        self.assertEqual(result["source"], "test")
    
    def test_remove_field(self):
        """测试移除字段"""
        data = {"id": "12345", "text": "test data"}
        result = SystemField.remove_field(data, "id")
        
        self.assertNotIn("id", result)
        self.assertIn("text", result)
    
    def test_id_adder_operator(self):
        """测试ID添加操作符"""
        operator = IdAdder()
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("id", result)
    
    def test_timestamp_adder_operator(self):
        """测试时间戳添加操作符"""
        operator = TimestampAdder()
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("timestamp", result)
    
    def test_datetime_adder_operator(self):
        """测试日期时间添加操作符"""
        operator = DateTimeAdder()
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("datetime", result)
    
    def test_custom_field_adder_operator(self):
        """测试自定义字段添加操作符"""
        operator = CustomFieldAdder("source", "test")
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("source", result)
        self.assertEqual(result["source"], "test")
    
    def test_field_remover_operator(self):
        """测试字段移除操作符"""
        operator = FieldRemover("id")
        data = {"id": "12345", "text": "test data"}
        result = operator.process(data)
        
        self.assertNotIn("id", result)
        self.assertIn("text", result)

if __name__ == '__main__':
    unittest.main()
```

## 3. 使用示例

### 3.1 透传字段示例

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

# 创建一个Pipeline并设置透传字段
pipeline = Pipeline([
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo")
])
pipeline.set_passthrough_fields(['id', 'metadata'])

# 从文件加载JSON数据
loader = JsonLoader("input.jsonl")

# 保存处理结果
saver = JsonSaver("output.jsonl")

# 处理每一行JSON数据
for json_line in loader:
    result = pipeline.process(json_line)
    saver.write(result)
```

### 3.2 系统字段示例

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.json_ops.system_field_ops import IdAdder, TimestampAdder
from jsonflow.operators.model import ModelInvoker
from jsonflow.utils.system_field import SystemField

# 创建一个包含系统字段操作符的管道
pipeline = Pipeline([
    IdAdder(),  # 添加UUID作为id字段
    TimestampAdder(),  # 添加时间戳
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo")
])

# 从文件加载JSON数据
loader = JsonLoader("input.jsonl")

# 保存处理结果
saver = JsonSaver("output.jsonl")

# 处理每一行JSON数据并添加自定义系统字段
for json_line in loader:
    # 直接使用SystemField工具类添加自定义字段
    json_line = SystemField.add_custom_field(json_line, 'source', 'example')
    
    # 通过管道处理数据
    result = pipeline.process(json_line)
    saver.write(result)
```

### 3.3 结合透传字段与系统字段

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.json_ops.system_field_ops import IdAdder, TimestampAdder
from jsonflow.operators.model import ModelInvoker

# 创建管道
pipeline = Pipeline([
    IdAdder(),  # 添加UUID作为id字段
    TimestampAdder(),  # 添加时间戳
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo")
])

# 设置id和timestamp为透传字段，确保它们不会在后续处理中丢失
pipeline.set_passthrough_fields(['id', 'timestamp'])

# 处理数据
loader = JsonLoader("input.jsonl")
saver = JsonSaver("output.jsonl")

for json_line in loader:
    result = pipeline.process(json_line)
    saver.write(result)
```