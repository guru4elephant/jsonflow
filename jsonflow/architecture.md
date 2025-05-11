# JSONFlow 软件架构设计

## 1. 核心组件

### 1.1 基础组件
- **Operator**: 所有操作符的基类，定义了处理JSON数据的接口
- **Pipeline**: 操作符的容器，负责按顺序执行操作符
- **Executor**: 执行器，负责并发或串行执行Pipeline

### 1.2 IO组件
- **JsonLoader**: 从文件或标准输入加载JSON数据
- **JsonSaver**: 将JSON数据保存到文件或标准输出

### 1.3 操作符组件
- **基础操作符**: 如TextNormalizer、JsonFilter、JsonTransformer等
- **字段操作符**: 如JsonFieldSelector、JsonPathExtractor、JsonPathUpdater等
- **表达式操作符**: 如JsonExpressionOperator、JsonFieldMapper、JsonTemplateOperator等
- **模型操作符**: 如ModelInvoker，负责调用大语言模型
- **集合操作符**: 如JsonSplitter、JsonAggregator等，用于处理JSON集合

### 1.4 工具组件
- **日志工具**: 提供日志记录功能，包括操作符IO日志装饰器
- **配置工具**: 提供配置管理功能
- **BOS工具**: 提供百度对象存储(Baidu Object Storage)功能，支持并发上传和下载文件

### 1.5 系统级功能
- **字段透传**: 支持在pipeline中自动透传指定字段，避免每个operator重复处理
- **系统字段**: 支持在数据中嵌入系统级字段，如id、timestamp等
- **集合处理模式**: 支持两种集合处理模式：展平模式和嵌套模式

## 2. 类关系图

```
+-------------------+       +-------------------+       +-------------------+
|     Operator      |<------+     Pipeline      |<------+     Executor      |
+-------------------+       +-------------------+       +-------------------+
         ^                        ^      |
         |                        |      |
         |                        |      v
+-------------------+       +-------------------+
| OperatorDecorator |       |  JsonLoader/Saver |
+-------------------+       +-------------------+
         ^
         |
+-------------------+
|     LogIoDecorator|
+-------------------+

+-------------------+
|   JsonOperator    |
+-------------------+
         ^
         |
+-------+-------+---+-------+-------+-------+
|               |                   |               |
+-------------------+   +-------------------+   +-------------------+
|   JsonTextOps     |   |   JsonFieldOps    |   |   JsonModelOps    |
+-------------------+   +-------------------+   +-------------------+
|  TextNormalizer   |   | JsonFieldSelector |   |   ModelInvoker    |
|  JsonFilter       |   | JsonPathExtractor |   +-------------------+
+-------------------+   +-------------------+
                                ^
                                |
                        +-------------------+
                        |   JsonExprOps     |
                        +-------------------+
                        | JsonExprOperator  |
                        | JsonFieldMapper   |
                        +-------------------+
                                ^
                                |
                        +-------------------+
                        |  CollectionOps    |
                        +-------------------+
                        |   JsonSplitter    |
                        |   JsonAggregator  |
                        +-------------------+
```

## 3. 功能设计

### 3.1 操作符设计

操作符是JSONFlow的核心组件，所有操作符都继承自基类Operator，需要实现process方法。每个操作符接收一个JSON对象或JSON列表作为输入，并返回一个JSON对象或JSON列表作为输出。

关键特性：
- 支持处理单个JSON对象或JSON列表
- 支持批处理模式
- 支持字段透传
- 支持异常处理和日志记录

### 3.2 管道设计

Pipeline用于串联多个操作符，按顺序执行它们。Pipeline本身也可以视为一个大型的操作符，接收JSON数据并返回处理后的结果。

关键特性：
- 支持链式调用
- 支持字段透传，自动将指定字段从输入传递到输出
- 支持两种集合处理模式：
  - **展平模式（FLATTEN）**：每个操作符处理单个JSON项，如果操作符返回列表，会自动展平并分别处理
  - **嵌套模式（NESTED）**：将JSON列表作为一个整体传递给操作符链，保持列表的嵌套结构

### 3.3 集合处理

JSONFlow支持处理JSON集合（列表），主要通过以下方式：

1. **单个JSON转多个JSON**：通过JsonSplitter操作符，可以将单个JSON对象中的数组字段拆分为多个独立的JSON对象
   
2. **多个JSON转单个JSON**：通过JsonAggregator操作符，可以将多个JSON对象合并为单个JSON对象，支持多种合并策略：
   - **列表合并**：将多个JSON对象合并为一个列表
   - **字段合并**：将多个JSON对象的字段合并为一个对象

3. **Pipeline集合处理模式**：
   - **展平模式**：自动展平操作符返回的列表，适合需要对列表中每项单独处理的场景
   - **嵌套模式**：保持列表的嵌套结构，适合需要整体处理列表的场景

### 3.4 执行器设计

Executor负责执行Pipeline，支持并发或串行执行。

关键特性：
- 支持多线程并发执行
- 支持多进程并发执行
- 支持异步执行
- 支持批处理

### 3.5 IO设计

JsonLoader和JsonSaver负责JSON数据的加载和保存。

关键特性：
- 支持从文件、标准输入/输出读写
- 支持批量加载和保存
- 支持单个JSON对象和JSON列表的处理

## 4. 接口定义

### 4.1 Operator接口

```python
class Operator:
    def process(self, json_data):
        """
        处理JSON数据
        
        Args:
            json_data (dict or list): 输入的JSON数据，可以是单个对象或列表
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        pass
```

### 4.2 Pipeline接口

```python
class Pipeline:
    def __init__(self, operators=None, passthrough_fields=None, collection_mode='flatten'):
        pass
        
    def add(self, operator):
        pass
        
    def process(self, json_data):
        pass
```

### 4.3 Executor接口

```python
class Executor:
    def __init__(self, pipeline, max_workers=None, mode='thread'):
        pass
        
    def execute(self, json_data):
        pass
        
    def execute_batch(self, json_data_list):
        pass
```

### 4.4 JsonLoader/JsonSaver接口

```python
class JsonLoader:
    def __init__(self, source=None):
        pass
        
    def load(self):
        pass
    
    def load_batch(self, batch_size=100):
        pass
        
class JsonSaver:
    def __init__(self, destination=None):
        pass
        
    def write(self, json_data):
        pass
        
    def write_all(self, json_data_list):
        pass
``` 