"""
JSON结构提取示例

这个示例展示了如何使用JsonStructureExtractor操作符提取JSON数据的键结构。
"""

import json
from jsonflow.core import Pipeline
from jsonflow.utils import get_logger, enable_operator_io_logging
from jsonflow.operators.json_ops import JsonStructureExtractor

# 启用操作符输入输出日志
enable_operator_io_logging(True)

# 获取日志记录器
logger = get_logger("json_structure_extraction")

def run_json_structure_extraction_example():
    """
    运行JSON结构提取示例
    """
    logger.info("=== JSON结构提取示例 ===")
    
    # 创建示例JSON数据，包含多种类型和嵌套结构
    sample_data = {
        "id": 12345,
        "user": {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "profile": {
                "age": 30,
                "occupation": "Software Engineer",
                "skills": ["Python", "JavaScript", "SQL"]
            },
            "active": True
        },
        "orders": [
            {
                "order_id": "ORD-001",
                "items": [
                    {"product": "Laptop", "price": 1299.99, "quantity": 1},
                    {"product": "Mouse", "price": 25.99, "quantity": 2}
                ],
                "total": 1351.97,
                "status": "shipped"
            },
            {
                "order_id": "ORD-002",
                "items": [
                    {"product": "Monitor", "price": 349.99, "quantity": 1}
                ],
                "total": 349.99,
                "status": "processing"
            }
        ],
        "metadata": {
            "created_at": "2023-06-15T10:30:00Z",
            "tags": ["customer", "active"],
            "notes": None
        }
    }
    
    logger.info("\n--- 示例1: 扁平化结构提取 ---")
    # 创建扁平化结构提取操作符
    flat_structure_extractor = JsonStructureExtractor(
        include_types=True,
        flatten=True,
        name="扁平化结构提取器"
    )
    
    # 处理数据
    result1 = flat_structure_extractor.process(sample_data)
    
    # 输出扁平化路径列表
    logger.info("扁平化路径列表:")
    for path in result1["structure"]:
        logger.info(f"  - {path}")
    
    logger.info("\n--- 示例2: 嵌套结构提取 ---")
    # 创建嵌套结构提取操作符
    nested_structure_extractor = JsonStructureExtractor(
        include_types=True,
        flatten=False,
        target_field="schema",
        name="嵌套结构提取器"
    )
    
    # 处理数据
    result2 = nested_structure_extractor.process(sample_data)
    
    # 输出嵌套结构
    logger.info("嵌套结构:")
    logger.info(json.dumps(result2["schema"], indent=2, ensure_ascii=False))
    
    logger.info("\n--- 示例3: 简化结构提取（无数组索引）---")
    # 创建简化结构提取操作符
    simplified_structure_extractor = JsonStructureExtractor(
        include_types=True,
        include_arrays=False,
        flatten=True,
        target_field="paths",
        name="简化结构提取器"
    )
    
    # 处理数据
    result3 = simplified_structure_extractor.process(sample_data)
    
    # 输出简化结构
    logger.info("简化路径列表:")
    for path in result3["paths"]:
        logger.info(f"  - {path}")
    
    logger.info("\n--- 示例4: 深度限制结构提取 ---")
    # 创建深度限制结构提取操作符
    depth_limited_extractor = JsonStructureExtractor(
        include_types=True,
        max_depth=2,
        flatten=True,
        target_field="limited_paths",
        name="深度限制结构提取器"
    )
    
    # 处理数据
    result4 = depth_limited_extractor.process(sample_data)
    
    # 输出深度限制结构
    logger.info("深度限制的路径列表 (max_depth=2):")
    for path in result4["limited_paths"]:
        logger.info(f"  - {path}")
    
    logger.info("\n--- 示例5: 提取特定路径下的结构 ---")
    # 对特定路径下的结构进行提取
    
    # 先提取orders数组的第一个元素
    first_order = {
        "order": sample_data["orders"][0]
    }
    
    # 创建结构提取操作符
    order_structure_extractor = JsonStructureExtractor(
        include_types=True,
        flatten=True,
        target_field="order_structure",
        name="订单结构提取器"
    )
    
    # 处理数据
    result5 = order_structure_extractor.process(first_order)
    
    # 输出订单结构
    logger.info("订单结构:")
    for path in result5["order_structure"]:
        logger.info(f"  - {path}")
    
    logger.info("\n=== 示例结束 ===")

if __name__ == "__main__":
    run_json_structure_extraction_example() 