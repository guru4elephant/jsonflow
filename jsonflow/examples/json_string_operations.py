"""
JSON字符串操作示例

这个示例展示了如何使用JsonStringOperator对JSON字段进行字符串操作并生成新字段。
"""

from jsonflow.core import Pipeline
from jsonflow.utils import get_logger, enable_operator_io_logging
from jsonflow.operators.json_ops import (
    JsonStringOperator,
    JsonPathExtractor
)

# 启用操作符输入输出日志
enable_operator_io_logging(True)

# 获取日志记录器
logger = get_logger("json_string_operations")

def run_json_string_operations_example():
    """
    运行JSON字符串操作示例
    """
    logger.info("=== JSON字符串操作示例 ===")
    
    # 创建示例JSON数据
    sample_data = {
        "user": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        },
        "content": {
            "title": "Introduction to JSON Processing",
            "tags": ["json", "data", "processing"],
            "summary": "A comprehensive guide to processing JSON data with various techniques."
        },
        "metadata": {
            "created_at": "2023-06-15T12:30:00Z",
            "views": 1250,
            "rating": 4.8
        }
    }
    
    logger.info("\n--- 示例1: 字段拼接 ---")
    # 创建字段拼接操作符
    concat_operator = JsonStringOperator.concat_fields(
        sources=["user.first_name", "user.last_name"],
        target="user.full_name",
        separator=" ",
        name="姓名拼接器"
    )
    
    # 处理数据
    result1 = concat_operator.process(sample_data)
    logger.info(f"拼接后的全名: {result1['user']['full_name']}")
    
    logger.info("\n--- 示例2: 多种字符串操作 ---")
    # 创建多种字符串操作
    string_ops = JsonStringOperator(
        operations={
            # 提取邮箱域名
            "user.email_domain": {
                "sources": ["user.email"],
                "op": "split",
                "sep": "@",
                "index": 1
            },
            # 标题大写
            "content.title_uppercase": {
                "sources": ["content.title"],
                "op": "upper"
            },
            # 标签拼接
            "content.tags_string": {
                "sources": ["content.tags"],
                "op": "join",
                "sep": ", "
            },
            # 截断摘要
            "content.short_summary": {
                "sources": ["content.summary"],
                "op": "trim",
                "max_len": 30,
                "suffix": "..."
            }
        },
        name="字符串操作集"
    )
    
    # 处理数据
    result2 = string_ops.process(result1)
    logger.info(f"邮箱域名: {result2['user']['email_domain']}")
    logger.info(f"大写标题: {result2['content']['title_uppercase']}")
    logger.info(f"标签字符串: {result2['content']['tags_string']}")
    logger.info(f"截断摘要: {result2['content']['short_summary']}")
    
    logger.info("\n--- 示例3: 字符串格式化 ---")
    # 创建字符串格式化操作符
    format_operator = JsonStringOperator.format_string(
        sources=["user.full_name", "user.email"],
        target="user.display_info",
        template="{} <{}>",
        name="用户信息格式化器"
    )
    
    # 处理数据
    result3 = format_operator.process(result2)
    logger.info(f"格式化的用户信息: {result3['user']['display_info']}")
    
    logger.info("\n--- 示例4: 更复杂的字符串操作 ---")
    # 创建更复杂的字符串操作
    complex_ops = JsonStringOperator(
        operations={
            # 替换操作
            "content.clean_title": {
                "sources": ["content.title"],
                "op": "replace",
                "old": "JSON",
                "new": "JavaScript Object Notation"
            },
            # 格式化元数据
            "metadata.formatted_stats": {
                "sources": ["metadata.views", "metadata.rating"],
                "op": "format",
                "template": "浏览量: {}, 评分: {}/5.0"
            },
            # 创建格式化的日期时间
            "metadata.formatted_date": {
                "sources": ["metadata.created_at"],
                "op": "split",
                "sep": "T",
                "index": 0
            }
        },
        name="复杂字符串操作"
    )
    
    # 处理数据
    result4 = complex_ops.process(result3)
    logger.info(f"清洁标题: {result4['content']['clean_title']}")
    logger.info(f"格式化统计: {result4['metadata']['formatted_stats']}")
    logger.info(f"格式化日期: {result4['metadata']['formatted_date']}")
    
    logger.info("\n--- 示例5: 管道操作 ---")
    # 创建提取和格式化管道
    extract_op = JsonPathExtractor(
        paths={
            "title": "content.title",
            "author": "user.full_name",
            "date": "metadata.created_at"
        },
        name="字段提取器"
    )
    
    format_op = JsonStringOperator(
        operations={
            "formatted_article": {
                "sources": ["title", "author", "date"],
                "op": "format",
                "template": "《{}》 by {} (published on {})"
            }
        },
        name="文章信息格式化器"
    )
    
    # 创建管道
    pipeline = Pipeline([extract_op, format_op])
    
    # 处理数据
    result5 = pipeline.process(result4)
    logger.info(f"格式化文章信息: {result5['formatted_article']}")
    
    logger.info("\n=== 示例结束 ===")

if __name__ == "__main__":
    run_json_string_operations_example() 