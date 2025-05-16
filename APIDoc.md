# JSONFlow API 文档

JSONFlow 是一个专为 JSON 数据处理而设计的高效库，支持构建灵活的数据处理流水线。它允许通过组合不同的操作符 (Operators) 来处理 JSON 数据，并支持并发执行提高性能。

## 目录

- [JSONFlow API 文档](#jsonflow-api-文档)
  - [目录](#目录)
  - [基础概念](#基础概念)
  - [核心组件](#核心组件)
    - [Operator](#operator)
    - [Pipeline](#pipeline)
    - [Executor](#executor)
  - [IO 组件](#io-组件)
    - [JsonLoader](#jsonloader)
    - [JsonSaver](#jsonsaver)
  - [操作符详解](#操作符详解)
    - [文本操作符](#文本操作符)
      - [TextNormalizer](#textnormalizer)
    - [JSON 过滤操作符](#json-过滤操作符)
      - [JsonFilter](#jsonfilter)
    - [JSON 转换操作符](#json-转换操作符)
      - [JsonTransformer](#jsontransformer)
    - [字段操作符](#字段操作符)
      - [JsonFieldSelector](#jsonfieldselector)
      - [JsonPathExtractor](#jsonpathextractor)
      - [JsonFieldMapper](#jsonfieldmapper)
    - [系统字段操作符](#系统字段操作符)
      - [IdAdder](#idadder)
      - [TimestampAdder](#timestampadder)
    - [表达式操作符](#表达式操作符)
      - [JsonExpressionOperator](#jsonexpressionoperator)
  - [工具组件](#工具组件)
    - [SystemField 工具](#systemfield-工具)
    - [多种执行模式](#多种执行模式)
      - [同步执行](#同步执行)
      - [多线程执行](#多线程执行)
      - [多进程执行](#多进程执行)
  - [综合示例](#综合示例)
    - [文本分析流水线](#文本分析流水线)
    - [数据转换流水线](#数据转换流水线)
  - [更多资源](#更多资源)
  - [模型操作符](#模型操作符)
    - [ModelInvoker](#modelinvoker)
- [设置 API 密钥（也可通过环境变量设置）](#设置-api-密钥也可通过环境变量设置)
- [基本用法：使用指定字段作为提示](#基本用法使用指定字段作为提示)
- [处理单个 JSON 对象](#处理单个-json-对象)
- [输出:](#输出)
- [{](#)
- ["id": "q1",](#id-q1)
- ["question": "什么是 JSONFlow？",](#question-什么是-jsonflow)
- ["answer": "JSONFlow 是一个专为 JSON 数据处理而设计的高效库，它允许用户通过组合不同的操作符来构建灵活的数据处理流水线。它支持从文件或标准输入加载 JSON 数据，并提供各种操作符对数据进行转换、过滤和处理。JSONFlow 还支持并发执行以提高处理大量数据的效率。"](#answer-jsonflow-是一个专为-json-数据处理而设计的高效库它允许用户通过组合不同的操作符来构建灵活的数据处理流水线它支持从文件或标准输入加载-json-数据并提供各种操作符对数据进行转换过滤和处理jsonflow-还支持并发执行以提高处理大量数据的效率)
- [}](#-1)
- [使用系统提示和提示模板](#使用系统提示和提示模板)
- [输出:](#输出-1)
- [{](#-2)
- ["document\_type": "新闻文章",](#document_type-新闻文章)
- ["text": "今日，科研人员宣布了一项突破性的发现，可能彻底改变我们对气候变化的理解。这项研究表明，通过特定的碳捕获技术，二氧化碳可以更高效地从大气中移除。研究团队表示，如果全球范围内部署这项技术，温室气体浓度可能在未来十年内显著下降。然而，专家指出实施该技术面临资金和基础设施挑战。",](#text-今日科研人员宣布了一项突破性的发现可能彻底改变我们对气候变化的理解这项研究表明通过特定的碳捕获技术二氧化碳可以更高效地从大气中移除研究团队表示如果全球范围内部署这项技术温室气体浓度可能在未来十年内显著下降然而专家指出实施该技术面临资金和基础设施挑战)
- ["metadata": {](#metadata-)
- ["source": "科技日报",](#source-科技日报)
- ["date": "2023-06-15"](#date-2023-06-15)
- [},](#-3)
- ["summary": "科研人员发现一种高效碳捕获技术，可能显著降低大气中的二氧化碳浓度，从而改变气候变化趋势。若全球部署，未来十年温室气体浓度有望大幅下降，但实施面临资金和基础设施方面的挑战。"](#summary-科研人员发现一种高效碳捕获技术可能显著降低大气中的二氧化碳浓度从而改变气候变化趋势若全球部署未来十年温室气体浓度有望大幅下降但实施面临资金和基础设施方面的挑战)
- [}](#-4)
- [批量处理多个问题](#批量处理多个问题)
- [使用完整配置的例子](#使用完整配置的例子)
- [输出内容将包含详细的文本分析结果](#输出内容将包含详细的文本分析结果)

## 基础概念

JSONFlow 的核心理念是通过可组合的操作符构建数据处理流水线：

1. **Operator (操作符)**: 处理单个 JSON 对象或 JSON 对象列表的基本单元
2. **Pipeline (管道)**: 操作符的有序集合，负责协调执行顺序和数据流
3. **Executor (执行器)**: 负责执行 Pipeline，支持同步或并发执行
4. **JsonLoader/JsonSaver**: 输入输出组件，管理 JSON 数据的加载和保存

## 核心组件

### Operator

`Operator` 是所有操作符的基类，定义了处理 JSON 数据的基本接口。

```python
from jsonflow.core import Operator

class CustomOperator(Operator):
    def __init__(self, name=None, description=None):
        super().__init__(name or "CustomOperator", 
                        description or "My custom operator")
        
    def process_item(self, json_data):
        # 处理单个 JSON 对象
        result = json_data.copy()
        result["custom_field"] = "Custom value"
        return result

# 使用自定义操作符
op = CustomOperator()
result = op.process({"id": 123})
print(result)  # 输出: {"id": 123, "custom_field": "Custom value"}
```

### Pipeline

`Pipeline` 管理多个操作符的执行顺序，处理数据在操作符间的流动。

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer, JsonFilter

# 创建操作符
text_normalizer = TextNormalizer(text_fields=["text"], strip=True)
json_filter = JsonFilter(include_fields=["id", "text"])

# 创建管道并添加操作符
pipeline = Pipeline()
pipeline.add(text_normalizer)
pipeline.add(json_filter)

# 处理数据
data = {"id": 123, "text": "  Hello World  ", "extra": "not needed"}
result = pipeline.process(data)
print(result)  # 输出: {"id": 123, "text": "Hello World"}
```

### Executor

`Executor` 负责执行 Pipeline，支持多种执行模式。

```python
from jsonflow.core import Pipeline, MultiThreadExecutor
from jsonflow.operators.json_ops import TextNormalizer

# 创建管道
pipeline = Pipeline([TextNormalizer(text_fields=["text"])])

# 创建多线程执行器
executor = MultiThreadExecutor(pipeline, max_workers=4)

# 并发处理多个 JSON 对象
data_list = [
    {"id": 1, "text": "  Text one  "},
    {"id": 2, "text": "  Text two  "},
    {"id": 3, "text": "  Text three  "}
]
results = executor.execute_all(data_list)
for result in results:
    print(result)
```

## IO 组件

### JsonLoader

`JsonLoader` 用于从文件或标准输入加载 JSON 数据。

```python
from jsonflow.io import JsonLoader

# 从文件加载
loader = JsonLoader("input.jsonl")

# 逐行处理
for json_data in loader:
    print(json_data)

# 加载所有数据
all_data = loader.load()

# 批量加载
for batch in loader.load_batch(batch_size=100):
    print(f"Loaded batch with {len(batch)} items")
```

### JsonSaver

`JsonSaver` 用于将 JSON 数据保存到文件或标准输出。

```python
from jsonflow.io import JsonSaver

# 创建保存器
saver = JsonSaver("output.jsonl")

# 保存单个 JSON 对象
saver.write({"id": 1, "text": "Hello"})

# 保存 JSON 对象列表
saver.write_all([
    {"id": 2, "text": "World"},
    {"id": 3, "text": "!"}
])

# 使用上下文管理器
with JsonSaver("another_output.jsonl") as s:
    s.write({"status": "complete"})
```

## 操作符详解

### 文本操作符

#### TextNormalizer

文本规范化操作符，处理 JSON 中的文本字段。

**输入**: 包含文本字段的 JSON 对象  
**输出**: 文本字段已规范化的 JSON 对象

**参数**:
- `text_fields` (List[str], 可选): 要处理的文本字段列表，为 None 时处理所有字符串字段
- `normalize_func` (Callable, 可选): 自定义文本规范化函数
- `strip` (bool): 是否去除首尾空白，默认为 True
- `lower_case` (bool): 是否转换为小写，默认为 False  
- `upper_case` (bool): 是否转换为大写，默认为 False
- `remove_extra_spaces` (bool): 是否替换连续空白为单个空格，默认为 True

**示例**:

```python
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver

# 创建文本规范化操作符
normalizer = TextNormalizer(
    text_fields=["title", "content"],
    strip=True,
    lower_case=True,
    remove_extra_spaces=True
)

# 在管道中使用
pipeline = Pipeline([normalizer])

# 示例数据
data = {
    "id": 1,
    "title": "  Hello   World  ",
    "content": "This   is  a    test",
    "count": 42
}

# 处理数据
result = pipeline.process(data)
print(result)
# 输出:
# {
#   "id": 1,
#   "title": "hello world",
#   "content": "this is a test",
#   "count": 42
# }

# 完整处理流程示例
loader = JsonLoader("input.jsonl")
saver = JsonSaver("output.jsonl")

for item in loader:
    processed = normalizer.process(item)
    saver.write(processed)
```

### JSON 过滤操作符

#### JsonFilter

根据条件过滤 JSON 数据，可保留或排除特定字段。

**输入**: JSON 对象  
**输出**: 过滤后的 JSON 对象，如果对象不符合过滤条件则返回空对象

**参数**:
- `include_fields` (List[str], 可选): 要保留的字段列表
- `exclude_fields` (List[str], 可选): 要排除的字段列表
- `filter_func` (Callable, 可选): 自定义过滤函数，接收 JSON 对象返回布尔值

**示例**:

```python
from jsonflow.operators.json_ops import JsonFilter
from jsonflow.core import Pipeline

# 创建只保留特定字段的过滤器
include_filter = JsonFilter.include_only(["id", "text"])

# 创建排除特定字段的过滤器
exclude_filter = JsonFilter.exclude(["debug_info", "metadata"])

# 创建使用自定义函数的过滤器
custom_filter = JsonFilter.with_predicate(
    lambda x: "text" in x and len(x["text"]) > 10
)

# 在管道中组合过滤器
pipeline = Pipeline([include_filter, custom_filter])

# 示例数据
data1 = {"id": 1, "text": "Short", "debug_info": "test"}
data2 = {"id": 2, "text": "This is a longer text", "debug_info": "test"}

# 处理数据
result1 = pipeline.process(data1)
result2 = pipeline.process(data2)

print(result1)  # 输出: {}（不符合长度条件，被过滤掉）
print(result2)  # 输出: {"id": 2, "text": "This is a longer text"}

# 链式调用示例
data = [
    {"id": 1, "text": "Hello", "debug": True, "size": 10},
    {"id": 2, "text": "This is a long enough text", "debug": False, "size": 20},
    {"id": 3, "text": "Another long text for testing", "debug": True, "size": 30}
]

pipeline = Pipeline([
    JsonFilter(exclude_fields=["debug"]),
    JsonFilter(filter_func=lambda x: x.get("size", 0) > 15),
    JsonFilter(include_fields=["id", "text"])
])

for item in data:
    result = pipeline.process(item)
    if result:  # 只处理非空结果
        print(result)
# 输出:
# {"id": 2, "text": "This is a long enough text"}
# {"id": 3, "text": "Another long text for testing"}
```

### JSON 转换操作符

#### JsonTransformer

对 JSON 数据进行结构转换的操作符。

**输入**: JSON 对象  
**输出**: 转换后的 JSON 对象

**参数**:
- `transform_function` (Callable): 转换函数，接收原 JSON 对象，返回新 JSON 对象

**示例**:

```python
from jsonflow.operators.json_ops import JsonTransformer
from jsonflow.core import Pipeline

# 创建转换函数
def transform_data(json_obj):
    return {
        "document": {
            "id": json_obj.get("id"),
            "content": json_obj.get("text", ""),
            "stats": {
                "word_count": len(json_obj.get("text", "").split()),
                "processed_at": "2023-01-01"
            }
        }
    }

# 创建转换操作符
transformer = JsonTransformer(transform_function=transform_data)

# 示例数据
data = {"id": 123, "text": "Hello world from JSONFlow", "extra": "value"}

# 处理数据
result = transformer.process(data)
print(result)
# 输出:
# {
#   "document": {
#     "id": 123,
#     "content": "Hello world from JSONFlow",
#     "stats": {
#       "word_count": 4,
#       "processed_at": "2023-01-01"
#     }
#   }
# }

# 在管道中使用转换器
pipeline = Pipeline([
    JsonTransformer(lambda x: {"text": x.get("content", ""), "length": len(x.get("content", ""))}),
    JsonTransformer(lambda x: {"text": x["text"].upper(), "length": x["length"]})
])

data = {"content": "hello world"}
result = pipeline.process(data)
print(result)  # 输出: {"text": "HELLO WORLD", "length": 11}
```

### 字段操作符

#### JsonFieldSelector

选择或保留 JSON 对象中的特定字段。

**输入**: JSON 对象  
**输出**: 只包含选定字段的 JSON 对象

**参数**:
- `fields` (List[str]): 要选择的字段列表
- `keep_missing` (bool, 可选): 是否保留缺失字段，默认为 False

**示例**:

```python
from jsonflow.operators.json_ops import JsonFieldSelector
from jsonflow.core import Pipeline

# 创建字段选择操作符
selector = JsonFieldSelector(
    fields=["id", "title", "content"],
    keep_missing=False
)

# 示例数据
data = {
    "id": "doc-123",
    "title": "Sample Document",
    "content": "This is the content",
    "author": "John Doe",
    "created_at": "2023-01-01",
    "views": 42
}

# 处理数据
result = selector.process(data)
print(result)
# 输出:
# {
#   "id": "doc-123",
#   "title": "Sample Document",
#   "content": "This is the content"
# }

# 在管道中使用
pipeline = Pipeline([
    # 其他操作符
    JsonFieldSelector(fields=["id", "summary"]),
    # 后续操作符
])

# 批量处理示例
data_list = [
    {"id": 1, "title": "Item 1", "description": "Desc 1", "category": "A"},
    {"id": 2, "title": "Item 2", "description": "Desc 2", "category": "B"},
    {"id": 3, "title": "Item 3", "description": "Desc 3", "category": "A"}
]

selected_data = []
selector = JsonFieldSelector(fields=["id", "title"])

for item in data_list:
    selected_data.append(selector.process(item))

print(selected_data)
# 输出: [
#   {"id": 1, "title": "Item 1"},
#   {"id": 2, "title": "Item 2"},
#   {"id": 3, "title": "Item 3"}
# ]
```

#### JsonPathExtractor

使用 JSONPath 表达式从 JSON 对象中提取数据。

**输入**: JSON 对象  
**输出**: 包含提取值的 JSON 对象

**参数**:
- `path_map` (Dict[str, str]): 字段名到 JSONPath 表达式的映射
- `default_value` (Any, 可选): 当路径不存在时的默认值

**示例**:

```python
from jsonflow.operators.json_ops import JsonPathExtractor
from jsonflow.core import Pipeline

# 创建 JSONPath 提取操作符
extractor = JsonPathExtractor(
    path_map={
        "title": "$.metadata.title",
        "authors": "$.metadata.authors[*].name",
        "first_section": "$.content.sections[0].text"
    },
    default_value="N/A"
)

# 示例数据
data = {
    "id": "doc-123",
    "metadata": {
        "title": "JSONFlow Guide",
        "authors": [
            {"name": "Alice Smith", "role": "lead"},
            {"name": "Bob Jones", "role": "contributor"}
        ],
        "version": "1.0"
    },
    "content": {
        "sections": [
            {"title": "Introduction", "text": "This is an introduction to JSONFlow."},
            {"title": "Getting Started", "text": "Install the package using pip."}
        ]
    }
}

# 处理数据
result = extractor.process(data)
print(result)
# 输出:
# {
#   "title": "JSONFlow Guide",
#   "authors": ["Alice Smith", "Bob Jones"],
#   "first_section": "This is an introduction to JSONFlow."
# }

# 在管道中使用
pipeline = Pipeline([
    JsonPathExtractor({
        "doc_title": "$.title",
        "summary": "$.abstract.text"
    }),
    # 后续处理
])

# 处理多个文档
documents = [
    {"title": "Doc 1", "abstract": {"text": "Summary 1"}, "body": "..."},
    {"title": "Doc 2", "abstract": {"text": "Summary 2"}, "body": "..."}
]

for doc in documents:
    result = pipeline.process(doc)
    print(result)
# 输出:
# {"doc_title": "Doc 1", "summary": "Summary 1"}
# {"doc_title": "Doc 2", "summary": "Summary 2"}
```

#### JsonFieldMapper

映射和转换 JSON 对象中的字段值。

**输入**: JSON 对象  
**输出**: 字段已转换的 JSON 对象

**参数**:
- `mappings` (Dict[str, Callable]): 字段名到转换函数的映射
- `copy_unmapped` (bool, 可选): 是否保留未映射字段，默认为 True

**示例**:

```python
from jsonflow.operators.json_ops import JsonFieldMapper
from jsonflow.core import Pipeline

# 创建字段映射操作符
mapper = JsonFieldMapper(
    mappings={
        "title": lambda v: v.upper() if v else "",
        "word_count": lambda v, obj: len(obj.get("content", "").split()),
        "is_long": lambda v, obj: len(obj.get("content", "").split()) > 100,
        "summary": lambda v: v[:100] + "..." if len(v) > 100 else v
    },
    copy_unmapped=True
)

# 示例数据
data = {
    "id": "article-123",
    "title": "Introduction to JSONFlow",
    "content": "This is a sample article about JSONFlow. " * 10,
    "summary": "A very long summary that needs to be truncated."
}

# 处理数据
result = mapper.process(data)
print(result)
# 输出:
# {
#   "id": "article-123",
#   "title": "INTRODUCTION TO JSONFLOW",
#   "content": "This is a sample article about JSONFlow. " * 10,
#   "word_count": 70,
#   "is_long": False,
#   "summary": "A very long summary that needs to be truncated."
# }

# 在管道中使用
pipeline = Pipeline([
    # 预处理
    JsonFieldMapper(mappings={
        "text": lambda v: v.strip() if v else "",
        "length": lambda _, obj: len(obj.get("text", ""))
    }),
    # 后续处理
])

# 批量处理
data_list = [
    {"id": 1, "text": "  Hello  "},
    {"id": 2, "text": "  World  "},
    {"id": 3, "text": "  JSONFlow  "}
]

for item in data_list:
    result = pipeline.process(item)
    print(result)
# 输出:
# {"id": 1, "text": "Hello", "length": 5}
# {"id": 2, "text": "World", "length": 5}
# {"id": 3, "text": "JSONFlow", "length": 8}
```

### 系统字段操作符

#### IdAdder

向 JSON 对象添加唯一 ID。

**输入**: JSON 对象  
**输出**: 添加了 ID 字段的 JSON 对象

**参数**:
- `field_name` (str, 可选): ID 字段名，默认为 "id"
- `id_generator` (Callable, 可选): 自定义 ID 生成函数
- `override` (bool, 可选): 是否覆盖已存在的 ID 字段，默认为 False

**示例**:

```python
from jsonflow.operators.json_ops import IdAdder
from jsonflow.core import Pipeline
import uuid

# 创建 ID 添加操作符
id_adder = IdAdder(
    field_name="document_id",
    override=False
)

# 使用自定义 ID 生成器
custom_id_adder = IdAdder(
    field_name="id",
    id_generator=lambda: f"doc-{uuid.uuid4().hex[:8]}",
    override=True
)

# 示例数据
data = {"title": "Sample Document"}
data_with_id = {"id": "old-id", "title": "Another Document"}

# 处理数据
result1 = id_adder.process(data)
result2 = custom_id_adder.process(data_with_id)

print(result1)
# 输出: {"title": "Sample Document", "document_id": "550e8400-e29b-41d4-a716-446655440000"}

print(result2)
# 输出: {"id": "doc-a1b2c3d4", "title": "Another Document"}

# 在管道中使用
pipeline = Pipeline([
    IdAdder(),
    # 其他操作符
])

# 批量处理
documents = [
    {"title": "Doc 1"},
    {"title": "Doc 2"},
    {"title": "Doc 3"}
]

for doc in documents:
    result = pipeline.process(doc)
    print(result)
# 输出:
# {"title": "Doc 1", "id": "550e8400-e29b-41d4-a716-446655440000"}
# {"title": "Doc 2", "id": "550e8400-e29b-41d4-a716-446655440001"}
# {"title": "Doc 3", "id": "550e8400-e29b-41d4-a716-446655440002"}
```

#### TimestampAdder

向 JSON 对象添加时间戳。

**输入**: JSON 对象  
**输出**: 添加了时间戳字段的 JSON 对象

**参数**:
- `field_name` (str, 可选): 时间戳字段名，默认为 "timestamp"
- `override` (bool, 可选): 是否覆盖已存在的字段，默认为 False
- `use_iso_format` (bool, 可选): 是否使用 ISO 格式而不是 UNIX 时间戳，默认为 False

**示例**:

```python
from jsonflow.operators.json_ops import TimestampAdder
from jsonflow.core import Pipeline

# 创建时间戳添加操作符
ts_adder = TimestampAdder(
    field_name="processed_at",
    override=False
)

# 使用 ISO 格式
iso_ts_adder = TimestampAdder(
    field_name="timestamp",
    use_iso_format=True,
    override=True
)

# 示例数据
data = {"title": "Sample Document"}
data_with_ts = {"timestamp": "old-timestamp", "title": "Another Document"}

# 处理数据
result1 = ts_adder.process(data)
result2 = iso_ts_adder.process(data_with_ts)

print(result1)
# 输出: {"title": "Sample Document", "processed_at": 1623456789}

print(result2)
# 输出: {"timestamp": "2023-06-12T15:19:49.123456", "title": "Another Document"}

# 在管道中使用
pipeline = Pipeline([
    TimestampAdder(),
    # 其他操作符
])

# 批量处理
documents = [
    {"title": "Doc 1"},
    {"title": "Doc 2"},
    {"title": "Doc 3"}
]

for doc in documents:
    result = pipeline.process(doc)
    print(result)
# 输出: (注意每个文档的时间戳会略有不同)
# {"title": "Doc 1", "timestamp": 1623456789}
# {"title": "Doc 2", "timestamp": 1623456789}
# {"title": "Doc 3", "timestamp": 1623456789}
```

### 表达式操作符

#### JsonExpressionOperator

使用 Python 表达式处理 JSON 数据。

**输入**: JSON 对象  
**输出**: 表达式处理后的 JSON 对象

**参数**:
- `expression` (str): Python 表达式
- `input_var_name` (str, 可选): 输入数据在表达式中的变量名，默认为 "input"
- `globals` (dict, 可选): 表达式可用的全局变量

**示例**:

```python
from jsonflow.operators.json_ops import JsonExpressionOperator
from jsonflow.core import Pipeline

# 创建表达式操作符
expr_op = JsonExpressionOperator(
    expression="""
    {
        'id': input.get('id'),
        'title': input.get('title', '').upper(),
        'summary': input.get('content', '')[:50] + '...' if len(input.get('content', '')) > 50 else input.get('content', ''),
        'word_count': len(input.get('content', '').split()),
        'is_long': len(input.get('content', '').split()) > 100
    }
    """,
    input_var_name="input"
)

# 示例数据
data = {
    "id": "doc-123",
    "title": "Sample Document",
    "content": "This is a sample document for testing the JSONFlow library. " * 5
}

# 处理数据
result = expr_op.process(data)
print(result)
# 输出:
# {
#   "id": "doc-123",
#   "title": "SAMPLE DOCUMENT",
#   "summary": "This is a sample document for testing the JSONFlow ...",
#   "word_count": 60,
#   "is_long": False
# }

# 带全局变量的表达式
import re
def count_words(text):
    return len(text.split())

expr_with_globals = JsonExpressionOperator(
    expression="""
    {
        'text': input.get('text', ''),
        'clean_text': re.sub(r'[^a-zA-Z0-9 ]', '', input.get('text', '')),
        'word_count': count_words(input.get('text', ''))
    }
    """,
    globals={"re": re, "count_words": count_words}
)

data = {"text": "Hello, World! This is a test."}
result = expr_with_globals.process(data)
print(result)
# 输出:
# {
#   "text": "Hello, World! This is a test.",
#   "clean_text": "Hello World This is a test",
#   "word_count": 6
# }
```

## 工具组件

### SystemField 工具

`SystemField` 是一个辅助类，提供便捷方法向 JSON 对象添加系统字段。

```python
from jsonflow.utils import SystemField

# 添加唯一 ID
data = {"title": "Sample"}
data = SystemField.add_id(data, field_name="document_id")
print(data)
# 输出: {"title": "Sample", "document_id": "550e8400-e29b-41d4-a716-446655440000"}

# 添加时间戳
data = SystemField.add_timestamp(data)
print(data)
# 输出: {"title": "Sample", "document_id": "...", "timestamp": 1623456789}

# 添加格式化日期时间
data = SystemField.add_datetime(data, format="%Y-%m-%d", field_name="date")
print(data)
# 输出: {"title": "Sample", "document_id": "...", "timestamp": 1623456789, "date": "2023-06-12"}

# 添加多个系统字段
data = {"content": "Test"}
data = SystemField.add_system_fields(data, 
                                   add_id=True, 
                                   add_timestamp=True,
                                   add_datetime=True)
print(data)
# 输出:
# {
#   "content": "Test",
#   "id": "550e8400-e29b-41d4-a716-446655440000",
#   "timestamp": 1623456789,
#   "datetime": "2023-06-12T15:19:49"
# }
```

### 多种执行模式

JSONFlow 支持多种执行模式以适应不同需求。

#### 同步执行

```python
from jsonflow.core import Pipeline, SyncExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer

# 创建管道
pipeline = Pipeline([TextNormalizer(text_fields=["text"])])

# 创建同步执行器
executor = SyncExecutor(pipeline)

# 加载数据
loader = JsonLoader("input.jsonl")
data = loader.load()

# 执行处理
results = executor.execute_all(data)

# 保存结果
JsonSaver("output.jsonl").write_all(results)
```

#### 多线程执行

```python
from jsonflow.core import Pipeline, MultiThreadExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer

# 创建管道
pipeline = Pipeline([TextNormalizer(text_fields=["text"])])

# 创建多线程执行器
executor = MultiThreadExecutor(pipeline, max_workers=4)

# 加载数据
loader = JsonLoader("input.jsonl")
data = loader.load()

# 并发执行处理
results = executor.execute_all(data)

# 保存结果
JsonSaver("output.jsonl").write_all(results)
```

#### 多进程执行

```python
from jsonflow.core import Pipeline, MultiProcessExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer

# 创建管道
pipeline = Pipeline([TextNormalizer(text_fields=["text"])])

# 创建多进程执行器
executor = MultiProcessExecutor(pipeline, max_workers=4)

# 加载数据
loader = JsonLoader("input.jsonl")
data = loader.load()

# 并发执行处理
results = executor.execute_all(data)

# 保存结果
JsonSaver("output.jsonl").write_all(results)
```

## 综合示例

### 文本分析流水线

```python
from jsonflow.core import Pipeline, MultiThreadExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import (
    TextNormalizer, 
    JsonSplitter, 
    JsonAggregator, 
    JsonFieldMapper
)
from jsonflow.operators.model import ModelInvoker
from jsonflow.utils import SystemField

# 创建完整处理流水线
pipeline = Pipeline()
pipeline.set_passthrough_fields(["id", "metadata"])

# 第一步：添加系统字段与文本规范化
pipeline.add(JsonFieldMapper(mappings={
    "id": lambda v, obj: SystemField.add_id(obj)["id"] if "id" not in obj else v,
    "text": lambda v: v.strip() if v else ""
}))

# 第二步：分段处理
pipeline.add(JsonSplitter(split_field="paragraphs", keep_original=True))

# 第三步：处理每个段落
pipeline.add(TextNormalizer(text_fields=["paragraphs"]))

# 第四步：统计信息
pipeline.add(JsonFieldMapper(mappings={
    "word_count": lambda _, obj: len(obj.get("paragraphs", "").split()),
    "char_count": lambda _, obj: len(obj.get("paragraphs", "")),
}))

# 第五步：大语言模型处理（对每个段落）
pipeline.add(ModelInvoker(
    model="gpt-3.5-turbo", 
    prompt_field="paragraphs",
    response_field="paragraph_summary",
    system_prompt="Summarize the following paragraph in one sentence."
))

# 第六步：重新聚合
pipeline.add(JsonAggregator(strategy="list"))

# 第七步：创建最终摘要
pipeline.add(ModelInvoker(
    model="gpt-3.5-turbo",
    prompt_field="paragraph_summary",
    response_field="document_summary",
    system_prompt="Create a concise summary from these paragraph summaries."
))

# 创建多线程执行器
executor = MultiThreadExecutor(pipeline, max_workers=4)

# 加载数据
data = JsonLoader("documents.jsonl").load()

# 并发处理
results = executor.execute_all(data)

# 保存结果
JsonSaver("processed_documents.jsonl").write_all(results)

print(f"处理完成！共处理 {len(results)} 个文档。")
```

### 数据转换流水线

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import (
    JsonTransformer,
    JsonFieldSelector,
    JsonPathExtractor,
    JsonFilter
)

# 创建数据转换流水线
pipeline = Pipeline()

# 第一步：提取需要的字段路径
pipeline.add(JsonPathExtractor({
    "id": "$.id",
    "title": "$.metadata.title",
    "author": "$.metadata.author.name",
    "content": "$.body.content",
    "tags": "$.metadata.tags[*]"
}))

# 第二步：过滤数据
pipeline.add(JsonFilter(filter_func=lambda x: 
    x.get("content") and len(x.get("content", "")) > 100
))

# 第三步：转换数据结构
pipeline.add(JsonTransformer(lambda x: {
    "document": {
        "id": x.get("id"),
        "title": x.get("title"),
        "author": x.get("author")
    },
    "content": x.get("content"),
    "metadata": {
        "tags": x.get("tags", []),
        "length": len(x.get("content", "")),
        "word_count": len(x.get("content", "").split())
    }
}))

# 第四步：选择最终输出字段
pipeline.add(JsonFieldSelector(fields=["document", "metadata"]))

# 加载和处理数据
loader = JsonLoader("source_data.jsonl")
saver = JsonSaver("transformed_data.jsonl")

for item in loader:
    result = pipeline.process(item)
    if result:  # 处理过滤后的非空结果
        saver.write(result)

print("数据转换完成！")
```

## 更多资源

- [JSONFlow GitHub 仓库](https://github.com/guru4elephant/jsonflow)
- [问题反馈](https://github.com/guru4elephant/jsonflow/issues)
- [贡献指南](https://github.com/guru4elephant/jsonflow/blob/main/CONTRIBUTING.md) 

## 模型操作符

### ModelInvoker

用于调用大语言模型的操作符，支持多种模型和自定义提示。

**输入**: 包含提示信息的 JSON 对象  
**输出**: 添加了模型响应的 JSON 对象

**参数**:
- `model` (str): 要使用的模型名称，如 "gpt-3.5-turbo"
- `prompt_field` (str, 可选): 输入 JSON 中包含提示的字段名，默认为 "prompt"
- `response_field` (str, 可选): 输出 JSON 中保存响应的字段名，默认为 "response"
- `system_prompt` (str, 可选): 系统提示，通常用于设置模型行为
- `prompt_template` (str, 可选): 提示模板，使用 {field_name} 引用输入 JSON 中的字段
- `temperature` (float, 可选): 生成随机性，默认为 0.7
- `api_key` (str, 可选): API 密钥，未提供则从环境变量读取
- `api_base` (str, 可选): API 基础 URL，未提供则使用默认值
- `model_kwargs` (dict, 可选): 传递给模型的其他参数

**示例**:

```python
from jsonflow.operators.model import ModelInvoker
import os

# 设置 API 密钥（也可通过环境变量设置）
os.environ["OPENAI_API_KEY"] = "your-api-key"  # 安全起见，建议使用环境变量

# 基本用法：使用指定字段作为提示
model_invoker = ModelInvoker(
    model="gpt-3.5-turbo",
    prompt_field="question",
    response_field="answer",
    temperature=0.5
)

# 处理单个 JSON 对象
result = model_invoker.process({
    "id": "q1",
    "question": "什么是 JSONFlow？"
})

print(result)
# 输出:
# {
#   "id": "q1",
#   "question": "什么是 JSONFlow？",
#   "answer": "JSONFlow 是一个专为 JSON 数据处理而设计的高效库，它允许用户通过组合不同的操作符来构建灵活的数据处理流水线。它支持从文件或标准输入加载 JSON 数据，并提供各种操作符对数据进行转换、过滤和处理。JSONFlow 还支持并发执行以提高处理大量数据的效率。"
# }

# 使用系统提示和提示模板
summarizer = ModelInvoker(
    model="gpt-3.5-turbo",
    prompt_field="text",
    response_field="summary",
    system_prompt="你是一个专业的文本摘要工具，请提供简洁明了的摘要。",
    prompt_template="请为以下{document_type}生成一个简短的摘要，保持在100字以内:\n\n{text}",
    temperature=0.3
)

article = {
    "document_type": "新闻文章",
    "text": "今日，科研人员宣布了一项突破性的发现，可能彻底改变我们对气候变化的理解。这项研究表明，通过特定的碳捕获技术，二氧化碳可以更高效地从大气中移除。研究团队表示，如果全球范围内部署这项技术，温室气体浓度可能在未来十年内显著下降。然而，专家指出实施该技术面临资金和基础设施挑战。",
    "metadata": {
        "source": "科技日报",
        "date": "2023-06-15"
    }
}

result = summarizer.process(article)
print(result)
# 输出:
# {
#   "document_type": "新闻文章",
#   "text": "今日，科研人员宣布了一项突破性的发现，可能彻底改变我们对气候变化的理解。这项研究表明，通过特定的碳捕获技术，二氧化碳可以更高效地从大气中移除。研究团队表示，如果全球范围内部署这项技术，温室气体浓度可能在未来十年内显著下降。然而，专家指出实施该技术面临资金和基础设施挑战。",
#   "metadata": {
#     "source": "科技日报",
#     "date": "2023-06-15"
#   },
#   "summary": "科研人员发现一种高效碳捕获技术，可能显著降低大气中的二氧化碳浓度，从而改变气候变化趋势。若全球部署，未来十年温室气体浓度有望大幅下降，但实施面临资金和基础设施方面的挑战。"
# }

# 批量处理多个问题
questions = [
    {"id": "q1", "question": "什么是机器学习？"},
    {"id": "q2", "question": "深度学习与传统机器学习有何区别？"},
    {"id": "q3", "question": "神经网络如何工作？"}
]

qa_model = ModelInvoker(
    model="gpt-3.5-turbo",
    prompt_field="question",
    response_field="answer",
    system_prompt="你是一位人工智能专家，请提供准确简洁的解答。",
    temperature=0.2
)

for question in questions:
    result = qa_model.process(question)
    print(f"问题: {result['question']}")
    print(f"回答: {result['answer']}")
    print("-" * 50)

# 使用完整配置的例子
advanced_invoker = ModelInvoker(
    model="gpt-3.5-turbo-16k",
    prompt_field="content",
    response_field="analysis",
    system_prompt="你是一位专业的文本分析师，擅长分析文本的情感、主题和关键点。",
    prompt_template="请分析以下{content_type}的内容，包括：\n1. 整体情感\n2. 主要主题\n3. 关键观点\n\n内容：{content}",
    temperature=0.4,
    model_kwargs={
        "max_tokens": 1000,
        "top_p": 0.95,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    }
)

text_for_analysis = {
    "content_type": "产品评论",
    "content": "这款新推出的智能手机价格虽然不低，但整体性能非常出色。屏幕显示效果细腻，色彩还原度高，是我用过的最好的屏幕之一。相机系统在各种光线条件下都表现优异，尤其是夜景模式令人印象深刻。电池续航也很强，重度使用可以坚持一整天。唯一的缺点是充电速度略慢，并且手机背面很容易留下指纹。总体来说，这是一款值得推荐的高端智能手机。",
    "product_id": "SP-2023-X1"
}

result = advanced_invoker.process(text_for_analysis)
print(result["analysis"])
# 输出内容将包含详细的文本分析结果 