"""
简单管道示例

这个示例展示了如何创建一个简单的Pipeline并处理JSON数据。
"""

from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker
from jsonflow.utils import get_logger
from jsonflow.core import JsonOperator

# 获取日志记录器
logger = get_logger("simple_pipeline")

# 创建一个模拟模型调用的操作符
class MockModelOperator(JsonOperator):
    """
    模拟模型调用的操作符，用于示例演示
    """
    
    def __init__(self, prompt_field="prompt", response_field="response", name=None, description=None):
        super().__init__(
            name or "MockModel",
            description or "Simulates a model response"
        )
        self.prompt_field = prompt_field
        self.response_field = response_field
    
    def process(self, json_data):
        """模拟处理JSON数据，生成响应"""
        if not json_data or self.prompt_field not in json_data:
            return json_data
        
        result = json_data.copy()
        prompt = result[self.prompt_field]
        
        # 生成模拟响应
        if "joke" in prompt.lower():
            response = "Why don't scientists trust atoms? Because they make up everything!"
        elif "meaning of life" in prompt.lower():
            response = "The meaning of life is 42, according to The Hitchhiker's Guide to the Galaxy."
        elif "chocolate cake" in prompt.lower():
            response = "To make a chocolate cake, you need flour, sugar, cocoa powder, eggs, milk, and butter. Mix dry ingredients, add wet ingredients, bake at 350°F for 30 minutes."
        elif "quantum physics" in prompt.lower():
            response = "Quantum physics is the study of matter and energy at its most fundamental level. It describes how particles behave at the atomic and subatomic level, often in ways that seem counterintuitive to our everyday experience."
        else:
            response = f"This is a simulated response to: {prompt}"
        
        result[self.response_field] = response
        return result

def run_simple_pipeline(input_file="input.jsonl", output_file="output.jsonl"):
    """
    运行一个简单的Pipeline
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    logger.info("创建Pipeline...")
    
    # 创建一个简单管道
    pipeline = Pipeline([
        TextNormalizer(text_fields=["prompt"], name="TextNormalizer"),
        # 使用模拟模型操作符替代实际的ModelInvoker
        MockModelOperator(name="MockGPT")
    ])
    
    logger.info(f"Pipeline创建完成，包含 {len(pipeline)} 个操作符")
    for op in pipeline:
        logger.info(f"- {op.name}: {op.description}")
    
    # 从文件加载JSON数据
    logger.info(f"从 {input_file} 加载数据...")
    loader = JsonLoader(input_file)
    
    # 保存处理结果
    saver = JsonSaver(output_file)
    
    # 处理每一行JSON数据
    logger.info("开始处理数据...")
    count = 0
    for json_line in loader:
        logger.debug(f"处理第 {count + 1} 条数据: {json_line}")
        result = pipeline.process(json_line)
        saver.write(result)
        count += 1
    
    logger.info(f"处理完成，共处理 {count} 条数据，结果保存到 {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行一个简单的Pipeline处理JSON数据")
    parser.add_argument("--input", default="input.jsonl", help="输入文件路径")
    parser.add_argument("--output", default="output.jsonl", help="输出文件路径")
    args = parser.parse_args()
    
    run_simple_pipeline(args.input, args.output) 