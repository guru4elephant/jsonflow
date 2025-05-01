"""
交互式开发示例

这个示例展示了如何在开发过程中交互式地构建、测试和改进操作符。
"""

import json
import sys
from jsonflow.core import Pipeline, JsonOperator
from jsonflow.operators.json_ops import TextNormalizer, JsonTransformer
from jsonflow.utils import get_logger

# 获取日志记录器
logger = get_logger("interactive_development")

class DevelopmentContext:
    """
    开发上下文，用于交互式开发和测试操作符
    """
    
    def __init__(self, sample_data):
        """
        初始化开发上下文
        
        Args:
            sample_data (dict): 示例JSON数据
        """
        self.sample_data = sample_data
        self.history = [("初始数据", sample_data)]
    
    def test_operator(self, operator, description=None):
        """
        测试单个操作符
        
        Args:
            operator: 要测试的操作符
            description (str, optional): 测试说明
        
        Returns:
            dict: 操作符处理后的数据
        """
        logger.info(f"\n=== 测试操作符: {operator.name} ===")
        if description:
            logger.info(f"说明: {description}")
        
        input_data = self.history[-1][1]
        logger.info(f"输入: {json.dumps(input_data, ensure_ascii=False, indent=2)}")
        
        try:
            result = operator.process(input_data)
            logger.info(f"输出: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 记录历史
            self.history.append((operator.name, result))
            return result
        except Exception as e:
            logger.error(f"错误: {e}")
            return None
    
    def show_history(self):
        """
        显示处理历史
        """
        logger.info("\n=== 处理历史 ===")
        for i, (name, data) in enumerate(self.history):
            logger.info(f"{i+1}. {name}")
    
    def compare_results(self, step1, step2):
        """
        比较两个处理步骤的结果
        
        Args:
            step1 (int): 第一个步骤索引（1开始）
            step2 (int): 第二个步骤索引（1开始）
        """
        if step1 < 1 or step1 > len(self.history) or step2 < 1 or step2 > len(self.history):
            logger.error("步骤索引超出范围")
            return
        
        name1, data1 = self.history[step1-1]
        name2, data2 = self.history[step2-1]
        
        logger.info(f"\n=== 比较结果: {name1} vs {name2} ===")
        
        # 获取所有键
        all_keys = set(data1.keys()) | set(data2.keys())
        
        for key in sorted(all_keys):
            value1 = data1.get(key, "<不存在>")
            value2 = data2.get(key, "<不存在>")
            
            if value1 != value2:
                logger.info(f"- {key}:")
                logger.info(f"  步骤{step1} ({name1}): {value1}")
                logger.info(f"  步骤{step2} ({name2}): {value2}")

# 自定义操作符示例 - 第一个版本（有Bug）
class KeywordExtractor_v1(JsonOperator):
    """关键词提取操作符 - 版本1 (有Bug)"""
    
    def __init__(self, text_field="prompt", keywords_field="keywords", name=None):
        super().__init__(
            name or "KeywordExtractor_v1",
            "Extracts keywords from text (version 1)"
        )
        self.text_field = text_field
        self.keywords_field = keywords_field
    
    def process(self, json_data):
        if not json_data or self.text_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field]
        
        # Bug: 不会过滤停用词，直接分割所有单词
        keywords = [word.strip(".,?!") for word in text.split()]
        
        result[self.keywords_field] = keywords
        return result

# 自定义操作符示例 - 第二个版本（修复Bug）
class KeywordExtractor_v2(JsonOperator):
    """关键词提取操作符 - 版本2 (修复Bug)"""
    
    def __init__(self, text_field="prompt", keywords_field="keywords", name=None):
        super().__init__(
            name or "KeywordExtractor_v2",
            "Extracts keywords from text (version 2)"
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
        
        # 修复: 过滤停用词
        words = [word.strip(".,?!") for word in text.split()]
        keywords = [word for word in words if word and word not in self.stopwords]
        
        result[self.keywords_field] = keywords
        return result

# 自定义操作符示例 - 最终版本（添加功能）
class KeywordExtractor_v3(JsonOperator):
    """关键词提取操作符 - 版本3 (添加功能)"""
    
    def __init__(self, text_field="prompt", keywords_field="keywords", min_length=3, name=None):
        super().__init__(
            name or "KeywordExtractor_v3",
            "Extracts keywords from text (version 3)"
        )
        self.text_field = text_field
        self.keywords_field = keywords_field
        self.min_length = min_length
        # 添加停用词列表
        self.stopwords = {"a", "an", "the", "is", "are", "was", "were", "be", "to", "of", "and", "in", "that", "me", "what", "how"}
    
    def process(self, json_data):
        if not json_data or self.text_field not in json_data:
            return json_data
        
        result = json_data.copy()
        text = result[self.text_field].lower()
        
        # 过滤停用词，并增加最小长度限制
        words = [word.strip(".,?!") for word in text.split()]
        keywords = [word for word in words if word and word not in self.stopwords and len(word) >= self.min_length]
        
        # 添加新功能：包含频率统计
        keyword_counts = {}
        for keyword in keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # 按频率排序
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        
        result[self.keywords_field] = [k for k, v in sorted_keywords]
        result[f"{self.keywords_field}_with_counts"] = {k: v for k, v in sorted_keywords}
        
        return result

def run_interactive_development():
    """
    运行交互式开发示例
    """
    logger.info("开始交互式开发示例...")
    
    # 创建示例数据
    sample_data = {
        "id": 1,
        "prompt": "What is the meaning of life? How to find purpose and happiness?",
        "metadata": {
            "type": "philosophy",
            "length": "medium"
        }
    }
    
    # 创建开发上下文
    dev_context = DevelopmentContext(sample_data)
    
    # 步骤1: 测试文本规范化
    text_normalizer = TextNormalizer(strip=True, lower_case=True)
    dev_context.test_operator(text_normalizer, "规范化文本，去除多余空格并转换为小写")
    
    # 步骤2: 测试第一版关键词提取器
    keyword_extractor_v1 = KeywordExtractor_v1()
    dev_context.test_operator(keyword_extractor_v1, "提取关键词 - 初始版本")
    
    # 步骤3: 测试改进的关键词提取器
    keyword_extractor_v2 = KeywordExtractor_v2()
    dev_context.test_operator(keyword_extractor_v2, "提取关键词 - 过滤停用词")
    
    # 步骤4: 测试最终版本的关键词提取器
    keyword_extractor_v3 = KeywordExtractor_v3(min_length=4)
    dev_context.test_operator(keyword_extractor_v3, "提取关键词 - 增加最小长度并添加频率统计")
    
    # 步骤5: 添加元数据
    metadata_enricher = JsonTransformer(
        add_fields={
            "analysis_timestamp": "2025-05-01T15:45:00Z",
            "analysis_version": "3.0"
        }
    )
    dev_context.test_operator(metadata_enricher, "添加分析元数据")
    
    # 显示处理历史
    dev_context.show_history()
    
    # 比较不同版本的结果
    logger.info("\n=== 比较不同版本的关键词提取器 ===")
    dev_context.compare_results(3, 4)  # 比较v1和v2版本
    dev_context.compare_results(4, 5)  # 比较v2和v3版本
    
    # 创建最终的Pipeline
    logger.info("\n=== 创建最终Pipeline ===")
    final_pipeline = Pipeline([
        TextNormalizer(strip=True, lower_case=True),
        KeywordExtractor_v3(min_length=4),
        JsonTransformer(
            add_fields={
                "analysis_timestamp": "2025-05-01T15:45:00Z",
                "analysis_version": "3.0"
            }
        )
    ])
    
    # 处理原始示例数据
    final_result = final_pipeline.process(sample_data)
    logger.info(f"最终Pipeline结果:\n{json.dumps(final_result, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    run_interactive_development() 