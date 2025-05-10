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
- **集合处理**: 支持在pipeline中处理单个JSON和JSON集合（列表）

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
  |     +-- JsonSplitter
  |     +-- JsonAggregator
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
  |
  +-- SystemField (系统字段管理)
  |
  +-- BosHelper (百度对象存储工具)
```

## 3. 组件详细设计

### 3.1 Operator
- **属性**:
  - `name`: 操作符名称
  - `description`: 操作符描述
  - `supports_batch`: 是否支持批处理（处理JSON列表）
- **方法**:
  - `process(json_data)`: 处理JSON数据的抽象方法，子类需要实现，支持单个JSON或JSON列表
  - `process_item(json_data)`: 处理单个JSON数据的方法，适用于不支持批处理的操作符
  - `process_batch(json_data_list)`: 处理JSON列表的方法，适用于支持批处理的操作符
  - `__call__(json_data)`: 便捷调用方法，内部调用`process`

### 3.2 Pipeline
- **属性**:
  - `operators`: 操作符列表
  - `passthrough_fields`: 需要透传的字段列表
  - `handle_collections`: 如何处理集合（自动展平或保持嵌套）
- **方法**:
  - `add(operator)`: 添加操作符
  - `process(json_data)`: 按顺序执行所有操作符，并处理透传字段，支持单个JSON或JSON列表
  - `__iter__()`: 迭代器方法，便于遍历所有操作符
  - `set_passthrough_fields(fields)`: 设置需要透传的字段列表
  - `set_collection_mode(mode)`: 设置集合处理模式（'flatten'或'nested'）

### 3.3 JsonLoader
- **属性**:
  - `source`: 数据源（文件路径或stdin）
- **方法**:
  - `load()`: 加载所有JSON数据
  - `__iter__()`: 迭代器方法，便于逐行加载JSON
  - `load_batch(batch_size)`: 批量加载指定数量的JSON数据

### 3.4 JsonSaver
- **属性**:
  - `destination`: 目标位置（文件路径或stdout）
- **方法**:
  - `write(json_data)`: 写入单个JSON数据或JSON列表
  - `write_all(json_data_list)`: 批量写入JSON数据
  - `write_item(json_data)`: 写入单个JSON数据

### 3.5 Executor
- **属性**:
  - `pipeline`: 要执行的Pipeline
- **方法**:
  - `execute(json_data)`: 执行Pipeline处理单个JSON数据或JSON列表
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

### 3.8 系统字段管理
- **功能**:
  - 提供创建和管理系统字段的工具类
  - 支持自动生成ID、时间戳等系统字段
  - 支持添加和移除系统字段

### 3.9 BOS工具
- **功能**:
  - 提供与百度对象存储(BOS)的交互功能
  - 支持并发上传和下载文件
  - 提供目录级操作和单文件操作
  - 支持配置管理和错误处理

### 3.10 集合处理操作符
- **功能**:
  - JsonSplitter: 将单个JSON拆分为多个JSON
  - JsonAggregator: 将多个JSON合并为单个JSON
  - 提供自定义逻辑来拆分和合并JSON数据

## 4. 数据流程

1. 通过JsonLoader从文件或标准输入加载JSON数据
2. 通过Pipeline组织多个Operator，设置需要透传的字段
3. Pipeline处理数据时，自动处理透传字段
4. 处理时可能发生单个JSON到多个JSON的转换，或多个JSON到单个JSON的合并
5. 使用Executor执行Pipeline处理JSON数据
6. 通过JsonSaver将处理后的JSON数据保存到文件或标准输出
7. 可选择使用BOS工具将处理结果上传到云存储

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

### 5.4 字段透传系统
- 支持在Pipeline级别设置需要透传的字段
- 保证透传字段在整个处理流程中不丢失
- 提供字段透传的配置接口

### 5.5 系统字段管理
- 提供常用系统字段的自动生成功能
- 支持自定义系统字段
- 提供字段添加和移除的配置接口

### 5.6 云存储集成
- 支持通过BOS工具与百度云对象存储集成
- 提供高性能的并发上传与下载功能
- 支持大规模数据的云端存储与处理

### 5.7 集合处理模式
- **展平模式(flatten)**: 当操作符输出列表时，Pipeline会自动展平处理每个元素
- **嵌套模式(nested)**: Pipeline保持列表的嵌套结构，传递给下一个操作符
- 两种模式可以根据需要在Pipeline级别配置

## 6. 配置系统
- 支持通过配置文件设置默认参数
- 支持通过环境变量覆盖默认参数 