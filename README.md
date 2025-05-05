# JSONFlow

JSONFlow是一个处理JSON数据的流式处理库。它可以以JSON格式的文件或标准输入作为输入，通过一系列操作符处理数据，并输出处理后的结果。

## 特性

- 以JSON格式的文件或标准输入作为输入
- 通过操作符处理JSON数据
- 将多个操作符组合成处理管道
- 支持同步和异步执行
- 支持多线程或多进程并发处理
- 专门用于调用大语言模型的操作符
- 系统级操作符日志功能，方便调试和开发
- 丰富的JSON字段处理操作符和表达式操作符
- 支持字段透传功能，避免每个操作符重复处理相同字段
- 支持系统字段管理，方便添加和处理ID、时间戳等系统级字段

## 安装

```bash
pip install jsonflow
```

## 快速开始

以下是一个简单的示例，展示如何使用JSONFlow处理JSON数据：

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

## 字段透传功能

JSONFlow提供了字段透传功能，允许在pipeline中设置特定字段自动透传，避免每个操作符都需要处理相同的系统字段：

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

# 创建一个带有透传字段的管道
pipeline = Pipeline([
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo"),
])

# 设置需要透传的字段
pipeline.set_passthrough_fields(['id', 'metadata'])

# 处理数据
loader = JsonLoader("input.jsonl")
saver = JsonSaver("output.jsonl")

for json_line in loader:
    # id 和 metadata 字段会在整个处理流程中保持不变
    result = pipeline.process(json_line)
    saver.write(result)
```

字段透传功能确保指定的字段在整个管道处理过程中不会丢失，特别适用于需要保留ID、元数据等系统字段的场景。

## 系统字段管理

JSONFlow提供了系统字段管理功能，方便添加UUID、时间戳等系统级字段：

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, IdAdder, TimestampAdder
from jsonflow.operators.model import ModelInvoker
from jsonflow.utils.system_field import SystemField

# 使用系统字段操作符
pipeline = Pipeline([
    IdAdder(),  # 添加UUID作为id字段
    TimestampAdder(),  # 添加时间戳
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo"),
])

# 也可以直接使用SystemField工具类
data = {"text": "示例文本"}
data = SystemField.add_id(data)  # 添加UUID
data = SystemField.add_timestamp(data)  # 添加时间戳
data = SystemField.add_datetime(data)  # 添加格式化日期时间
data = SystemField.add_custom_field(data, "source", "example")  # 添加自定义字段
```

系统字段管理支持以下操作：

- `IdAdder`: 添加UUID作为ID
- `TimestampAdder`: 添加UNIX时间戳
- `DateTimeAdder`: 添加格式化的日期时间
- `CustomFieldAdder`: 添加自定义字段
- `FieldRemover`: 移除指定字段

## 结合使用字段透传和系统字段

以下示例展示如何结合使用字段透传和系统字段功能：

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, IdAdder, TimestampAdder
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

## 表达式操作符

JSONFlow提供了强大的表达式操作符，使用Python语法处理JSON数据：

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

# 处理数据
result = expr_op.process(data)
```

## 并发处理

JSONFlow支持并发处理多个JSON数据：

```python
from jsonflow.core import Pipeline, MultiThreadExecutor
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

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
```

## 操作符输入输出日志

JSONFlow提供了系统级别的操作符输入输出日志功能，方便调试和开发：

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer, JsonExpressionOperator
from jsonflow.utils import enable_operator_io_logging, set_io_log_indent, set_io_log_truncate_length

# 启用操作符输入输出日志
enable_operator_io_logging(True)
# 设置日志缩进
set_io_log_indent(2)
# 设置长JSON的截断长度
set_io_log_truncate_length(1000)

# 创建并运行管道
pipeline = Pipeline([
    TextNormalizer(),
    JsonExpressionOperator({
        "summary": lambda d: f"处理{d.get('text', '')}"
    })
])

result = pipeline.process({"text": "示例文本"})

# 禁用操作符日志
enable_operator_io_logging(False)
```

通过启用此功能，系统会自动记录每个操作符的输入和输出JSON数据，方便开发和调试。

## 自定义操作符

您可以通过继承`JsonOperator`类创建自定义操作符：

```python
from jsonflow.core import JsonOperator

class MyOperator(JsonOperator):
    def __init__(self, name=None, description=None):
        super().__init__(name, description or "My custom operator")
    
    def process(self, json_data):
        # 处理JSON数据
        result = json_data.copy()
        # 进行自定义处理
        result["processed_by"] = self.name
        return result
```

## 许可证

MIT 

# JSONL检查工具

这个脚本用于检查JSONL文件，验证每行是否是有效的JSON，并可以选择过滤无效行，只输出有效的JSON行。

## 功能特点

- 检查JSONL文件中每行是否是有效的JSON
- 提供选项过滤无效JSON行
- 支持从标准输入读取和向标准输出写入
- 提供详细的错误报告
- 提供简单的统计信息
- 尝试自动修复常见的JSON错误
- 规范化空白字符处理

## 使用方法

```bash
./check_jsonl.py [-h] [-o OUTPUT] [-r] [-v] [-c] [-n] [-f] input
```

### 参数说明

- `input`: 输入JSONL文件 (使用 "-" 从标准输入读取)
- `-o, --output OUTPUT`: 输出文件 (使用 "-" 输出到标准输出)
- `-r, --remove-invalid`: 移除无效的JSON行
- `-v, --verbose`: 显示详细信息
- `-c, --count-only`: 仅显示统计信息
- `-n, --normalize-whitespace`: 规范化空白字符（将制表符、回车等替换为空格）
- `-f, --fix-errors`: 尝试修复简单的JSON错误
- `-h, --help`: 显示帮助信息

### 示例

1. 检查JSONL文件并显示统计信息:

```bash
./check_jsonl.py data.jsonl -v
```

2. 移除无效JSON行并输出到新文件:

```bash
./check_jsonl.py data.jsonl -r -o filtered_data.jsonl
```

3. 从标准输入读取，过滤后输出到标准输出:

```bash
cat data.jsonl | ./check_jsonl.py - -r
```

4. 只显示统计信息:

```bash
./check_jsonl.py data.jsonl -c
```

5. 尝试修复JSON错误并保存结果:

```bash
./check_jsonl.py data.jsonl -f -r -o fixed_data.jsonl
```

6. 规范化空白字符并过滤:

```bash
./check_jsonl.py data.jsonl -n -r > cleaned_data.jsonl
```

## 返回值

- 0: 所有行都是有效的JSON
- 1: 存在无效的JSON行

## 依赖

- Python 3.6+
- 标准库: argparse, json, sys, pathlib 