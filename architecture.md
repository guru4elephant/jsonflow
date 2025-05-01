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

### 1.4 工具组件
- **日志工具**: 提供日志记录功能，包括操作符IO日志装饰器
- **配置工具**: 提供配置管理功能

## 2. 类关系图

```
Operator (abstract)
  |
  +-- JsonOperator (abstract)
  |     |
  |     +-- TextNormalizer
  |     +-- JsonFilter
  |     +-- JsonTransformer
  |     +-- JsonFieldSelector
  |     +-- JsonPathOperator
  |     |     |
  |     |     +-- JsonPathExtractor
  |     |     +-- JsonPathUpdater
  |     |     +-- JsonPathRemover
  |     |
  |     +-- JsonStringOperator
  |     +-- JsonStructureExtractor
  |     +-- JsonArrayOperator
  |     +-- JsonMerger
  |     +-- JsonExpressionOperator
  |     |     |
  |     |     +-- JsonFieldMapper
  |     |
  |     +-- JsonTemplateOperator
  |     +-- DebugOperator
  |
  +-- ModelOperator (abstract)
        |
        +-- ModelInvoker
        +-- MockModelOperator
        +-- ...

Pipeline
  |
  +-- 包含多个 Operator

Executor
  |
  +-- SyncExecutor
  |
  +-- AsyncExecutor
  |
  +-- MultiProcessExecutor
  |
  +-- MultiThreadExecutor

IO
  |
  +-- JsonLoader
  |
  +-- JsonSaver

Utils
  |
  +-- Logger
  |
  +-- Config
  |
  +-- OperatorUtils (提供装饰器等功能)
```

## 3. 组件详细设计

### 3.1 Operator
- **属性**:
  - `name`: 操作符名称
  - `description`: 操作符描述
- **方法**:
  - `process(json_data)`: 处理JSON数据的抽象方法，子类需要实现
  - `__call__(json_data)`: 便捷调用方法，内部调用`process`

### 3.2 Pipeline
- **属性**:
  - `operators`: 操作符列表
- **方法**:
  - `add(operator)`: 添加操作符
  - `process(json_data)`: 按顺序执行所有操作符
  - `__iter__()`: 迭代器方法，便于遍历所有操作符

### 3.3 JsonLoader
- **属性**:
  - `source`: 数据源（文件路径或stdin）
- **方法**:
  - `load()`: 加载所有JSON数据
  - `__iter__()`: 迭代器方法，便于逐行加载JSON

### 3.4 JsonSaver
- **属性**:
  - `destination`: 目标位置（文件路径或stdout）
- **方法**:
  - `write(json_data)`: 写入单个JSON数据
  - `write_all(json_data_list)`: 批量写入JSON数据

### 3.5 Executor
- **属性**:
  - `pipeline`: 要执行的Pipeline
- **方法**:
  - `execute(json_data)`: 执行Pipeline处理单个JSON数据
  - `execute_all(json_data_list)`: 批量执行Pipeline处理多个JSON数据

### 3.6 操作符IO日志装饰器
- **功能**:
  - 记录操作符的输入和输出数据
  - 支持自定义日志配置
  - 提供简单的API来控制日志开关
  
### 3.7 JSON表达式操作符
- **功能**:
  - 使用Python表达式处理JSON数据
  - 支持Lambda函数和命名函数
  - 提供字段映射和模板功能

## 4. 数据流程

1. 通过JsonLoader从文件或标准输入加载JSON数据
2. 通过Pipeline组织多个Operator
3. 使用Executor执行Pipeline处理JSON数据
4. 通过JsonSaver将处理后的JSON数据保存到文件或标准输出

## 5. 扩展设计

### 5.1 自定义操作符
用户可以通过继承Operator基类或其子类来创建自定义操作符

### 5.2 错误处理
- 每个组件都包含错误处理机制
- Pipeline可以配置出错后的行为（跳过或中断）

### 5.3 日志系统
- 所有组件支持日志记录
- 可配置日志级别和输出目标
- 提供操作符IO日志装饰器

## 6. 配置系统
- 支持通过配置文件设置默认参数
- 支持通过环境变量覆盖默认参数 