"""
操作符日志示例

这个示例展示了如何使用系统级别的操作符输入输出日志功能。
"""

from jsonflow.core import Pipeline, JsonOperator
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonTransformer
from jsonflow.utils import (
    get_logger, 
    enable_operator_io_logging, 
    set_io_log_indent, 
    set_io_log_truncate_length
)

# 获取日志记录器
logger = get_logger("operator_logging")

# 自定义操作符示例
class KeywordExtractor(JsonOperator):
    """关键词提取操作符"""
    
    def __init__(self, text_field="prompt", keywords_field="keywords", name=None):
        super().__init__(
            name or "KeywordExtractor",
            "Extracts keywords from text"
        )
        self.text_field = text_field
        self.keywords_field = keywords_field
        # 添加停用词列表
        self.stopwords = {"a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "and", "in", "that", "me", "what"}
    
    def process(self, json_data):
        if not json_data or self.text_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field].lower()
        
        # 过滤停用词
        words = [word.strip(".,?!") for word in text.split()]
        keywords = [word for word in words if word and word not in self.stopwords]
        
        result[self.keywords_field] = keywords
        return result

def run_operator_logging_example(input_file="input.jsonl", output_file="logging_output.jsonl"):
    """
    运行操作符日志示例
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    logger.info("=== 操作符日志示例 ===")
    
    # 第一阶段: 不启用操作符IO日志
    logger.info("\n--- 阶段1: 不启用操作符IO日志 ---")
    
    # 创建Pipeline
    pipeline1 = Pipeline([
        TextNormalizer(strip=True, lower_case=True),
        KeywordExtractor(),
        JsonTransformer(add_fields={"stage": "无日志"})
    ])
    
    # 处理一个示例JSON
    sample_data = {
        "id": 1,
        "prompt": "What is the meaning of life? How to find happiness and purpose?",
        "metadata": {"type": "philosophy"}
    }
    
    logger.info("处理数据...")
    result1 = pipeline1.process(sample_data)
    logger.info(f"处理结果: ID={result1.get('id')}, 关键词数量={len(result1.get('keywords', []))}")
    
    # 第二阶段: 启用操作符IO日志
    logger.info("\n--- 阶段2: 启用操作符IO日志 ---")
    enable_operator_io_logging(True)
    set_io_log_indent(2)
    
    # 创建新的Pipeline
    pipeline2 = Pipeline([
        TextNormalizer(strip=True, lower_case=True),
        KeywordExtractor(),
        JsonTransformer(add_fields={"stage": "启用日志"})
    ])
    
    logger.info("处理数据...")
    result2 = pipeline2.process(sample_data)
    logger.info(f"处理结果: ID={result2.get('id')}, 关键词数量={len(result2.get('keywords', []))}")
    
    # 第三阶段: 设置截断长度
    logger.info("\n--- 阶段3: 设置日志截断 ---")
    set_io_log_truncate_length(100)  # 设置截断长度为100字符
    
    # 创建大量数据的示例
    large_sample = sample_data.copy()
    large_sample["large_field"] = "x" * 200  # 添加一个大字段
    
    logger.info("处理大数据...")
    result3 = pipeline2.process(large_sample)
    
    # 第四阶段: 禁用操作符IO日志
    logger.info("\n--- 阶段4: 禁用操作符IO日志 ---")
    enable_operator_io_logging(False)
    
    logger.info("处理数据...")
    result4 = pipeline2.process(sample_data)
    logger.info(f"处理结果: ID={result4.get('id')}, 关键词数量={len(result4.get('keywords', []))}")
    
    logger.info("\n日志示例结束")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行操作符日志示例")
    parser.add_argument("--input", default="input.jsonl", help="输入文件路径")
    parser.add_argument("--output", default="logging_output.jsonl", help="输出文件路径")
    
    args = parser.parse_args()
    
    run_operator_logging_example(args.input, args.output) 