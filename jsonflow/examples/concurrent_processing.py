"""
并发处理示例

这个示例展示了如何使用并发执行器处理大量JSON数据。
"""

from jsonflow.core import Pipeline, MultiThreadExecutor, JsonOperator
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonFilter
from jsonflow.utils import get_logger

# 获取日志记录器
logger = get_logger("concurrent_processing")

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

def run_concurrent_pipeline(input_file="input.jsonl", output_file="output.jsonl", max_workers=4):
    """
    使用并发执行器运行Pipeline
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        max_workers (int): 最大工作线程数
    """
    logger.info("创建Pipeline...")
    
    # 创建一个管道
    pipeline = Pipeline([
        JsonFilter(filter_func=lambda x: "prompt" in x, name="PromptFilter"),
        TextNormalizer(text_fields=["prompt"], name="TextNormalizer"),
        MockModelOperator(name="MockGPT")
    ])
    
    logger.info(f"Pipeline创建完成，包含 {len(pipeline)} 个操作符")
    for op in pipeline:
        logger.info(f"- {op.name}: {op.description}")
    
    # 创建一个多线程执行器
    executor = MultiThreadExecutor(pipeline, max_workers=max_workers)
    logger.info(f"创建多线程执行器，最大工作线程数: {max_workers}")
    
    # 从文件加载所有JSON数据
    logger.info(f"从 {input_file} 加载数据...")
    loader = JsonLoader(input_file)
    json_data_list = loader.load()
    logger.info(f"加载完成，共 {len(json_data_list)} 条数据")
    
    # 并发处理所有数据
    logger.info("开始并发处理数据...")
    results = executor.execute_all(json_data_list)
    logger.info(f"处理完成，共 {len(results)} 条结果")
    
    # 保存处理结果
    logger.info(f"保存结果到 {output_file}...")
    saver = JsonSaver(output_file)
    saver.write_all(results)
    logger.info("保存完成")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="使用并发执行器处理JSON数据")
    parser.add_argument("--input", default="input.jsonl", help="输入文件路径")
    parser.add_argument("--output", default="output.jsonl", help="输出文件路径")
    parser.add_argument("--workers", type=int, default=4, help="最大工作线程数")
    args = parser.parse_args()
    
    run_concurrent_pipeline(args.input, args.output, args.workers) 