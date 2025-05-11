# JSONFlow API 文档

JSONFlow 是一个强大的 JSON 数据处理库，专为构建可扩展、高性能的 JSON 数据处理流水线而设计。它允许你通过组合不同的操作符（Operators）来创建复杂的数据处理管道（Pipeline），并支持并发处理以提高性能。

## 目录

- [安装](#安装)
- [核心概念](#核心概念)
- [基本用法](#基本用法)
- [核心 API](#核心-api)
  - [Operator](#operator)
  - [Pipeline](#pipeline)
  - [Executor](#executor)
- [IO 组件](#io-组件)
  - [JsonLoader](#jsonloader)
  - [JsonSaver](#jsonsaver)
- [操作符](#操作符)
  - [基础操作符](#基础操作符)
  - [字段操作符](#字段操作符)
  - [表达式操作符](#表达式操作符)
  - [系统字段操作符](#系统字段操作符)
  - [集合操作符](#集合操作符)
  - [模型操作符](#模型操作符)
- [工具组件](#工具组件)
  - [系统字段工具](#系统字段工具)
  - [BOS 工具](#bos-工具)
- [高级功能](#高级功能)
  - [字段透传](#字段透传)
  - [集合处理模式](#集合处理模式)
  - [并发处理](#并发处理)
- [自定义开发](#自定义开发)
  - [自定义操作符](#自定义操作符)
  - [自定义执行器](#自定义执行器)
- [完整示例](#完整示例)

## 安装

使用 pip 安装 JSONFlow：

```bash
pip install guru4elephant-jsonflow
```

如果需要使用特定功能，可以安装对应的额外依赖：

```bash
# 包含百度对象存储(BOS)支持
pip install guru4elephant-jsonflow[bos]

# 包含开发工具
pip install guru4elephant-jsonflow[dev]

# 包含所有可选依赖
pip install guru4elephant-jsonflow[all]
```

## 核心概念

- **Operator（操作符）**：处理 JSON 数据的基本单元，每个操作符接收 JSON 数据作为输入，执行特定处理，并输出处理后的 JSON 数据。
- **Pipeline（管道）**：操作符的有序集合，负责协调多个操作符的执行顺序，并管理数据在操作符之间的传递。
- **Executor（执行器）**：负责执行 Pipeline，支持同步、多线程、多进程等执行方式。
- **JsonLoader（加载器）**：从文件或标准输入加载 JSON 数据。
- **JsonSaver（保存器）**：将处理后的 JSON 数据保存到文件或标准输出。

## 基本用法

以下是 JSONFlow 的基本使用示例：

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

# 创建操作符
text_normalizer = TextNormalizer()
model_invoker = ModelInvoker(model="gpt-3.5-turbo")

# 创建管道
pipeline = Pipeline([text_normalizer, model_invoker])

# 加载数据
loader = JsonLoader("input.jsonl")

# 保存处理结果
saver = JsonSaver("output.jsonl")

# 处理数据
for json_data in loader:
    processed_data = pipeline.process(json_data)
    saver.write(processed_data)
```

## 核心 API

### Operator

`Operator` 是所有操作符的基类，定义了处理 JSON 数据的基本接口。

#### 主要方法

```python
class Operator:
    def __init__(self, name=None, description=None, supports_batch=False):
        """
        初始化操作符
        
        参数:
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            supports_batch (bool, optional): 是否支持批处理
        """
        pass
        
    def process(self, json_data):
        """
        处理 JSON 数据
        
        参数:
            json_data (dict or list): 输入的 JSON 数据，可以是单个对象或列表
            
        返回:
            dict or list: 处理后的 JSON 数据
        """
        pass
        
    def process_item(self, json_data):
        """
        处理单个 JSON 数据项
        
        参数:
            json_data (dict): 输入的单个 JSON 数据
            
        返回:
            dict or list: 处理后的 JSON 数据
        """
        pass
        
    def process_batch(self, json_data_list):
        """
        处理 JSON 数据列表
        
        参数:
            json_data_list (list): 输入的 JSON 数据列表
            
        返回:
            list: 处理后的 JSON 数据列表
        """
        pass
```

### Pipeline

`Pipeline` 是操作符的容器，负责按顺序执行多个操作符，并管理数据流。

#### 主要方法

```python
class Pipeline:
    def __init__(self, operators=None, passthrough_fields=None, collection_mode='flatten'):
        """
        初始化管道
        
        参数:
            operators (list, optional): 操作符列表
            passthrough_fields (list, optional): 需要透传的字段列表
            collection_mode (str, optional): 集合处理模式，'flatten'或'nested'
        """
        pass
        
    def add(self, operator):
        """
        添加操作符到管道中
        
        参数:
            operator (Operator): 要添加的操作符
            
        返回:
            Pipeline: 返回 self 以支持链式调用
        """
        pass
        
    def process(self, json_data):
        """
        处理 JSON 数据
        
        参数:
            json_data (dict or list): 输入的 JSON 数据，可以是单个对象或列表
            
        返回:
            dict or list: 处理后的 JSON 数据
        """
        pass
        
    def set_passthrough_fields(self, fields):
        """
        设置需要透传的字段列表
        
        参数:
            fields (list or str): 字段名或字段名列表
            
        返回:
            Pipeline: 返回 self 以支持链式调用
        """
        pass
        
    def set_collection_mode(self, mode):
        """
        设置集合处理模式
        
        参数:
            mode (str): 'flatten'或'nested'
            
        返回:
            Pipeline: 返回 self 以支持链式调用
        """
        pass
```

### Executor

`Executor` 是执行器的基类，负责执行 Pipeline 处理 JSON 数据。

#### 内置执行器类型

- `SyncExecutor`：同步执行器
- `AsyncExecutor`：异步执行器
- `MultiThreadExecutor`：多线程执行器
- `MultiProcessExecutor`：多进程执行器

#### 主要方法

```python
class Executor:
    def __init__(self, pipeline):
        """
        初始化执行器
        
        参数:
            pipeline (Pipeline): 要执行的管道
        """
        pass
        
    def execute(self, json_data):
        """
        执行管道处理 JSON 数据
        
        参数:
            json_data (dict or list): 输入的 JSON 数据
            
        返回:
            dict or list: 处理后的 JSON 数据
        """
        pass
        
    def execute_all(self, json_data_list):
        """
        批量执行管道处理 JSON 数据
        
        参数:
            json_data_list (list): 输入的 JSON 数据列表
            
        返回:
            list: 处理后的 JSON 数据列表
        """
        pass
```

#### 多线程执行器示例

```python
from jsonflow.core import Pipeline, MultiThreadExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer

# 创建管道
pipeline = Pipeline([TextNormalizer()])

# 创建多线程执行器，最大工作线程数为4
executor = MultiThreadExecutor(pipeline, max_workers=4)

# 加载所有数据
json_data_list = JsonLoader("input.jsonl").load()

# 并发处理数据
results = executor.execute_all(json_data_list)

# 保存结果
JsonSaver("output.jsonl").write_all(results)
```

## IO 组件

### JsonLoader

`JsonLoader` 用于从文件或标准输入加载 JSON 数据。

#### 主要方法

```python
class JsonLoader:
    def __init__(self, source=None):
        """
        初始化 JSON 加载器
        
        参数:
            source (str, optional): 数据源，文件路径或 None 表示从 stdin 读取
        """
        pass
        
    def load(self):
        """
        加载所有 JSON 数据到列表
        
        返回:
            list: JSON 数据列表
        """
        pass
        
    def load_batch(self, batch_size=100):
        """
        批量加载指定数量的 JSON 数据
        
        参数:
            batch_size (int): 每批加载的数据量
            
        返回:
            generator: 每次返回一批 JSON 数据列表的生成器
        """
        pass
        
    def __iter__(self):
        """
        迭代器方法，逐行加载 JSON
        
        返回:
            iterator: JSON 数据迭代器
        """
        pass
```

#### 使用示例

```python
# 从文件加载 JSON 数据
loader = JsonLoader("input.jsonl")

# 逐行处理
for json_data in loader:
    print(json_data)

# 加载所有数据
all_data = loader.load()

# 批量加载数据
for batch in loader.load_batch(batch_size=100):
    print(f"Loaded batch of {len(batch)} items")
```

### JsonSaver

`JsonSaver` 用于将 JSON 数据保存到文件或标准输出。

#### 主要方法

```python
class JsonSaver:
    def __init__(self, destination=None):
        """
        初始化 JSON 保存器
        
        参数:
            destination (str, optional): 目标位置，文件路径或 None 表示输出到 stdout
        """
        pass
        
    def write(self, json_data):
        """
        写入 JSON 数据，支持单个对象或列表
        
        参数:
            json_data (dict or list): 要写入的 JSON 数据
        """
        pass
        
    def write_item(self, json_data):
        """
        写入单个 JSON 数据
        
        参数:
            json_data (dict): 要写入的单个 JSON 数据
        """
        pass
        
    def write_all(self, json_data_list):
        """
        批量写入 JSON 数据
        
        参数:
            json_data_list (list): 要写入的 JSON 数据列表
        """
        pass
```

#### 使用示例

```python
# 创建保存器
saver = JsonSaver("output.jsonl")

# 写入单个 JSON 对象
saver.write({"text": "Hello, World!"})

# 写入 JSON 列表
saver.write([{"id": 1}, {"id": 2}])

# 批量写入
json_data_list = [{"id": i} for i in range(10)]
saver.write_all(json_data_list)

# 使用上下文管理器
with JsonSaver("output.jsonl") as saver:
    for i in range(10):
        saver.write({"id": i})
```

## 操作符

### 基础操作符

#### TextNormalizer

文本规范化操作符，用于处理 JSON 中的文本字段。

```python
from jsonflow.operators.json_ops import TextNormalizer

# 创建文本规范化操作符
normalizer = TextNormalizer(
    field="text",                    # 要处理的字段
    strip=True,                      # 是否去除首尾空白
    lower=False,                     # 是否转为小写
    replace_spaces=False,            # 是否替换连续空白
    remove_punctuation=False,        # 是否移除标点
    max_length=None,                 # 最大长度限制
    output_field=None                # 输出字段，默认覆盖原字段
)

# 处理 JSON 数据
result = normalizer.process({"text": "  Hello, World!  "})
# 结果: {"text": "Hello, World!"}
```

#### JsonFilter

JSON 过滤操作符，用于根据条件过滤 JSON 数据。

```python
from jsonflow.operators.json_ops import JsonFilter

# 创建 JSON 过滤操作符
json_filter = JsonFilter(
    condition=lambda x: "text" in x and len(x["text"]) > 10,  # 过滤条件
    exclude=False                                             # True 为排除匹配项，False 为保留匹配项
)

# 处理 JSON 数据
data = {"text": "Hello"}
result = json_filter.process(data)
# 结果: None (因为条件不满足)

data = {"text": "Hello, World!"}
result = json_filter.process(data)
# 结果: {"text": "Hello, World!"} (条件满足)
```

#### JsonTransformer

JSON 转换操作符，用于对 JSON 数据进行结构转换。

```python
from jsonflow.operators.json_ops import JsonTransformer

# 创建 JSON 转换操作符
transformer = JsonTransformer(
    transform_function=lambda x: {
        "content": x.get("text", ""),
        "word_count": len(x.get("text", "").split())
    }
)

# 处理 JSON 数据
result = transformer.process({"text": "Hello, World!"})
# 结果: {"content": "Hello, World!", "word_count": 2}
```

### 字段操作符

#### JsonFieldSelector

JSON 字段选择操作符，用于选择指定的字段。

```python
from jsonflow.operators.json_ops import JsonFieldSelector

# 创建字段选择操作符
selector = JsonFieldSelector(
    fields=["id", "text"],       # 要选择的字段列表
    keep_missing=False           # 是否保留缺失字段
)

# 处理 JSON 数据
result = selector.process({"id": 1, "text": "Hello", "extra": "value"})
# 结果: {"id": 1, "text": "Hello"}
```

#### JsonPathExtractor

JSON Path 提取操作符，使用 JSONPath 表达式提取数据。

```python
from jsonflow.operators.json_ops import JsonPathExtractor

# 创建 JSON Path 提取操作符
extractor = JsonPathExtractor(
    path_map={
        "title": "$.book.title",          # 将 $.book.title 提取到 title 字段
        "authors": "$.book.authors[*]"    # 将 $.book.authors 数组提取到 authors 字段
    },
    default_value=None                    # 找不到路径时的默认值
)

# 处理 JSON 数据
data = {
    "book": {
        "title": "JSONFlow Guide",
        "authors": ["Alice", "Bob"]
    }
}
result = extractor.process(data)
# 结果: {"title": "JSONFlow Guide", "authors": ["Alice", "Bob"]}
```

#### JsonPathUpdater

JSON Path 更新操作符，使用 JSONPath 表达式更新数据。

```python
from jsonflow.operators.json_ops import JsonPathUpdater

# 创建 JSON Path 更新操作符
updater = JsonPathUpdater(
    updates=[
        {
            "path": "$.book.title",         # 要更新的路径
            "value": "Updated Title"        # 新值
        },
        {
            "path": "$.book.year",
            "value": 2023
        }
    ]
)

# 处理 JSON 数据
data = {
    "book": {
        "title": "Old Title"
    }
}
result = updater.process(data)
# 结果: {"book": {"title": "Updated Title", "year": 2023}}
```

### 表达式操作符

#### JsonExpressionOperator

JSON 表达式操作符，使用 Python 表达式处理 JSON 数据。

```python
from jsonflow.operators.json_ops import JsonExpressionOperator

# 创建 JSON 表达式操作符
expr_op = JsonExpressionOperator(
    expression="{'id': input.get('id'), 'length': len(input.get('text', ''))}",  # Python 表达式
    input_var_name="input"  # 输入数据在表达式中的变量名
)

# 处理 JSON 数据
result = expr_op.process({"id": 1, "text": "Hello, World!"})
# 结果: {"id": 1, "length": 13}
```

#### JsonFieldMapper

JSON 字段映射操作符，用于映射字段名和转换字段值。

```python
from jsonflow.operators.json_ops import JsonFieldMapper

# 创建字段映射操作符
mapper = JsonFieldMapper(
    mappings={
        "text": lambda v: v.upper(),                # 将 text 字段转为大写
        "count": lambda v: len(v) if v else 0,      # 计算 count 字段长度
        "new_field": lambda _, obj: obj.get("id")   # 创建新字段，值为 id 字段的值
    },
    copy_unmapped=True                              # 是否保留未映射的字段
)

# 处理 JSON 数据
result = mapper.process({"id": 1, "text": "hello", "count": "123"})
# 结果: {"id": 1, "text": "HELLO", "count": 3, "new_field": 1}
```

### 系统字段操作符

#### IdAdder

添加唯一 ID 的操作符。

```python
from jsonflow.operators.json_ops import IdAdder

# 创建 ID 添加操作符
id_adder = IdAdder(
    field_name="id",      # ID 字段名
    override=False        # 是否覆盖已存在的字段
)

# 处理 JSON 数据
result = id_adder.process({"text": "Hello"})
# 结果: {"text": "Hello", "id": "f7f8e132-3f98-4b36-a3e0-e569d4d8f789"}
```

#### TimestampAdder

添加时间戳的操作符。

```python
from jsonflow.operators.json_ops import TimestampAdder

# 创建时间戳添加操作符
ts_adder = TimestampAdder(
    field_name="timestamp",  # 时间戳字段名
    override=False           # 是否覆盖已存在的字段
)

# 处理 JSON 数据
result = ts_adder.process({"text": "Hello"})
# 结果: {"text": "Hello", "timestamp": 1623456789}
```

### 集合操作符

#### JsonSplitter

JSON 拆分操作符，将单个 JSON 拆分为多个 JSON。

```python
from jsonflow.operators.json_ops import JsonSplitter

# 创建 JSON 拆分操作符
splitter = JsonSplitter(
    array_field="items",                # 要拆分的数组字段
    keep_parent_fields=True,            # 是否保留父级字段
    output_field="item"                 # 单个元素的输出字段名
)

# 处理 JSON 数据
data = {
    "id": "parent",
    "items": ["a", "b", "c"]
}
result = splitter.process(data)
# 结果: [
#   {"id": "parent", "item": "a"},
#   {"id": "parent", "item": "b"},
#   {"id": "parent", "item": "c"}
# ]
```

#### JsonAggregator

JSON 聚合操作符，将多个 JSON 合并为单个 JSON。

```python
from jsonflow.operators.json_ops import JsonAggregator

# 创建 JSON 聚合操作符
aggregator = JsonAggregator(
    key_field="id",                  # 分组依据的字段
    items_field="items",             # 存放聚合项目的字段名
    aggregate_fields=["count"],      # 需要聚合的字段
    aggregate_function=sum           # 聚合函数
)

# 处理 JSON 列表
data = [
    {"id": "group1", "value": "a", "count": 1},
    {"id": "group1", "value": "b", "count": 2},
    {"id": "group2", "value": "c", "count": 3}
]
result = aggregator.process(data)
# 结果: [
#   {"id": "group1", "items": [{"value": "a", "count": 1}, {"value": "b", "count": 2}], "count": 3},
#   {"id": "group2", "items": [{"value": "c", "count": 3}], "count": 3}
# ]
```

### 模型操作符

#### ModelInvoker

模型调用操作符，用于调用大语言模型。

```python
from jsonflow.operators.model import ModelInvoker

# 创建模型调用操作符
model_invoker = ModelInvoker(
    model="gpt-3.5-turbo",                   # 模型名称
    input_field="prompt",                     # 输入字段
    output_field="response",                  # 输出字段
    system_message="You are an assistant.",   # 系统消息
    max_tokens=100,                           # 最大生成 token 数
    temperature=0.7                           # 温度参数
)

# 处理 JSON 数据
result = model_invoker.process({"prompt": "Tell me a joke."})
# 结果: {"prompt": "Tell me a joke.", "response": "Why don't scientists trust atoms? Because they make up everything!"}
```

## 工具组件

### 系统字段工具

`SystemField` 类提供了添加和管理系统级字段的工具。

```python
from jsonflow.utils import SystemField

# 添加唯一ID
data = SystemField.add_id({"text": "Hello"})
# 结果: {"text": "Hello", "id": "f7f8e132-3f98-4b36-a3e0-e569d4d8f789"}

# 添加时间戳
data = SystemField.add_timestamp(data)
# 结果: {"text": "Hello", "id": "...", "timestamp": 1623456789}

# 添加日期时间
data = SystemField.add_datetime(data, format="%Y-%m-%d")
# 结果: {"text": "Hello", "id": "...", "timestamp": 1623456789, "datetime": "2023-06-12"}

# 添加自定义字段
data = SystemField.add_custom_field(data, "version", "1.0")
# 结果: {"text": "Hello", "id": "...", "timestamp": 1623456789, "datetime": "2023-06-12", "version": "1.0"}

# 移除字段
data = SystemField.remove_field(data, "timestamp")
# 结果: {"text": "Hello", "id": "...", "datetime": "2023-06-12", "version": "1.0"}
```

### BOS 工具

`BosHelper` 类提供了与百度对象存储 (BOS) 的交互功能。

```python
from jsonflow.utils import BosHelper

# 初始化 BOS 工具
bos = BosHelper(
    access_key="your_access_key",
    secret_key="your_secret_key",
    endpoint="bj.bcebos.com",
    bucket="your_bucket_name"
)

# 上传文件
bos.upload_file("local_file.txt", "remote/path/file.txt")

# 下载文件
bos.download_file("remote/path/file.txt", "local_downloaded.txt")

# 并发上传目录
bos.upload_directory("local_dir", "remote/dir", max_workers=4)

# 并发下载目录
bos.download_directory("remote/dir", "local_dir", max_workers=4)

# 检查文件是否存在
exists = bos.file_exists("remote/path/file.txt")

# 删除文件
bos.delete_file("remote/path/file.txt")
```

## 高级功能

### 字段透传

字段透传允许在整个 Pipeline 中自动传递特定字段，而不需要每个操作符手动处理这些字段。

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer, JsonFieldMapper

# 创建管道并设置透传字段
pipeline = Pipeline()
pipeline.set_passthrough_fields(["id", "metadata"])

# 添加操作符
pipeline.add(TextNormalizer(field="text"))
pipeline.add(JsonFieldMapper(
    mappings={"text": lambda v: v.upper()}
))

# 处理 JSON 数据
data = {
    "id": "12345",
    "metadata": {"source": "user"},
    "text": "Hello, World!"
}
result = pipeline.process(data)
# 结果: {
#   "id": "12345",
#   "metadata": {"source": "user"},
#   "text": "HELLO, WORLD!"
# }
```

### 集合处理模式

JSONFlow 支持两种集合处理模式：展平模式和嵌套模式。

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import JsonSplitter, TextNormalizer

# 创建拆分操作符
splitter = JsonSplitter(array_field="items")

# 创建文本规范化操作符
normalizer = TextNormalizer(field="item")

# 展平模式（默认）：操作符输出的列表会被展平处理
pipeline_flatten = Pipeline([splitter, normalizer], collection_mode='flatten')

# 嵌套模式：保持列表的嵌套结构
pipeline_nested = Pipeline([splitter, normalizer], collection_mode='nested')

# 示例数据
data = {"items": ["  A  ", "  B  ", "  C  "]}

# 展平模式处理
result_flatten = pipeline_flatten.process(data)
# 结果: [{"item": "A"}, {"item": "B"}, {"item": "C"}]

# 嵌套模式处理
result_nested = pipeline_nested.process(data)
# 结果: [{"item": "A"}, {"item": "B"}, {"item": "C"}]
# 注：在此例中两种模式结果相同，但对于更复杂的管道，结果可能会不同
```

### 并发处理

并发处理可以显著提高大批量 JSON 数据的处理效率。

```python
from jsonflow.core import Pipeline, MultiThreadExecutor, MultiProcessExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer

# 创建管道
pipeline = Pipeline([TextNormalizer(field="text")])

# 创建多线程执行器
thread_executor = MultiThreadExecutor(pipeline, max_workers=4)

# 创建多进程执行器
process_executor = MultiProcessExecutor(pipeline, max_workers=4)

# 加载所有数据
json_data_list = JsonLoader("input.jsonl").load()

# 使用多线程执行器处理数据
thread_results = thread_executor.execute_all(json_data_list)

# 使用多进程执行器处理数据
process_results = process_executor.execute_all(json_data_list)

# 保存结果
JsonSaver("thread_output.jsonl").write_all(thread_results)
JsonSaver("process_output.jsonl").write_all(process_results)
```

## 自定义开发

### 自定义操作符

通过继承 `Operator` 基类或其子类，可以创建自定义操作符。

```python
from jsonflow.core import Operator

class MyCustomOperator(Operator):
    def __init__(self, custom_param, name=None, description=None):
        super().__init__(name, description)
        self.custom_param = custom_param
        
    def process_item(self, json_data):
        # 实现自定义逻辑
        result = json_data.copy()
        result["custom_field"] = self.custom_param
        return result

# 使用自定义操作符
custom_op = MyCustomOperator(custom_param="value")
result = custom_op.process({"text": "Hello"})
# 结果: {"text": "Hello", "custom_field": "value"}
```

### 自定义执行器

通过继承 `Executor` 基类，可以创建自定义执行器。

```python
from jsonflow.core import Executor
import asyncio

class MyAsyncExecutor(Executor):
    def __init__(self, pipeline, max_concurrent=10):
        super().__init__(pipeline)
        self.max_concurrent = max_concurrent
        
    async def _execute_async(self, json_data):
        return self.pipeline.process(json_data)
        
    async def _execute_all_async(self, json_data_list):
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_with_semaphore(data):
            async with semaphore:
                return await self._execute_async(data)
        
        tasks = [process_with_semaphore(data) for data in json_data_list]
        return await asyncio.gather(*tasks)
    
    def execute_all(self, json_data_list):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._execute_all_async(json_data_list))

# 使用自定义执行器
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer

pipeline = Pipeline([TextNormalizer(field="text")])
executor = MyAsyncExecutor(pipeline, max_concurrent=5)

json_data_list = [{"text": f"Text {i}"} for i in range(10)]
results = executor.execute_all(json_data_list)
```

## 完整示例

### 基本处理流程

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonFieldMapper, IdAdder
from jsonflow.operators.model import ModelInvoker

# 创建管道
pipeline = Pipeline()

# 设置透传字段
pipeline.set_passthrough_fields(["id", "metadata"])

# 添加操作符
pipeline.add(IdAdder(field_name="id"))  # 添加唯一ID
pipeline.add(TextNormalizer(field="text", strip=True))  # 文本规范化
pipeline.add(JsonFieldMapper(mappings={
    "text_length": lambda _, obj: len(obj.get("text", ""))
}))  # 添加文本长度字段
pipeline.add(ModelInvoker(
    model="gpt-3.5-turbo",
    input_field="text",
    output_field="response",
    system_message="You are a helpful assistant."
))  # 调用大语言模型

# 加载和处理数据
loader = JsonLoader("input.jsonl")
saver = JsonSaver("output.jsonl")

for json_data in loader:
    result = pipeline.process(json_data)
    saver.write(result)

print("处理完成！")
```

### 并发处理大规模数据

```python
from jsonflow.core import Pipeline, MultiProcessExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonFilter, JsonFieldSelector
from jsonflow.utils import SystemField

# 创建管道
pipeline = Pipeline([
    # 文本规范化
    TextNormalizer(field="text", strip=True, lower=True),
    
    # 过滤掉文本长度小于10的数据
    JsonFilter(condition=lambda x: len(x.get("text", "")) >= 10),
    
    # 选择需要的字段
    JsonFieldSelector(fields=["id", "text", "metadata"])
])

# 创建多进程执行器
executor = MultiProcessExecutor(pipeline, max_workers=8)

# 批量加载数据
loader = JsonLoader("large_input.jsonl")
all_data = []

# 每次加载1000条数据并处理
for batch in loader.load_batch(batch_size=1000):
    # 添加系统字段
    batch = [SystemField.add_timestamp(item) for item in batch]
    
    # 并发处理批次数据
    results = executor.execute_all(batch)
    
    # 过滤掉None结果（被JsonFilter过滤掉的数据）
    valid_results = [r for r in results if r is not None]
    all_data.extend(valid_results)

# 保存所有处理结果
saver = JsonSaver("large_output.jsonl")
saver.write_all(all_data)

print(f"处理完成！共处理 {len(all_data)} 条有效数据。")
``` 