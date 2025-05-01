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