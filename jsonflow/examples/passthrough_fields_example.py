"""
透传字段示例

该示例演示如何使用JSONFlow的字段透传功能。
"""

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