# JSONFlow

一个高效、灵活的JSON数据流式处理库，专为大规模数据处理和大语言模型交互设计。

## 核心特性

- **流式处理架构**: 将JSON数据通过操作符链式处理，支持单个对象和批量处理
- **集合处理能力**: 智能处理JSON列表，支持自动展平或保持嵌套结构
- **大语言模型集成**: 专门的模型操作符，轻松调用各种大语言模型
- **并发执行**: 多线程/多进程并行处理，保持输入顺序
- **字段透传**: 自动保留指定字段，避免重复处理系统字段
- **系统字段管理**: 简化ID、时间戳等系统级字段的添加与管理
- **丰富的操作符**: 内置文本处理、字段操作、表达式计算等多种操作符
- **操作符IO日志**: 全面的日志系统，便于调试和开发

## 安装

```bash
pip install jsonflow
```

## 快速开始

### 基本用法

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

# 创建处理管道
pipeline = Pipeline([
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo"),
])

# 处理单个JSON文件
loader = JsonLoader("input.jsonl")
saver = JsonSaver("output.jsonl")

for json_line in loader:
    result = pipeline.process(json_line)
    saver.write(result)
```

### 集合处理

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import JsonSplitter, JsonAggregator

# 创建一个带有集合操作的管道
pipeline = Pipeline([
    JsonSplitter(split_field="items"),  # 将单个JSON拆分为多个
    TextNormalizer(),                   # 处理拆分后的每个项目
    ModelInvoker(model="gpt-3.5-turbo"),
], collection_mode="flatten")           # 自动展平结果

# 或者保持嵌套结构，并最终聚合
nested_pipeline = Pipeline([
    JsonSplitter(split_field="items"),
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo"),
    JsonAggregator(aggregate_field="processed_items")
], collection_mode="nested")            # 保持嵌套结构
```

### 字段透传与系统字段

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import IdAdder, TimestampAdder

# 设置带有系统字段和透传功能的管道
pipeline = Pipeline([
    IdAdder(),                          # 添加唯一ID
    TimestampAdder(),                   # 添加时间戳
    TextNormalizer(),
    ModelInvoker(model="gpt-3.5-turbo"),
])

# 设置需要透传的字段
pipeline.set_passthrough_fields(['id', 'timestamp'])
```

### 并发处理

```python
from jsonflow.core import Pipeline, MultiThreadExecutor
from jsonflow.io import JsonLoader, JsonSaver

# 创建多线程执行器
pipeline = Pipeline([...])
executor = MultiThreadExecutor(pipeline, max_workers=4)

# 并行处理所有数据，保持原始顺序
loader = JsonLoader("input.jsonl")
json_data_list = loader.load()
results = executor.execute_all(json_data_list)

saver = JsonSaver("output.jsonl")
saver.write_all(results)
```

## 进阶用法

### 表达式操作符

```python
from jsonflow.operators.json_ops import JsonExpressionOperator

expr_op = JsonExpressionOperator({
    # 使用Lambda函数计算
    "total": lambda d: sum(item["price"] for item in d["items"]),
    # 提取和格式化字段
    "summary": lambda d: f"{d['user']['name']}的订单总额为{d['total']}元",
})
```

### 自定义操作符

```python
from jsonflow.core import JsonOperator

class MyOperator(JsonOperator):
    def __init__(self, param, name=None):
        super().__init__(name, "My custom operator")
        self.param = param
    
    def process_item(self, json_data):
        # 处理逻辑
        json_data["result"] = json_data.get("input", "") + self.param
        return json_data
```

### 异步执行

```python
from jsonflow.core import AsyncExecutor

# 创建异步执行器
async_executor = AsyncExecutor(pipeline)
result = await async_executor.execute(json_data)
```

## 更多示例

查看 `examples` 目录获取更多使用示例和最佳实践。

## 贡献

欢迎提交 Issue 和 Pull Request，一起完善这个库！

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