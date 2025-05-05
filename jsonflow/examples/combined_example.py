"""
组合功能示例

该示例演示如何结合使用JSONFlow的字段透传和系统字段功能。
"""

from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.json_ops import IdAdder, TimestampAdder
from jsonflow.operators.model import ModelInvoker

def run_combined_example():
    """演示字段透传和系统字段的组合使用"""
    
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
        
    print("处理完成，已添加系统字段并设置为透传字段")

if __name__ == "__main__":
    run_combined_example() 