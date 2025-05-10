"""
JSON操作符模块

该模块包含各种用于处理JSON数据的操作符。
"""

# 导入所有JSON操作相关的操作符
from jsonflow.operators.json_ops.text_normalizer import TextNormalizer
from jsonflow.operators.json_ops.json_filter import JsonFilter
from jsonflow.operators.json_ops.json_transformer import JsonTransformer
from jsonflow.operators.json_ops.json_field_ops import (
    JsonFieldSelector,
    JsonPathOperator,
    JsonPathExtractor,
    JsonPathUpdater,
    JsonPathRemover,
    JsonStringOperator,
    JsonStructureExtractor,
    JsonArrayOperator,
    JsonMerger
)
from jsonflow.operators.json_ops.json_expr_ops import (
    JsonExpressionOperator,
    JsonFieldMapper,
    JsonTemplateOperator
)
from jsonflow.operators.json_ops.system_field_ops import (
    IdAdder, 
    TimestampAdder, 
    DateTimeAdder, 
    CustomFieldAdder, 
    FieldRemover
)
from jsonflow.operators.json_ops.collection_ops import (
    JsonSplitter,
    JsonAggregator
)

# 导出所有操作符
__all__ = [
    'TextNormalizer',
    'JsonFilter',
    'JsonTransformer',
    'JsonFieldSelector',
    'JsonPathOperator',
    'JsonPathExtractor',
    'JsonPathUpdater',
    'JsonPathRemover',
    'JsonStringOperator',
    'JsonStructureExtractor',
    'JsonArrayOperator',
    'JsonMerger',
    'JsonExpressionOperator',
    'JsonFieldMapper',
    'JsonTemplateOperator',
    'IdAdder',
    'TimestampAdder',
    'DateTimeAdder',
    'CustomFieldAdder',
    'FieldRemover',
    'JsonSplitter',
    'JsonAggregator'
] 