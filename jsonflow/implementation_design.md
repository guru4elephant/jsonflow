### 2.8 百度对象存储工具 (utils/bos.py)

### 2.9 集合操作符 (operators/json_ops/collection_ops.py)

集合操作符主要用于处理JSON集合的转换，包括单个JSON转换为多个JSON，以及多个JSON合并为一个JSON的场景。

```python
class JsonSplitter(JsonOperator):
    """
    将单个JSON拆分为多个JSON的操作符
    """
    
    def __init__(self, split_field, output_key_map=None, keep_original=False, name=None):
        """
        初始化JsonSplitter
        
        Args:
            split_field (str): 包含要拆分的列表的字段名
            output_key_map (dict, optional): 输出字段映射，用于从原始字段映射到拆分后的新对象
            keep_original (bool, optional): 是否在拆分后的对象中保留其他原始字段
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Split JSON by {split_field} field")
        self.split_field = split_field
        self.output_key_map = output_key_map or {}
        self.keep_original = keep_original
    
    def process_item(self, json_data):
        """
        处理单个JSON对象，将其拆分为多个JSON对象
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            list: 拆分后的JSON对象列表
        """
        # 如果拆分字段不存在，返回原对象的列表
        if self.split_field not in json_data:
            return [json_data]
        
        # 获取要拆分的列表
        items = json_data.get(self.split_field)
        
        # 如果不是列表类型，返回原对象的列表
        if not isinstance(items, list):
            return [json_data]
        
        # 拆分为多个JSON对象
        result = []
        for item in items:
            new_item = {}
            
            # 保留原始字段
            if self.keep_original:
                for key, value in json_data.items():
                    if key != self.split_field:
                        new_item[key] = value
            
            # 处理映射字段
            if self.output_key_map:
                for old_key, new_key in self.output_key_map.items():
                    if old_key in json_data:
                        if old_key == self.split_field:
                            new_item[new_key] = item
                        else:
                            new_item[new_key] = json_data[old_key]
            else:
                new_item[self.split_field] = item
                
            result.append(new_item)
            
        return result


class JsonAggregator(JsonOperator):
    """
    将多个JSON合并为一个JSON的操作符
    """
    
    def __init__(self, aggregate_field=None, strategy='list', condition=None, name=None):
        """
        初始化JsonAggregator
        
        Args:
            aggregate_field (str, optional): 聚合后的字段名，如果不提供则直接返回聚合结果
            strategy (str, optional): 聚合策略，支持'list'和'merge'，默认为'list'
            condition (callable, optional): 筛选条件，接受一个JSON对象参数，返回布尔值
            name (str, optional): 操作符名称
        """
        desc = f"Aggregate JSON objects to {aggregate_field or 'root'} using {strategy} strategy"
        super().__init__(name, desc, supports_batch=True)
        self.aggregate_field = aggregate_field
        self.strategy = strategy
        self.condition = condition
    
    def process_item(self, json_data):
        """
        处理单个JSON对象，直接返回
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 原始JSON数据
        """
        return json_data
    
    def process_batch(self, json_data_list):
        """
        处理JSON对象列表，将其合并为一个对象
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            dict or list: 合并后的JSON数据
        """
        # 如果列表为空，返回空对象或空列表
        if not json_data_list:
            return {} if self.aggregate_field else []
        
        # 应用筛选条件
        if self.condition:
            json_data_list = [item for item in json_data_list if self.condition(item)]
        
        # 根据策略聚合
        if self.strategy == 'list':
            # 列表策略：将所有对象作为列表项
            result = json_data_list
        elif self.strategy == 'merge':
            # 合并策略：将所有对象的字段合并
            result = {}
            for item in json_data_list:
                result.update(item)
        else:
            raise ValueError(f"Unsupported aggregation strategy: {self.strategy}")
        
        # 如果指定了聚合字段，将结果嵌套在该字段下
        if self.aggregate_field:
            return {self.aggregate_field: result}
        return result
```

### 2.10 集合处理模式实现 (core/pipeline.py)

Pipeline支持两种集合处理模式：
1. **展平模式（FLATTEN）**：每个操作符处理单个JSON项，自动展平操作符返回的列表
2. **嵌套模式（NESTED）**：将JSON列表作为一个整体传递给操作符链

```python
class Pipeline:
    """
    操作符的容器，负责按顺序执行操作符
    
    Pipeline类封装了一系列操作符，并按顺序执行它们。
    支持处理单个JSON对象或JSON列表，具有两种集合处理模式。
    """
    
    # 集合处理模式常量
    FLATTEN = 'flatten'  # 展平模式：自动展平操作符返回的列表
    NESTED = 'nested'    # 嵌套模式：保持列表的嵌套结构
    
    def __init__(self, operators=None, passthrough_fields=None, collection_mode=FLATTEN):
        """
        初始化Pipeline
        
        Args:
            operators (list, optional): 操作符列表，如果不提供则创建空列表
            passthrough_fields (list, optional): 需要透传的字段列表
            collection_mode (str, optional): 集合处理模式，'flatten'或'nested'
        """
        self.operators = operators or []
        self.passthrough_fields = passthrough_fields or []
        self.collection_mode = collection_mode
    
    def set_collection_mode(self, mode):
        """
        设置集合处理模式
        
        Args:
            mode (str): 'flatten'或'nested'
        
        Returns:
            Pipeline: 返回self以支持链式调用
        """
        if mode not in [self.FLATTEN, self.NESTED]:
            raise ValueError(f"Collection mode must be '{self.FLATTEN}' or '{self.NESTED}'")
        self.collection_mode = mode
        return self
    
    def process(self, json_data):
        """
        按顺序执行所有操作符，并处理透传字段
        
        Args:
            json_data (dict or list): 输入的JSON数据，可以是单个对象或列表
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        # 记录原始输入是否为列表
        is_list_input = isinstance(json_data, list)
        
        # 如果输入是列表，根据集合处理模式处理
        if is_list_input:
            if self.collection_mode == self.NESTED:
                # 嵌套模式：将整个列表作为一个整体传递给操作符链
                result = json_data
                for op in self.operators:
                    result = op.process(result)
                return result
            else:
                # 展平模式：分别处理列表中的每个项目
                results = []
                for item in json_data:
                    # 处理单个项目
                    result = self._process_single_item(item)
                    # 收集结果
                    if isinstance(result, list):
                        results.extend(result)
                    else:
                        results.append(result)
                return results
        else:
            # 单个JSON对象的处理
            return self._process_single_item(json_data)
    
    def _process_single_item(self, json_data):
        """
        处理单个JSON数据项通过所有操作符
        
        Args:
            json_data (dict): 输入的单个JSON数据
            
        Returns:
            dict or list: 处理后的JSON数据，可能是单个对象或列表
        """
        result = json_data
        original_data = json_data.copy()  # 保存原始数据用于透传
        
        for op in self.operators:
            # 处理当前项
            op_result = op.process(result)
            
            # 根据操作符结果类型和集合处理模式决定如何继续
            if isinstance(op_result, list):
                if self.collection_mode == self.NESTED:
                    # 嵌套模式：保持列表结构传递给下一个操作符
                    result = op_result
                else:
                    # 展平模式：处理列表中的每个项目，应用透传，然后返回
                    processed_results = []
                    for item in op_result:
                        # 应用透传字段到列表中的每个项
                        processed_item = self._apply_passthrough(original_data, item)
                        processed_results.append(processed_item)
                    return processed_results
            else:
                # 结果是单个对象，继续处理
                result = op_result
        
        # 如果结果是单个对象，处理透传字段
        if not isinstance(result, list):
            result = self._apply_passthrough(original_data, result)
        
        return result
    
    def _apply_passthrough(self, original_data, processed_data):
        """
        应用字段透传逻辑
        
        Args:
            original_data (dict): 原始JSON数据
            processed_data (dict): 处理后的JSON数据
            
        Returns:
            dict: 添加了透传字段的JSON数据
        """
        # 提取需要透传的字段值
        passthrough_values = {}
        for field in self.passthrough_fields:
            if field in original_data:
                passthrough_values[field] = original_data[field]
        
        # 将透传字段添加到处理后的数据中
        result = processed_data.copy()
        for field, value in passthrough_values.items():
            result[field] = value
        
        return result
```

## 3. 使用示例

### 3.1 基本使用

### 3.2 集合处理示例

以下示例展示了如何使用JSONFlow处理JSON集合，包括拆分和合并操作：

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer, JsonSplitter, JsonAggregator

# 创建示例数据
input_data = {
    "id": "12345",
    "items": [
        {"text": "First item text"},
        {"text": "Second item text"},
        {"text": "Third item text"}
    ],
    "metadata": {
        "source": "example",
        "created_at": "2023-05-01"
    }
}

# 创建管道，使用展平模式
pipeline1 = Pipeline([
    # 拆分阶段：将'items'字段拆分为多个独立JSON对象
    JsonSplitter(split_field='items', keep_original=True),
    
    # 处理阶段：对拆分后的每个项目进行处理
    TextNormalizer(),
], collection_mode=Pipeline.FLATTEN)

# 处理数据
results = pipeline1.process(input_data)
# 结果是一个列表，包含多个处理后的JSON对象

# 创建管道，使用嵌套模式
pipeline2 = Pipeline([
    # 合并阶段：将所有对象合并到一个列表中
    JsonAggregator(aggregate_field='processed_items', strategy='list')
], collection_mode=Pipeline.NESTED)

# 处理数据（传入上一阶段的列表结果）
final_result = pipeline2.process(results)
# 结果是一个单一的JSON对象，包含所有处理后的项目
```

### 3.3 批量处理示例

以下示例展示了如何使用JSONFlow批量处理JSON数据：

```python
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonFilter

# 创建管道
pipeline = Pipeline([
    TextNormalizer(),
    JsonFilter(lambda x: len(x.get('text', '')) > 10)  # 过滤短文本
])

# 批量加载和处理
loader = JsonLoader("input.jsonl")
saver = JsonSaver("output.jsonl")

# 方法1：一次性加载所有数据
all_data = loader.load()
results = pipeline.process(all_data)  # 自动处理列表
saver.write(results)  # 自动处理列表

# 方法2：批量加载和处理
for batch in loader.load_batch(batch_size=100):
    results = pipeline.process(batch)
    saver.write(results)
``` 