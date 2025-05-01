"""
JSON字段操作符模块

该模块定义了一系列用于JSON字段操作的操作符，如选择、提取、更新等。
"""

from typing import Dict, Any, List, Optional, Union, Callable, Tuple, Set

from jsonflow.core import JsonOperator

class JsonFieldSelector(JsonOperator):
    """
    JSON字段选择操作符
    
    该操作符可以从JSON数据中选择特定字段，可以扁平化嵌套结构，支持多级路径选择。
    """
    
    def __init__(self, 
                 fields: List[str],
                 flatten: bool = False,
                 prefix: str = "",
                 default_value: Any = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonFieldSelector
        
        Args:
            fields (list): 要选择的字段列表，支持点号分隔的路径，如"metadata.type"
            flatten (bool): 是否扁平化嵌套结构，默认为False
            prefix (str): 扁平化时的字段前缀
            default_value (any): 字段不存在时的默认值
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonFieldSelector",
            description or "Selects specific fields from JSON data"
        )
        self.fields = fields
        self.flatten = flatten
        self.prefix = prefix
        self.default_value = default_value
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，选择指定字段
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 选择字段后的JSON数据
        """
        if not json_data:
            return {}
        
        result = {}
        
        for field in self.fields:
            # 处理点号分隔的路径
            if "." in field:
                parts = field.split(".")
                value = json_data
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = self.default_value
                        break
                
                if self.flatten:
                    # 扁平化: metadata.type -> metadata_type
                    flat_field = self.prefix + field.replace(".", "_")
                    result[flat_field] = value
                else:
                    # 创建嵌套结构
                    current = result
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
            else:
                # 简单字段
                if field in json_data:
                    result[field] = json_data[field]
                else:
                    result[field] = self.default_value
        
        return result


class JsonPathOperator(JsonOperator):
    """
    JSON路径操作符基类
    
    该操作符可以基于路径对JSON数据进行操作，支持点号分隔的路径。
    """
    
    def __init__(self, name: Optional[str] = None, description: Optional[str] = None):
        """
        初始化JsonPathOperator
        
        Args:
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonPathOperator",
            description or "Operates on JSON data using paths"
        )
    
    def _get_value_by_path(self, data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """
        通过路径获取值
        
        Args:
            data (dict): JSON数据
            path (str): 点号分隔的路径
            default (any): 默认值
            
        Returns:
            any: 路径对应的值或默认值
        """
        parts = path.split(".")
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def _set_value_by_path(self, data: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
        """
        通过路径设置值
        
        Args:
            data (dict): JSON数据
            path (str): 点号分隔的路径
            value (any): 要设置的值
            
        Returns:
            dict: 设置后的JSON数据
        """
        result = data.copy()
        parts = path.split(".")
        
        # 处理嵌套路径
        if len(parts) > 1:
            current = result
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            # 顶层字段
            result[path] = value
        
        return result
    
    def _delete_by_path(self, data: Dict[str, Any], path: str) -> Dict[str, Any]:
        """
        通过路径删除值
        
        Args:
            data (dict): JSON数据
            path (str): 点号分隔的路径
            
        Returns:
            dict: 删除后的JSON数据
        """
        result = data.copy()
        parts = path.split(".")
        
        # 处理嵌套路径
        if len(parts) > 1:
            current = result
            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    # 路径不存在，无需删除
                    return result
                current = current[part]
            
            if parts[-1] in current:
                del current[parts[-1]]
        else:
            # 顶层字段
            if path in result:
                del result[path]
        
        return result


class JsonPathExtractor(JsonPathOperator):
    """
    JSON路径提取操作符
    
    该操作符可以从JSON数据中提取指定路径的值。
    """
    
    def __init__(self, 
                 paths: Dict[str, str],
                 default_value: Any = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonPathExtractor
        
        Args:
            paths (dict): 路径映射，键为目标字段名，值为源路径
            default_value (any): 路径不存在时的默认值
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonPathExtractor",
            description or "Extracts values from JSON data using paths"
        )
        self.paths = paths
        self.default_value = default_value
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，提取指定路径的值
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 提取值后的JSON数据
        """
        if not json_data:
            return {}
        
        result = {}
        
        for target_field, source_path in self.paths.items():
            result[target_field] = self._get_value_by_path(json_data, source_path, self.default_value)
        
        return result


class JsonPathUpdater(JsonPathOperator):
    """
    JSON路径更新操作符
    
    该操作符可以更新JSON数据中指定路径的值。
    """
    
    def __init__(self, 
                 updates: Dict[str, Any],
                 create_missing: bool = True,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonPathUpdater
        
        Args:
            updates (dict): 更新映射，键为路径，值为新值
            create_missing (bool): 是否创建不存在的路径，默认为True
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonPathUpdater",
            description or "Updates values in JSON data using paths"
        )
        self.updates = updates
        self.create_missing = create_missing
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，更新指定路径的值
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 更新后的JSON数据
        """
        if not json_data:
            return json_data
        
        result = json_data.copy()
        
        for path, value in self.updates.items():
            # 如果值是可调用的，使用JSON数据调用它
            if callable(value):
                computed_value = value(json_data)
            else:
                computed_value = value
            
            # 获取当前路径的值
            current_value = self._get_value_by_path(result, path)
            
            # 如果路径不存在且不创建缺失路径，则跳过
            if current_value is None and not self.create_missing:
                continue
            
            # 更新值
            result = self._set_value_by_path(result, path, computed_value)
        
        return result


class JsonPathRemover(JsonPathOperator):
    """
    JSON路径删除操作符
    
    该操作符可以删除JSON数据中指定路径的字段。
    """
    
    def __init__(self, 
                 paths: List[str],
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonPathRemover
        
        Args:
            paths (list): 要删除的路径列表
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonPathRemover",
            description or "Removes fields from JSON data using paths"
        )
        self.paths = paths
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，删除指定路径的字段
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 删除字段后的JSON数据
        """
        if not json_data:
            return json_data
        
        result = json_data.copy()
        
        for path in self.paths:
            result = self._delete_by_path(result, path)
        
        return result


class JsonStringOperator(JsonPathOperator):
    """
    JSON字符串操作符
    
    该操作符可以基于JSON数据中的字段进行字符串操作，生成新字段。
    """
    
    # 预定义的字符串操作类型
    STRING_OPS = {
        "concat": lambda vals: "".join(str(v) for v in vals),
        "join": lambda vals, sep="": sep.join(str(v) for v in vals),
        "upper": lambda vals: str(vals[0]).upper() if vals else "",
        "lower": lambda vals: str(vals[0]).lower() if vals else "",
        "strip": lambda vals: str(vals[0]).strip() if vals else "",
        "replace": lambda vals, old="", new="": str(vals[0]).replace(old, new) if vals else "",
        "split": lambda vals, sep=" ", index=None: (str(vals[0]).split(sep)[index] if index is not None else str(vals[0]).split(sep)) if vals else [],
        "format": lambda vals, template="{}": template.format(*[str(v) for v in vals]),
        "substring": lambda vals, start=0, end=None: str(vals[0])[start:end] if vals else "",
        "trim": lambda vals, max_len=None, suffix="...": (str(vals[0])[:max_len] + suffix if len(str(vals[0])) > max_len else str(vals[0])) if vals and max_len else str(vals[0]) if vals else ""
    }
    
    def __init__(self, 
                 operations: Dict[str, Dict[str, Any]],
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonStringOperator
        
        Args:
            operations (dict): 字符串操作配置，格式为{目标字段: 操作配置}
                操作配置包括：
                - "sources": 源字段路径列表
                - "op": 操作类型，如"concat", "join", "upper", "lower", "replace", "split", "format", "substring", "trim"
                - 操作特有的参数，如"sep"（连接符）, "template"（格式模板）, "old"/"new"（替换参数）等
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            
        示例:
            operations = {
                "full_name": {
                    "sources": ["user.first_name", "user.last_name"],
                    "op": "join",
                    "sep": " "
                },
                "email_domain": {
                    "sources": ["user.email"],
                    "op": "split",
                    "sep": "@",
                    "index": 1
                }
            }
        """
        super().__init__(
            name or "JsonStringOperator",
            description or "Performs string operations on JSON fields"
        )
        self.operations = operations
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，应用字符串操作
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data:
            return json_data
        
        result = json_data.copy()
        
        for target_field, operation in self.operations.items():
            # 获取源字段值
            source_values = []
            for source_path in operation.get("sources", []):
                value = self._get_value_by_path(json_data, source_path)
                source_values.append(value if value is not None else "")
            
            # 获取操作类型
            op_type = operation.get("op", "concat")
            if op_type not in self.STRING_OPS:
                # 不支持的操作类型
                continue
            
            # 创建操作参数
            op_args = {k: v for k, v in operation.items() if k not in ["sources", "op"]}
            
            # 应用操作
            try:
                # 根据操作类型和参数执行字符串操作
                if op_args:
                    result_value = self.STRING_OPS[op_type](source_values, **op_args)
                else:
                    result_value = self.STRING_OPS[op_type](source_values)
                
                # 更新目标字段
                result = self._set_value_by_path(result, target_field, result_value)
            except Exception as e:
                # 操作失败时保持原值不变
                continue
        
        return result
    
    @classmethod
    def concat_fields(cls, sources: List[str], target: str, separator: str = "", name: Optional[str] = None) -> 'JsonStringOperator':
        """
        创建一个字段连接操作符
        
        Args:
            sources (list): 源字段路径列表
            target (str): 目标字段路径
            separator (str): 连接符
            name (str, optional): 操作符名称
            
        Returns:
            JsonStringOperator: 新的JsonStringOperator实例
        """
        operations = {
            target: {
                "sources": sources,
                "op": "join",
                "sep": separator
            }
        }
        return cls(operations, name or f"StringConcat({target})")
    
    @classmethod
    def format_string(cls, sources: List[str], target: str, template: str, name: Optional[str] = None) -> 'JsonStringOperator':
        """
        创建一个字符串格式化操作符
        
        Args:
            sources (list): 源字段路径列表，用于填充模板
            target (str): 目标字段路径
            template (str): 格式模板，如"{} <{}>"
            name (str, optional): 操作符名称
            
        Returns:
            JsonStringOperator: 新的JsonStringOperator实例
        """
        operations = {
            target: {
                "sources": sources,
                "op": "format",
                "template": template
            }
        }
        return cls(operations, name or f"StringFormat({target})")


class JsonArrayOperator(JsonOperator):
    """
    JSON数组操作符
    
    该操作符可以对JSON数据中的数组字段进行操作，如过滤、映射、排序等。
    """
    
    def __init__(self, 
                 field: str,
                 operation: str = "map",
                 func: Optional[Callable] = None,
                 output_field: Optional[str] = None,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonArrayOperator
        
        Args:
            field (str): 数组字段名，支持点号分隔的路径
            operation (str): 操作类型，支持"map"、"filter"、"sort"
            func (callable): 操作函数
            output_field (str): 输出字段名，默认为None，表示覆盖原字段
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or f"JsonArrayOperator({operation})",
            description or f"Performs {operation} operation on array field"
        )
        self.field = field
        self.operation = operation
        self.func = func
        self.output_field = output_field or field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，对数组字段应用操作
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data:
            return json_data
        
        result = json_data.copy()
        
        # 获取数组字段
        parts = self.field.split(".")
        target = result
        for i, part in enumerate(parts[:-1]):
            if part not in target:
                # 路径不存在
                return result
            target = target[part]
        
        last_part = parts[-1]
        if last_part not in target or not isinstance(target[last_part], list):
            # 不是数组字段
            return result
        
        array_value = target[last_part]
        
        # 应用操作
        if self.operation == "map" and self.func:
            new_array = [self.func(item) for item in array_value]
        elif self.operation == "filter" and self.func:
            new_array = [item for item in array_value if self.func(item)]
        elif self.operation == "sort" and self.func:
            new_array = sorted(array_value, key=self.func)
        elif self.operation == "sort" and not self.func:
            new_array = sorted(array_value)
        else:
            # 不支持的操作
            return result
        
        # 更新数组
        if self.output_field == self.field:
            # 原地更新
            target[last_part] = new_array
        else:
            # 创建新字段
            output_parts = self.output_field.split(".")
            output_target = result
            for i, part in enumerate(output_parts[:-1]):
                if part not in output_target:
                    output_target[part] = {}
                output_target = output_target[part]
            
            output_target[output_parts[-1]] = new_array
        
        return result


class JsonMerger(JsonOperator):
    """
    JSON合并操作符
    
    该操作符可以合并多个JSON数据或将新字段合并到现有数据中。
    """
    
    def __init__(self, 
                 data_to_merge: Optional[Dict[str, Any]] = None,
                 overwrite: bool = True,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonMerger
        
        Args:
            data_to_merge (dict): 要合并的JSON数据，默认为None
            overwrite (bool): 是否覆盖现有字段，默认为True
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonMerger",
            description or "Merges JSON data"
        )
        self.data_to_merge = data_to_merge or {}
        self.overwrite = overwrite
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，合并数据
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 合并后的JSON数据
        """
        if not json_data:
            return self.data_to_merge.copy() if self.data_to_merge else {}
        
        result = json_data.copy()
        
        # 合并数据
        for key, value in self.data_to_merge.items():
            if key not in result or self.overwrite:
                # 字段不存在或允许覆盖
                if callable(value):
                    result[key] = value(json_data)
                else:
                    result[key] = value
        
        return result


class JsonStructureExtractor(JsonOperator):
    """
    JSON结构提取操作符
    
    该操作符可以提取JSON数据的键结构，包括所有路径和类型信息。
    """
    
    def __init__(self, 
                 include_types: bool = True,
                 max_depth: Optional[int] = None,
                 include_arrays: bool = True,
                 target_field: str = "structure",
                 flatten: bool = False,
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonStructureExtractor
        
        Args:
            include_types (bool): 是否包含值类型信息，默认为True
            max_depth (int, optional): 最大嵌套深度，默认为None（无限制）
            include_arrays (bool): 是否包含数组索引，默认为True
            target_field (str): 存储结构信息的目标字段，默认为"structure"
            flatten (bool): 是否返回扁平化的路径列表而非嵌套结构，默认为False
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
        """
        super().__init__(
            name or "JsonStructureExtractor",
            description or "Extracts the key structure of JSON data"
        )
        self.include_types = include_types
        self.max_depth = max_depth
        self.include_arrays = include_arrays
        self.target_field = target_field
        self.flatten = flatten
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，提取键结构
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 添加了结构信息的JSON数据
        """
        if not json_data:
            result = {}
            result[self.target_field] = {} if not self.flatten else []
            return result
        
        result = json_data.copy()
        
        # 提取结构
        if self.flatten:
            # 扁平化路径列表
            paths = []
            self._extract_flat_paths(json_data, "", paths)
            result[self.target_field] = paths
        else:
            # 嵌套结构
            structure = self._extract_structure(json_data)
            result[self.target_field] = structure
        
        return result
    
    def _extract_flat_paths(self, data: Any, current_path: str, paths: List[str], current_depth: int = 0) -> None:
        """
        提取扁平化的路径列表
        
        Args:
            data (any): 当前数据节点
            current_path (str): 当前路径
            paths (list): 路径列表，用于存储结果
            current_depth (int): 当前深度
        """
        # 检查深度限制
        if self.max_depth is not None and current_depth > self.max_depth:
            return
        
        # 处理不同类型的数据
        if isinstance(data, dict):
            # 如果是空字典且当前路径不为空，添加当前路径
            if not data and current_path:
                path_info = current_path
                if self.include_types:
                    path_info = f"{path_info} (object)"
                paths.append(path_info)
                return
            
            # 遍历字典
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                self._extract_flat_paths(value, new_path, paths, current_depth + 1)
        
        elif isinstance(data, list):
            # 如果是空列表且当前路径不为空，添加当前路径
            if not data and current_path:
                path_info = current_path
                if self.include_types:
                    path_info = f"{path_info} (array)"
                paths.append(path_info)
                return
            
            # 处理数组
            if self.include_arrays:
                for i, item in enumerate(data):
                    new_path = f"{current_path}[{i}]"
                    self._extract_flat_paths(item, new_path, paths, current_depth + 1)
            else:
                # 只处理第一个元素作为示例
                if data:
                    new_path = f"{current_path}[]"
                    self._extract_flat_paths(data[0], new_path, paths, current_depth + 1)
        
        else:
            # 叶子节点
            if current_path:
                path_info = current_path
                if self.include_types:
                    type_name = type(data).__name__
                    path_info = f"{path_info} ({type_name})"
                paths.append(path_info)
    
    def _extract_structure(self, data: Any, current_depth: int = 0) -> Dict[str, Any]:
        """
        提取嵌套结构
        
        Args:
            data (any): 当前数据节点
            current_depth (int): 当前深度
            
        Returns:
            dict: 结构信息
        """
        # 检查深度限制
        if self.max_depth is not None and current_depth > self.max_depth:
            return {"type": "max_depth_reached"}
        
        # 处理不同类型的数据
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self._extract_structure(value, current_depth + 1)
            
            if self.include_types:
                result["__type__"] = "object"
            return result
        
        elif isinstance(data, list):
            if not data:
                result = {}
                if self.include_types:
                    result["__type__"] = "array"
                    result["__items__"] = "unknown"
                return result
            
            if self.include_arrays:
                result = {}
                for i, item in enumerate(data):
                    result[f"[{i}]"] = self._extract_structure(item, current_depth + 1)
                
                if self.include_types:
                    result["__type__"] = "array"
                return result
            else:
                # 只处理第一个元素作为示例
                result = {"items": self._extract_structure(data[0], current_depth + 1)}
                if self.include_types:
                    result["__type__"] = "array"
                return result
        
        else:
            # 叶子节点
            if self.include_types:
                return {"__type__": type(data).__name__, "__value__": str(data)}
            else:
                return {"__value__": str(data)} 