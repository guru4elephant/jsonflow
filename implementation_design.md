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
    
    def __init__(self, name=None, description=None, supports_batch=False):
        self.name = name or self.__class__.__name__
        self.description = description or f"{self.name} operator"
        self.supports_batch = supports_batch
    
    def process(self, json_data):
        """
        处理JSON数据的方法，支持单个JSON对象或JSON列表
        
        Args:
            json_data (dict or list): 输入的JSON数据，可以是单个对象或列表
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        if isinstance(json_data, list):
            return self.process_batch(json_data)
        else:
            return self.process_item(json_data)
    
    def process_item(self, json_data):
        """
        处理单个JSON数据的方法，子类通常需要实现此方法
        
        Args:
            json_data (dict): 输入的单个JSON数据
            
        Returns:
            dict or list: 处理后的JSON数据，可以是单个对象或列表
        """
        raise NotImplementedError("Subclasses must implement process_item() or process_batch()")
    
    def process_batch(self, json_data_list):
        """
        处理JSON列表的方法，支持批处理的子类可以重写此方法提供优化实现
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表
        """
        if self.supports_batch:
            # 对于显式声明支持批处理的子类，应该提供自己的实现
            raise NotImplementedError("Batch-supporting operators must implement process_batch()")
        else:
            # 默认实现：逐个处理列表中的每个项目
            results = []
            for item in json_data_list:
                result = self.process_item(item)
                if isinstance(result, list):
                    # 如果单个项目的处理结果是列表，则展平
                    results.extend(result)
                else:
                    results.append(result)
            return results
    
    def __call__(self, json_data):
        """便捷调用方法，内部调用process"""
        return self.process(json_data)


class JsonOperator(Operator):
    """JSON操作符基类，专门处理JSON数据转换"""
    
    def __init__(self, name=None, description=None, supports_batch=False):
        super().__init__(name, description or "JSON data operator", supports_batch)


class ModelOperator(Operator):
    """模型操作符基类，专门处理模型调用"""
    
    def __init__(self, name=None, description=None, supports_batch=False, **model_params):
        super().__init__(name, description or "Model operator", supports_batch)
        self.model_params = model_params
```

### 2.2 Pipeline (core/pipeline.py)

```python
class Pipeline:
    """操作符的容器，负责按顺序执行操作符"""
    
    # 集合处理模式常量
    FLATTEN = 'flatten'  # 展平模式：自动展平操作符返回的列表
    NESTED = 'nested'    # 嵌套模式：保持列表的嵌套结构
    
    def __init__(self, operators=None, passthrough_fields=None, collection_mode=FLATTEN):
        """
        初始化Pipeline
        
        Args:
            operators (list, optional): 操作符列表
            passthrough_fields (list, optional): 需要透传的字段列表
            collection_mode (str, optional): 集合处理模式，'flatten'或'nested'
        """
        self.operators = operators or []
        self.passthrough_fields = passthrough_fields or []
        self.collection_mode = collection_mode
    
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
    
    def load_batch(self, batch_size=100):
        """
        批量加载指定数量的JSON数据
        
        Args:
            batch_size (int): 每批加载的数据量
            
        Returns:
            generator: 生成器，每次返回一批JSON数据列表
        """
        batch = []
        for item in self:
            batch.append(item)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
    
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
        """
        写入JSON数据，支持单个JSON对象或JSON列表
        
        Args:
            json_data (dict or list): 要写入的JSON数据，可以是单个对象或列表
        """
        if isinstance(json_data, list):
            for item in json_data:
                self.write_item(item)
        else:
            self.write_item(json_data)
    
    def write_item(self, json_data):
        """
        写入单个JSON数据
        
        Args:
            json_data (dict): 要写入的单个JSON数据
        """
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
        """
        批量写入JSON数据
        
        Args:
            json_data_list (list): 要写入的JSON数据列表，每个元素可以是单个对象或列表
        """
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

### 2.8 百度对象存储工具 (utils/bos.py)

```python
import os
import logging
import concurrent.futures
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union, Any

# Import Baidu BOS SDK
try:
    from baidubce.bce_client_configuration import BceClientConfiguration
    from baidubce.auth.bce_credentials import BceCredentials
    from baidubce.services.bos.bos_client import BosClient
    from baidubce import exception
except ImportError:
    raise ImportError(
        "Baidu BOS SDK is required. Please install it using: "
        "pip install bce-python-sdk"
    )


class BosHelper:
    """
    Helper class for Baidu Object Storage (BOS) operations.
    Supports concurrent upload and download of files.
    """

    def __init__(
        self,
        access_key_id: str = None,
        secret_access_key: str = None,
        endpoint: str = None,
        bucket: str = None,
        max_workers: int = None,
    ):
        """
        Initialize BOS Helper.

        Args:
            access_key_id (str, optional): BOS access key ID. Defaults to env var BOS_ACCESS_KEY.
            secret_access_key (str, optional): BOS secret access key. Defaults to env var BOS_SECRET_KEY.
            endpoint (str, optional): BOS endpoint. Defaults to env var BOS_HOST or 'bj.bcebos.com'.
            bucket (str, optional): Default bucket name. Defaults to env var BOS_BUCKET.
            max_workers (int, optional): Maximum number of worker threads/processes for concurrent operations.
        """
        self.access_key_id = access_key_id or os.environ.get("BOS_ACCESS_KEY")
        self.secret_access_key = secret_access_key or os.environ.get("BOS_SECRET_KEY")
        self.endpoint = endpoint or os.environ.get("BOS_HOST", "bj.bcebos.com")
        self.bucket = bucket or os.environ.get("BOS_BUCKET")
        self.max_workers = max_workers
        self.client = self._create_client()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for BOS operations."""
        logger = logging.getLogger("jsonflow.utils.bos")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _create_client(self) -> BosClient:
        """Create and return a BOS client."""
        if not self.access_key_id or not self.secret_access_key:
            raise ValueError(
                "BOS credentials not provided. Set access_key_id and secret_access_key "
                "or environment variables BOS_ACCESS_KEY and BOS_SECRET_KEY."
            )

        config = BceClientConfiguration(
            credentials=BceCredentials(self.access_key_id, self.secret_access_key),
            endpoint=self.endpoint,
        )
        return BosClient(config)

    def upload_file(
        self, local_file: str, remote_key: str, bucket: str = None
    ) -> Tuple[bool, str]:
        """
        Upload a single file to BOS.

        Args:
            local_file (str): Path to local file
            remote_key (str): Remote object key
            bucket (str, optional): Bucket name. Defaults to self.bucket.

        Returns:
            Tuple[bool, str]: (success, remote_url)
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        if not os.path.exists(local_file):
            self.logger.error(f"File not found: {local_file}")
            return False, ""

        try:
            self.client.put_object_from_file(bucket, remote_key, local_file)
            remote_url = f"https://{bucket}.{self.endpoint}/{remote_key}"
            self.logger.info(f"Uploaded: {local_file} -> {remote_url}")
            return True, remote_url
        except exception.BceHttpClientError as e:
            self.logger.error(f"Upload failed: {local_file} - {str(e)}")
            return False, ""

    def download_file(
        self, remote_key: str, local_file: str, bucket: str = None
    ) -> bool:
        """
        Download a single file from BOS.

        Args:
            remote_key (str): Remote object key
            local_file (str): Path to save the downloaded file
            bucket (str, optional): Bucket name. Defaults to self.bucket.

        Returns:
            bool: Success status
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(local_file)), exist_ok=True)
            
            # Download the file
            self.client.get_object_to_file(bucket, remote_key, local_file)
            self.logger.info(f"Downloaded: {remote_key} -> {local_file}")
            return True
        except exception.BceHttpClientError as e:
            self.logger.error(f"Download failed: {remote_key} - {str(e)}")
            return False
    
    def upload_directory(
        self,
        local_dir: str,
        remote_base_path: str,
        bucket: str = None,
        include_pattern: str = None,
        exclude_pattern: str = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Upload a directory to BOS with concurrent workers.

        Args:
            local_dir (str): Local directory path
            remote_base_path (str): Remote base path
            bucket (str, optional): Bucket name. Defaults to self.bucket.
            include_pattern (str, optional): Pattern to include files.
            exclude_pattern (str, optional): Pattern to exclude files.

        Returns:
            Tuple[List[str], List[str]]: (uploaded_urls, failed_files)
        """
        # Implementation omitted for brevity, handles concurrent uploads

    def download_directory(
        self,
        remote_prefix: str,
        local_dir: str,
        bucket: str = None,
        include_pattern: str = None,
        exclude_pattern: str = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Download a directory from BOS with concurrent workers.

        Args:
            remote_prefix (str): Remote directory prefix
            local_dir (str): Local directory path
            bucket (str, optional): Bucket name. Defaults to self.bucket.
            include_pattern (str, optional): Pattern to include files.
            exclude_pattern (str, optional): Pattern to exclude files.

        Returns:
            Tuple[List[str], List[str]]: (downloaded_files, failed_keys)
        """
        # Implementation omitted for brevity, handles concurrent downloads

    def check_bucket_exists(self, bucket: str = None) -> bool:
        """Check if a bucket exists."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")
        
        try:
            self.client.list_objects(bucket, max_keys=1)
            return True
        except exception.BceHttpClientError:
            return False

    def create_bucket(self, bucket: str = None) -> bool:
        """Create a new bucket if it doesn't exist."""
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")
        
        try:
            if not self.check_bucket_exists(bucket):
                self.client.create_bucket(bucket)
                self.logger.info(f"Bucket created: {bucket}")
            return True
        except exception.BceHttpClientError as e:
            self.logger.error(f"Failed to create bucket: {bucket} - {str(e)}")
            return False


# Convenience functions
def upload_file(
    local_file: str,
    remote_key: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
) -> Tuple[bool, str]:
    """Convenience function to upload a file without creating a BosHelper instance."""
    helper = BosHelper(access_key_id, secret_access_key, endpoint, bucket)
    return helper.upload_file(local_file, remote_key)

def download_file(
    remote_key: str,
    local_file: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
) -> bool:
    """Convenience function to download a file without creating a BosHelper instance."""
    helper = BosHelper(access_key_id, secret_access_key, endpoint, bucket)
    return helper.download_file(remote_key, local_file)

def upload_directory(
    local_dir: str,
    remote_base_path: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
    max_workers: int = None,
) -> Tuple[List[str], List[str]]:
    """Convenience function to upload a directory without creating a BosHelper instance."""
    helper = BosHelper(access_key_id, secret_access_key, endpoint, bucket, max_workers)
    return helper.upload_directory(local_dir, remote_base_path)

def download_directory(
    remote_prefix: str,
    local_dir: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
    max_workers: int = None,
) -> Tuple[List[str], List[str]]:
    """Convenience function to download a directory without creating a BosHelper instance."""
    helper = BosHelper(access_key_id, secret_access_key, endpoint, bucket, max_workers)
    return helper.download_directory(remote_prefix, local_dir)
```

### 2.9 BOS操作符 (operators/json_ops/bos_ops.py)

可以考虑添加BOS操作符，利用BosHelper功能：

```python
from jsonflow.core import JsonOperator
from jsonflow.utils.bos import BosHelper

class BosUploader(JsonOperator):
    """上传JSON数据中指定字段的文件到BOS的操作符"""
    
    def __init__(
        self, 
        file_field, 
        remote_key_field=None, 
        result_field='bos_url',
        access_key_id=None, 
        secret_access_key=None, 
        endpoint=None, 
        bucket=None,
        name=None
    ):
        """
        初始化BosUploader
        
        Args:
            file_field (str): JSON中包含本地文件路径的字段名
            remote_key_field (str, optional): JSON中包含远程键的字段名，如果为None则自动生成
            result_field (str, optional): 存储上传结果URL的字段名
            access_key_id (str, optional): BOS访问密钥ID
            secret_access_key (str, optional): BOS访问密钥
            endpoint (str, optional): BOS端点
            bucket (str, optional): 存储桶名称
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Upload file in {file_field} field to BOS")
        self.file_field = file_field
        self.remote_key_field = remote_key_field
        self.result_field = result_field
        self.bos_helper = BosHelper(access_key_id, secret_access_key, endpoint, bucket)
    
    def process(self, json_data):
        """处理JSON数据，上传文件并添加URL结果"""
        result = json_data.copy()
        
        # 获取本地文件路径
        if self.file_field not in result:
            return result
        
        local_file = result[self.file_field]
        
        # 获取或生成远程键
        if self.remote_key_field and self.remote_key_field in result:
            remote_key = result[self.remote_key_field]
        else:
            # 使用文件名作为远程键
            import os
            remote_key = os.path.basename(local_file)
        
        # 上传文件
        success, url = self.bos_helper.upload_file(local_file, remote_key)
        
        # 添加结果URL到JSON数据
        if success:
            result[self.result_field] = url
        
        return result


class BosDownloader(JsonOperator):
    """从BOS下载JSON数据中指定字段URL的文件的操作符"""
    
    def __init__(
        self, 
        url_field, 
        local_file_field='local_file',
        access_key_id=None, 
        secret_access_key=None, 
        endpoint=None, 
        bucket=None,
        name=None
    ):
        """
        初始化BosDownloader
        
        Args:
            url_field (str): JSON中包含BOS URL的字段名
            local_file_field (str, optional): 存储本地文件路径的字段名
            access_key_id (str, optional): BOS访问密钥ID
            secret_access_key (str, optional): BOS访问密钥
            endpoint (str, optional): BOS端点
            bucket (str, optional): 存储桶名称
            name (str, optional): 操作符名称
        """
        super().__init__(name, f"Download file from BOS URL in {url_field} field")
        self.url_field = url_field
        self.local_file_field = local_file_field
        self.bos_helper = BosHelper(access_key_id, secret_access_key, endpoint, bucket)
    
    def process(self, json_data):
        """处理JSON数据，下载文件并添加本地文件路径"""
        result = json_data.copy()
        
        # 获取BOS URL
        if self.url_field not in result:
            return result
        
        bos_url = result[self.url_field]
        
        # 从URL提取远程键和存储桶
        import os
        import re
        
        # 解析BOS URL获取bucket和key
        url_pattern = r'https://([^.]+)\.([^/]+)/(.+)'
        match = re.match(url_pattern, bos_url)
        
        if not match:
            return result
        
        bucket, endpoint, remote_key = match.groups()
        
        # 确定本地文件路径
        local_file = os.path.join('/tmp', os.path.basename(remote_key))
        
        # 下载文件
        success = self.bos_helper.download_file(remote_key, local_file, bucket)
        
        # 添加本地文件路径到JSON数据
        if success:
            result[self.local_file_field] = local_file
        
        return result
```

这个设计建议添加BOS相关的操作符，使其能够与JsonFlow的Pipeline无缝集成，提供文件上传下载功能。

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