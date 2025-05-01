"""
JSON字段操作示例

这个示例展示了如何使用各种JSON字段操作符对JSON数据进行增删查改。
"""

from jsonflow.core import Pipeline
from jsonflow.utils import get_logger, enable_operator_io_logging
from jsonflow.operators.json_ops import (
    JsonFieldSelector,
    JsonPathExtractor,
    JsonPathUpdater,
    JsonPathRemover,
    JsonArrayOperator,
    JsonMerger
)

# 启用操作符输入输出日志
enable_operator_io_logging(True)

# 获取日志记录器
logger = get_logger("json_field_operations")

def run_json_field_operations_example():
    """
    运行JSON字段操作示例
    """
    logger.info("=== JSON字段操作示例 ===")
    
    # 创建示例JSON数据
    sample_data = {
        "id": 123,
        "user": {
            "name": "John Doe",
            "email": "john@example.com",
            "profile": {
                "age": 30,
                "occupation": "Developer"
            }
        },
        "items": [
            {"id": 1, "name": "Item 1", "price": 10.5},
            {"id": 2, "name": "Item 2", "price": 20.0},
            {"id": 3, "name": "Item 3", "price": 15.75}
        ],
        "metadata": {
            "created_at": "2023-01-01T12:00:00Z",
            "tags": ["example", "json", "test"]
        }
    }
    
    logger.info("\n--- 示例1: 字段选择 ---")
    # 创建字段选择操作符
    field_selector = JsonFieldSelector(
        fields=["id", "user.name", "user.profile.occupation", "metadata.tags"],
        name="示例选择器"
    )
    
    # 处理数据
    result1 = field_selector.process(sample_data)
    logger.info(f"选择字段后的结果包含 {len(result1)} 个顶级字段")
    
    logger.info("\n--- 示例2: 扁平化字段选择 ---")
    # 创建扁平化字段选择操作符
    flat_selector = JsonFieldSelector(
        fields=["id", "user.name", "user.profile.age", "metadata.created_at"],
        flatten=True,
        prefix="data_",
        name="扁平化选择器"
    )
    
    # 处理数据
    result2 = flat_selector.process(sample_data)
    logger.info(f"扁平化后的结果包含 {len(result2)} 个字段")
    
    logger.info("\n--- 示例3: 路径提取 ---")
    # 创建路径提取操作符
    path_extractor = JsonPathExtractor(
        paths={
            "user_name": "user.name",
            "user_occupation": "user.profile.occupation",
            "first_item_name": "items.0.name",
            "tags": "metadata.tags"
        },
        default_value="未知",
        name="路径提取器"
    )
    
    # 处理数据
    result3 = path_extractor.process(sample_data)
    logger.info(f"提取后的结果: {result3}")
    
    logger.info("\n--- 示例4: 路径更新 ---")
    # 创建路径更新操作符
    path_updater = JsonPathUpdater(
        updates={
            "user.name": "Jane Smith",
            "user.profile.age": 32,
            "user.profile.skills": ["Python", "JavaScript", "SQL"],
            "metadata.updated_at": "2023-06-15T15:30:00Z"
        },
        name="路径更新器"
    )
    
    # 处理数据
    result4 = path_updater.process(sample_data)
    logger.info(f"更新后的用户名: {result4['user']['name']}")
    logger.info(f"更新后的用户资料: {result4['user']['profile']}")
    
    logger.info("\n--- 示例5: 路径删除 ---")
    # 创建路径删除操作符
    path_remover = JsonPathRemover(
        paths=["user.email", "metadata.created_at", "items.0"],
        name="路径删除器"
    )
    
    # 处理数据
    result5 = path_remover.process(sample_data)
    logger.info(f"删除后的结果包含 {len(result5)} 个顶级字段")
    logger.info(f"用户字段现在包含: {list(result5['user'].keys())}")
    logger.info(f"商品数量: {len(result5['items'])}")
    
    logger.info("\n--- 示例6: 数组操作 ---")
    # 创建数组操作符 - 价格过滤
    array_filter = JsonArrayOperator(
        field="items",
        operation="filter",
        func=lambda item: item["price"] > 15,
        name="价格过滤器"
    )
    
    # 创建数组操作符 - 排序
    array_sort = JsonArrayOperator(
        field="items",
        operation="sort",
        func=lambda item: item["price"],
        output_field="sorted_items",
        name="价格排序器"
    )
    
    # 创建数组操作符 - 映射
    array_map = JsonArrayOperator(
        field="items",
        operation="map",
        func=lambda item: {"name": item["name"], "price_with_tax": item["price"] * 1.1},
        output_field="items_with_tax",
        name="税价映射器"
    )
    
    # 处理数据 - 链式操作
    pipeline = Pipeline([array_filter, array_sort, array_map])
    result6 = pipeline.process(sample_data)
    
    logger.info(f"过滤后的商品数量: {len(result6['items'])}")
    logger.info(f"排序后的商品: {[item['name'] for item in result6['sorted_items']]}")
    logger.info(f"映射后的商品: {result6['items_with_tax']}")
    
    logger.info("\n--- 示例7: JSON合并 ---")
    # 创建合并操作符
    merger = JsonMerger(
        data_to_merge={
            "app_info": {
                "version": "1.0.0",
                "environment": "production"
            },
            "processed_at": "2023-06-20T10:15:00Z",
            "item_count": lambda data: len(data.get("items", []))
        },
        name="JSON合并器"
    )
    
    # 处理数据
    result7 = merger.process(sample_data)
    logger.info(f"合并后的结果包含新字段: {list(set(result7.keys()) - set(sample_data.keys()))}")
    logger.info(f"动态计算的商品数量: {result7['item_count']}")
    
    logger.info("\n=== 示例结束 ===")

if __name__ == "__main__":
    run_json_field_operations_example() 