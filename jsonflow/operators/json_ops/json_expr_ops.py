"""
JSON表达式操作符模块

该模块提供了使用Python表达式和函数更简洁地操作JSON数据的操作符。
"""

from typing import Dict, Any, List, Optional, Union, Callable, Set
import re
import operator as op

from jsonflow.core import JsonOperator

class JsonExpressionOperator(JsonOperator):
    """
    JSON表达式操作符
    
    该操作符使用Python表达式或函数来处理JSON数据，提供更接近Python原生的操作方式。
    """
    
    def __init__(self, 
                 expressions: Dict[str, Union[str, Callable]],
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonExpressionOperator
        
        Args:
            expressions (dict): 表达式映射，键为目标字段，值为表达式字符串或函数
                表达式字符串中可以使用 $ 符号引用JSON字段，例如 $.user.name
                也可以提供一个函数，接收json_data作为参数
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            
        示例:
            expressions = {
                "full_name": "$.user.first_name + ' ' + $.user.last_name",
                "item_count": "len($.items)",
                "has_orders": "$.order_count > 0",
                "email_domain": lambda data: data.get("email", "").split("@")[-1] if "@" in data.get("email", "") else ""
            }
        """
        super().__init__(
            name or "JsonExpressionOperator",
            description or "Applies expressions to JSON data"
        )
        self.expressions = expressions
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，应用表达式
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data:
            return {}
        
        result = json_data.copy()
        
        for target_field, expression in self.expressions.items():
            try:
                # 处理函数表达式
                if callable(expression):
                    value = expression(json_data)
                    self._set_nested_value(result, target_field, value)
                    continue
                
                # 处理字符串表达式
                value = self._evaluate_expression(expression, json_data)
                self._set_nested_value(result, target_field, value)
            except Exception as e:
                # 表达式求值失败时忽略，可以选择记录错误
                print(f"表达式求值错误(字段: {target_field}): {str(e)}")
                continue
        
        return result
    
    def _evaluate_expression(self, expression: str, json_data: Dict[str, Any]) -> Any:
        """
        求值表达式
        
        Args:
            expression (str): 表达式字符串
            json_data (dict): JSON数据
            
        Returns:
            any: 表达式求值结果
        """
        # 替换表达式中的字段引用
        expr = self._replace_field_references(expression, json_data)
        
        # 创建安全的本地环境
        safe_locals = {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "abs": abs,
            "round": round,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "all": all,
            "any": any,
            # 添加一些字符串操作
            "lower": lambda s: s.lower() if isinstance(s, str) else s,
            "upper": lambda s: s.upper() if isinstance(s, str) else s,
            "strip": lambda s: s.strip() if isinstance(s, str) else s,
            "split": lambda s, sep=" ": s.split(sep) if isinstance(s, str) else [],
            "join": lambda l, sep="": sep.join(l) if isinstance(l, list) else "",
            "replace": lambda s, old, new: s.replace(old, new) if isinstance(s, str) else s,
            "startswith": lambda s, prefix: s.startswith(prefix) if isinstance(s, str) else False,
            "endswith": lambda s, suffix: s.endswith(suffix) if isinstance(s, str) else False,
        }
        
        # 使用eval求值表达式
        # 注意：在实际生产环境中应该小心使用eval，这里假设表达式是可信的
        return eval(expr, {"__builtins__": {}}, safe_locals)
    
    def _replace_field_references(self, expression: str, json_data: Dict[str, Any]) -> str:
        """
        替换表达式中的字段引用
        
        Args:
            expression (str): 表达式字符串
            json_data (dict): JSON数据
            
        Returns:
            str: 替换后的表达式
        """
        # 查找所有字段引用，支持点号路径
        pattern = r'\$\.[a-zA-Z0-9_.[\]]+|\$\[[\'"]([^\'"]+)[\'"]\]'
        
        def replace_match(match):
            ref = match.group(0)
            if ref.startswith('$['):
                # 处理 $["field"]
                field = ref[3:-2]
                value = json_data.get(field)
            else:
                # 处理 $.field.subfield
                parts = ref[2:].split('.')
                value = json_data
                for part in parts:
                    if part and '[' in part and ']' in part:
                        # 处理数组索引，如items[0]
                        arr_name, idx_str = part.split('[', 1)
                        idx = int(idx_str.rstrip(']'))
                        if isinstance(value, dict) and arr_name in value:
                            arr = value[arr_name]
                            if isinstance(arr, list) and 0 <= idx < len(arr):
                                value = arr[idx]
                            else:
                                return "None"
                        else:
                            return "None"
                    elif isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return "None"  # 字段不存在
            
            # 替换不同类型的值
            if isinstance(value, str):
                return f"'{value}'"
            elif value is None:
                return "None"
            elif isinstance(value, (list, dict)):
                # 对复杂类型使用repr
                return repr(value)
            else:
                # 数字和布尔值
                return str(value)
        
        return re.sub(pattern, replace_match, expression)
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """
        设置嵌套字段的值
        
        Args:
            data (dict): 要修改的数据
            path (str): 字段路径，可以是点号分隔的路径
            value (any): 要设置的值
        """
        if '.' not in path:
            data[path] = value
            return
        
        parts = path.split('.')
        current = data
        
        # 创建嵌套结构
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # 如果不是字典，转换为字典
                current[part] = {}
            current = current[part]
        
        # 设置值
        current[parts[-1]] = value


class JsonFieldMapper(JsonExpressionOperator):
    """
    JSON字段映射操作符
    
    该操作符简化了字段映射和简单转换的创建过程。
    """
    
    def __init__(self,
                 mappings: Dict[str, Union[str, Callable]],
                 name: Optional[str] = None):
        """
        初始化JsonFieldMapper
        
        Args:
            mappings (dict): 字段映射，键为目标字段，值为源字段路径或转换函数
                源字段路径可以使用点号表示嵌套结构
                也可以提供一个接收value参数的简单转换函数
            name (str, optional): 操作符名称
            
        示例:
            mappings = {
                "customer_name": "user.name",                      # 简单映射
                "email_verified": "user.verified",                 # 简单映射
                "item_names": "items[*].name",                     # 数组映射
                "total_cost": lambda data: sum(item.get('price', 0) * item.get('quantity', 0) for item in data.get('items', [])),  # 计算函数
            }
        """
        # 将映射转换为表达式
        expressions = {}
        for target, source in mappings.items():
            if callable(source):
                # 直接使用函数
                expressions[target] = source
            elif isinstance(source, str):
                if '[*]' in source:
                    # 处理数组映射
                    array_path, field = source.split('[*]', 1)
                    if field.startswith('.'):
                        field = field[1:]
                    
                    def array_mapper(data, path=array_path, field_name=field):
                        array = self._get_by_path(data, path)
                        if not isinstance(array, list):
                            return []
                        if not field_name:
                            return array
                        return [self._get_by_path(item, field_name) for item in array]
                    
                    expressions[target] = array_mapper
                else:
                    # 简单字段引用
                    expressions[target] = f"$.{source}"
        
        super().__init__(
            expressions,
            name or "JsonFieldMapper",
            "Maps JSON fields using simple path expressions"
        )
    
    def _get_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        通过路径获取值
        
        Args:
            data (dict): JSON数据
            path (str): 字段路径
            
        Returns:
            any: 字段值
        """
        if not path:
            return data
        
        parts = path.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value


class JsonTemplateOperator(JsonOperator):
    """
    JSON模板操作符
    
    该操作符使用模板字符串来格式化JSON数据中的值。
    """
    
    def __init__(self, 
                 templates: Dict[str, str],
                 name: Optional[str] = None,
                 description: Optional[str] = None):
        """
        初始化JsonTemplateOperator
        
        Args:
            templates (dict): 模板映射，键为目标字段，值为模板字符串
                模板字符串中可以使用 {field.path} 格式引用JSON字段
            name (str, optional): 操作符名称
            description (str, optional): 操作符描述
            
        示例:
            templates = {
                "user.display_name": "{user.first_name} {user.last_name}",
                "order.summary": "Order #{order.id} - {order.items|length} items, total: ${order.total}",
                "metadata.description": "{metadata.title|upper}: {metadata.content|truncate:100}"
            }
        """
        super().__init__(
            name or "JsonTemplateOperator",
            description or "Applies string templates to JSON data"
        )
        self.templates = templates
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理JSON数据，应用模板
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        if not json_data:
            return {}
        
        result = json_data.copy()
        
        for target_field, template in self.templates.items():
            try:
                # 解析模板并替换字段引用
                value = self._render_template(template, json_data)
                
                # 设置目标字段
                self._set_nested_value(result, target_field, value)
            except Exception as e:
                # 模板渲染失败时忽略
                print(f"模板渲染错误(字段: {target_field}): {str(e)}")
                continue
        
        return result
    
    def _render_template(self, template: str, json_data: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template (str): 模板字符串
            json_data (dict): JSON数据
            
        Returns:
            str: 渲染后的字符串
        """
        # 查找所有字段引用
        pattern = r'\{([^{}|]+)(?:\|([^{}]+))?\}'
        
        def replace_field(match):
            field_path = match.group(1).strip()
            modifiers = match.group(2).strip() if match.group(2) else None
            
            # 获取字段值
            value = self._get_by_path(json_data, field_path)
            
            # 应用修饰符
            if modifiers:
                value = self._apply_modifiers(value, modifiers)
            
            return str(value) if value is not None else ""
        
        return re.sub(pattern, replace_field, template)
    
    def _get_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        通过路径获取值
        
        Args:
            data (dict): JSON数据
            path (str): 字段路径，支持简单的数组索引，如items[0]
            
        Returns:
            any: 字段值
        """
        parts = path.split('.')
        value = data
        
        for part in parts:
            if '[' in part and ']' in part:
                # 处理数组索引
                name, idx_str = part.split('[', 1)
                idx = int(idx_str.rstrip(']'))
                
                if isinstance(value, dict) and name in value:
                    array = value[name]
                    if isinstance(array, list) and 0 <= idx < len(array):
                        value = array[idx]
                    else:
                        return None
                else:
                    return None
            elif isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _apply_modifiers(self, value: Any, modifiers: str) -> Any:
        """
        应用修饰符
        
        Args:
            value (any): 字段值
            modifiers (str): 修饰符字符串，如 "upper", "truncate:100"
            
        Returns:
            any: 修改后的值
        """
        for modifier in modifiers.split('|'):
            modifier = modifier.strip()
            if not modifier:
                continue
            
            # 处理带参数的修饰符
            if ':' in modifier:
                name, args = modifier.split(':', 1)
                args = args.split(',')
            else:
                name = modifier
                args = []
            
            # 应用修饰符
            if name == 'upper' and isinstance(value, str):
                value = value.upper()
            elif name == 'lower' and isinstance(value, str):
                value = value.lower()
            elif name == 'title' and isinstance(value, str):
                value = value.title()
            elif name == 'strip' and isinstance(value, str):
                value = value.strip()
            elif name == 'truncate' and isinstance(value, str) and args:
                length = int(args[0])
                suffix = args[1] if len(args) > 1 else '...'
                if len(value) > length:
                    value = value[:length] + suffix
            elif name == 'default' and args:
                if value is None:
                    value = args[0]
            elif name == 'length':
                if isinstance(value, (list, dict, str)):
                    value = len(value)
                else:
                    value = 0
            elif name == 'join' and isinstance(value, list):
                separator = args[0] if args else ''
                value = separator.join(str(item) for item in value)
        
        return value
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """
        设置嵌套字段的值
        
        Args:
            data (dict): 要修改的数据
            path (str): 字段路径，可以是点号分隔的路径
            value (any): 要设置的值
        """
        if '.' not in path:
            data[path] = value
            return
        
        parts = path.split('.')
        current = data
        
        # 创建嵌套结构
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # 如果不是字典，转换为字典
                current[part] = {}
            current = current[part]
        
        # 设置值
        current[parts[-1]] = value 