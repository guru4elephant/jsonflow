"""
调试管道示例

这个示例展示了如何创建一个Pipeline并打印每个操作符的输入和输出，便于调试和开发。
"""

import json
from jsonflow.core import Pipeline, JsonOperator
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer, JsonFilter, JsonTransformer
from jsonflow.utils import get_logger

# 获取日志记录器
logger = get_logger("debug_pipeline")

# 创建一个打印输入输出的操作符包装器
class DebugOperator(JsonOperator):
    """
    操作符包装器，用于打印操作符的输入和输出
    """
    
    def __init__(self, operator, name=None):
        """
        初始化DebugOperator
        
        Args:
            operator: 被包装的操作符
            name: 操作符名称，默认为被包装操作符的名称
        """
        self.operator = operator
        super().__init__(
            name or f"Debug({operator.name})",
            f"Debug wrapper for {operator.name}"
        )
    
    def process(self, json_data):
        """
        处理JSON数据，并打印输入和输出
        """
        logger.info(f"[{self.operator.name}] 输入: {json.dumps(json_data, ensure_ascii=False)}")
        result = self.operator.process(json_data)
        logger.info(f"[{self.operator.name}] 输出: {json.dumps(result, ensure_ascii=False)}")
        return result

# 示例JSON转换操作符
class SentimentAnalyzer(JsonOperator):
    """
    模拟情感分析操作符
    """
    
    def __init__(self, text_field="prompt", sentiment_field="sentiment", name=None):
        super().__init__(
            name or "SentimentAnalyzer",
            "Analyzes sentiment in text"
        )
        self.text_field = text_field
        self.sentiment_field = sentiment_field
    
    def process(self, json_data):
        if not json_data or self.text_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field].lower()
        
        # 简单的关键词匹配情感分析
        positive_words = ["good", "great", "excellent", "happy", "love", "wonderful", "joke"]
        negative_words = ["bad", "terrible", "sad", "hate", "awful", "difficult", "problem"]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        result[self.sentiment_field] = sentiment
        return result

def run_debug_pipeline(input_file="input.jsonl", output_file="debug_output.jsonl"):
    """
    运行一个调试Pipeline，打印每个操作符的输入和输出
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    logger.info("创建调试Pipeline...")
    
    # 创建操作符
    text_normalizer = TextNormalizer(text_fields=["prompt"])
    sentiment_analyzer = SentimentAnalyzer()
    metadata_enricher = JsonTransformer(
        add_fields={
            "processed_at": "2025-05-01T12:00:00Z",
            "version": "1.0"
        }
    )
    category_extractor = JsonTransformer(
        add_fields={
            "category": lambda x: x.get("metadata", {}).get("type", "unknown")
        }
    )
    
    # 创建Pipeline，使用DebugOperator包装每个操作符
    pipeline = Pipeline([
        DebugOperator(text_normalizer),
        DebugOperator(sentiment_analyzer),
        DebugOperator(metadata_enricher),
        DebugOperator(category_extractor)
    ])
    
    logger.info(f"Pipeline创建完成，包含 {len(pipeline)} 个操作符")
    
    # 从文件加载JSON数据
    logger.info(f"从 {input_file} 加载数据...")
    loader = JsonLoader(input_file)
    
    # 保存处理结果
    saver = JsonSaver(output_file)
    
    # 处理每一行JSON数据
    logger.info("开始处理数据...")
    count = 0
    
    for json_line in loader:
        logger.info(f"\n--- 处理第 {count + 1} 条数据 ---")
        
        # 逐个操作符处理数据
        result = pipeline.process(json_line)
        
        # 保存最终结果
        saver.write(result)
        count += 1
        
        logger.info(f"--- 第 {count} 条数据处理完成 ---\n")
    
    logger.info(f"所有数据处理完成，共处理 {count} 条数据，结果保存到 {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行调试Pipeline，打印每个操作符的输入和输出")
    parser.add_argument("--input", default="input.jsonl", help="输入文件路径")
    parser.add_argument("--output", default="debug_output.jsonl", help="输出文件路径")
    
    args = parser.parse_args()
    
    run_debug_pipeline(args.input, args.output) 