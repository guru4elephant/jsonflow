"""
自定义操作符链示例

这个示例展示了如何创建多个自定义操作符并将它们链接在一起，同时打印每一步的输入和输出。
"""

import json
from jsonflow.core import Pipeline, JsonOperator
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.utils import get_logger

# 获取日志记录器
logger = get_logger("custom_operator_chain")

# 定义一个日志装饰器，用于记录操作符的输入和输出
def log_io(func):
    """
    装饰器：记录操作符的输入和输出
    """
    def wrapper(self, json_data):
        logger.info(f"\n[{self.name}] 输入:\n{json.dumps(json_data, ensure_ascii=False, indent=2)}")
        result = func(self, json_data)
        logger.info(f"[{self.name}] 输出:\n{json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    return wrapper

# 第一个自定义操作符：文本预处理
class TextPreprocessor(JsonOperator):
    """
    文本预处理操作符
    
    对文本字段进行预处理，包括去除多余空格、标准化标点符号等。
    """
    
    def __init__(self, text_field="prompt", name=None):
        super().__init__(
            name or "TextPreprocessor",
            "Preprocesses text field"
        )
        self.text_field = text_field
    
    @log_io
    def process(self, json_data):
        if not json_data or self.text_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field]
        
        # 执行预处理
        # 1. 标准化空白字符
        text = " ".join(text.split())
        # 2. 标准化标点符号
        for char, replacement in [("?", " ? "), ("!", " ! "), (".", " . "), (",", " , ")]:
            text = text.replace(char, replacement)
        # 3. 再次标准化空白字符
        text = " ".join(text.split())
        
        result[self.text_field] = text
        return result

# 第二个自定义操作符：分词器
class Tokenizer(JsonOperator):
    """
    分词器操作符
    
    将文本字段分割为标记（token）。
    """
    
    def __init__(self, text_field="prompt", tokens_field="tokens", name=None):
        super().__init__(
            name or "Tokenizer",
            "Tokenizes text field"
        )
        self.text_field = text_field
        self.tokens_field = tokens_field
    
    @log_io
    def process(self, json_data):
        if not json_data or self.text_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field]
        
        # 简单分词
        tokens = text.split()
        
        result[self.tokens_field] = tokens
        return result

# 第三个自定义操作符：统计分析器
class TokenAnalyzer(JsonOperator):
    """
    标记分析器
    
    对分词结果进行统计分析，计算词频、平均长度等。
    """
    
    def __init__(self, tokens_field="tokens", stats_field="token_stats", name=None):
        super().__init__(
            name or "TokenAnalyzer",
            "Analyzes token statistics"
        )
        self.tokens_field = tokens_field
        self.stats_field = stats_field
    
    @log_io
    def process(self, json_data):
        if not json_data or self.tokens_field not in json_data:
            return json_data
        
        result = json_data.copy()
        tokens = result[self.tokens_field]
        
        # 计算统计数据
        token_count = len(tokens)
        unique_tokens = len(set(tokens))
        
        if token_count > 0:
            avg_length = sum(len(t) for t in tokens) / token_count
        else:
            avg_length = 0
        
        # 计算词频
        token_freq = {}
        for token in tokens:
            token_freq[token] = token_freq.get(token, 0) + 1
        
        # 排序后的词频
        sorted_freq = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)
        top_tokens = sorted_freq[:5]
        
        # 组装统计结果
        stats = {
            "token_count": token_count,
            "unique_tokens": unique_tokens,
            "avg_token_length": round(avg_length, 2),
            "top_tokens": {t: f for t, f in top_tokens},
            "token_frequency": {t: f for t, f in sorted_freq}
        }
        
        result[self.stats_field] = stats
        return result

# 第四个自定义操作符：复杂度分析器
class ComplexityAnalyzer(JsonOperator):
    """
    复杂度分析器
    
    分析文本的复杂度，如平均句子长度、词汇多样性等。
    """
    
    def __init__(self, text_field="prompt", tokens_field="tokens", 
                complexity_field="complexity", name=None):
        super().__init__(
            name or "ComplexityAnalyzer",
            "Analyzes text complexity"
        )
        self.text_field = text_field
        self.tokens_field = tokens_field
        self.complexity_field = complexity_field
    
    @log_io
    def process(self, json_data):
        if not json_data or self.text_field not in json_data or self.tokens_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field]
        tokens = result[self.tokens_field]
        
        # 分析句子
        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        sentence_count = len(sentences)
        
        # 计算复杂度指标
        if sentence_count > 0:
            avg_sentence_length = len(tokens) / sentence_count
        else:
            avg_sentence_length = 0
        
        if len(tokens) > 0:
            lexical_diversity = len(set(tokens)) / len(tokens)
        else:
            lexical_diversity = 0
        
        # 评估复杂度级别
        if avg_sentence_length > 15:
            complexity_level = "high"
        elif avg_sentence_length > 10:
            complexity_level = "medium"
        else:
            complexity_level = "low"
        
        # 组装复杂度分析结果
        complexity = {
            "sentence_count": sentence_count,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "lexical_diversity": round(lexical_diversity, 2),
            "complexity_level": complexity_level
        }
        
        result[self.complexity_field] = complexity
        return result

# 第五个自定义操作符：元数据生成器
class MetadataGenerator(JsonOperator):
    """
    元数据生成器
    
    根据前面的分析结果生成综合元数据。
    """
    
    def __init__(self, stats_field="token_stats", complexity_field="complexity", 
                metadata_field="analysis_metadata", name=None):
        super().__init__(
            name or "MetadataGenerator",
            "Generates analysis metadata"
        )
        self.stats_field = stats_field
        self.complexity_field = complexity_field
        self.metadata_field = metadata_field
    
    @log_io
    def process(self, json_data):
        if not json_data:
            return json_data
        
        result = json_data.copy()
        stats = result.get(self.stats_field, {})
        complexity = result.get(self.complexity_field, {})
        
        # 生成综合元数据
        metadata = {
            "timestamp": "2025-05-01T16:00:00Z",
            "version": "1.0",
            "summary": {
                "token_count": stats.get("token_count", 0),
                "sentence_count": complexity.get("sentence_count", 0),
                "complexity_level": complexity.get("complexity_level", "unknown"),
                "top_tokens": list(stats.get("top_tokens", {}).keys())
            }
        }
        
        result[self.metadata_field] = metadata
        return result

def run_custom_operator_chain(input_file="input.jsonl", output_file="custom_chain_output.jsonl"):
    """
    运行自定义操作符链示例
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    logger.info("创建自定义操作符链...")
    
    # 创建操作符
    text_preprocessor = TextPreprocessor()
    tokenizer = Tokenizer()
    token_analyzer = TokenAnalyzer()
    complexity_analyzer = ComplexityAnalyzer()
    metadata_generator = MetadataGenerator()
    
    # 创建Pipeline
    pipeline = Pipeline([
        text_preprocessor,
        tokenizer,
        token_analyzer,
        complexity_analyzer,
        metadata_generator
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
        logger.info(f"\n=== 处理第 {count + 1} 条数据 ===")
        
        # 处理数据
        result = pipeline.process(json_line)
        
        # 保存结果
        saver.write(result)
        count += 1
        
        logger.info(f"=== 第 {count} 条数据处理完成 ===\n")
    
    logger.info(f"所有数据处理完成，共处理 {count} 条数据，结果保存到 {output_file}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行自定义操作符链示例")
    parser.add_argument("--input", default="input.jsonl", help="输入文件路径")
    parser.add_argument("--output", default="custom_chain_output.jsonl", help="输出文件路径")
    
    args = parser.parse_args()
    
    run_custom_operator_chain(args.input, args.output) 