"""
系统字段示例

该示例演示如何使用JSONFlow的系统字段功能。
"""

from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.json_ops import IdAdder, TimestampAdder
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