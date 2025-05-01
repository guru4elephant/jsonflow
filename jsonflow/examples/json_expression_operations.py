"""
JSON表达式操作示例

这个示例展示了如何使用JSON表达式操作符，通过更简单和直观的方式操作JSON数据。
"""

from jsonflow.core import Pipeline
from jsonflow.utils import get_logger, enable_operator_io_logging
from jsonflow.operators.json_ops import (
    JsonExpressionOperator,
    JsonFieldMapper,
    JsonTemplateOperator
)

# 启用操作符输入输出日志
enable_operator_io_logging(True)

# 获取日志记录器
logger = get_logger("json_expression_operations")

def run_json_expression_operations_example():
    """
    运行JSON表达式操作示例
    """
    logger.info("=== JSON表达式操作示例 ===")
    
    # 创建示例JSON数据
    sample_data = {
        "user": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "age": 32,
            "verified": True
        },
        "items": [
            {"id": 101, "name": "Laptop", "price": 1299.99, "quantity": 1},
            {"id": 102, "name": "Mouse", "price": 24.99, "quantity": 2},
            {"id": 103, "name": "Keyboard", "price": 59.99, "quantity": 1}
        ],
        "order": {
            "id": "ORD-12345",
            "status": "processing",
            "created_at": "2023-06-15T12:00:00Z"
        },
        "shipping": {
            "address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zipcode": "12345"
        }
    }
    
    logger.info("\n--- 示例1: 使用表达式操作符 ---")
    # 创建表达式操作符，使用Python表达式直接处理JSON数据
    expression_op = JsonExpressionOperator(
        expressions={
            # 合并字符串 - 创建全名
            "user.full_name": "$.user.first_name + ' ' + $.user.last_name",
            
            # 字符串操作 - 提取邮箱域名
            "user.email_domain": lambda data: data["user"]["email"].split("@")[1] if "@" in data["user"]["email"] else "",
            
            # 数学运算 - 计算总价
            "order.total_price": lambda data: sum(item["price"] * item["quantity"] for item in data["items"]),
            
            # 逻辑操作 - 订单是否超过1000美元
            "order.is_large_order": lambda data: sum(item["price"] * item["quantity"] for item in data["items"]) > 1000,
            
            # 数组操作 - 提取所有商品名称
            "order.item_names": lambda data: [item["name"] for item in data["items"]],
            
            # 格式化字符串
            "shipping.formatted_address": lambda data: (
                f"{data['shipping']['address']}, {data['shipping']['city']}, "
                f"{data['shipping']['state']} {data['shipping']['zipcode']}"
            ),
            
            # 动态计算商品数量
            "order.item_count": lambda data: len(data.get("items", []))
        },
        name="表达式操作符"
    )
    
    # 处理数据
    result1 = expression_op.process(sample_data)
    
    # 输出结果
    logger.info("表达式操作结果:")
    logger.info(f"  全名: {result1['user'].get('full_name', 'N/A')}")
    logger.info(f"  总价: ${result1['order'].get('total_price', 0):.2f}")
    logger.info(f"  是否大额订单: {result1['order'].get('is_large_order', False)}")
    logger.info(f"  邮箱域名: {result1['user'].get('email_domain', 'N/A')}")
    logger.info(f"  商品名称: {result1['order'].get('item_names', [])}")
    logger.info(f"  格式化地址: {result1['shipping'].get('formatted_address', 'N/A')}")
    logger.info(f"  商品数量: {result1['order'].get('item_count', 0)}")
    
    logger.info("\n--- 示例2: 使用字段映射操作符 ---")
    # 创建字段映射操作符，简化字段间的映射操作
    mapper_op = JsonFieldMapper(
        mappings={
            # 简单字段映射
            "customer.name": "user.first_name",
            "customer.email": "user.email",
            "customer.verified": "user.verified",
            
            # 嵌套字段映射
            "delivery.full_address": "shipping.address",
            "delivery.zip": "shipping.zipcode",
            
            # 数组元素映射（提取所有商品名称）
            "product_names": "items[*].name",
            
            # 使用函数进行复杂计算
            "order_summary.subtotal": lambda data: sum(item.get("price", 0) * item.get("quantity", 0) for item in data.get("items", [])),
            "order_summary.item_count": lambda data: sum(item.get("quantity", 0) for item in data.get("items", [])),
            "order_summary.avg_price": lambda data: (
                sum(item.get("price", 0) for item in data.get("items", [])) / len(data.get("items", [])) 
                if data.get("items") else 0
            )
        },
        name="字段映射操作符"
    )
    
    # 处理数据
    result2 = mapper_op.process(sample_data)
    
    # 输出结果
    logger.info("字段映射结果:")
    logger.info(f"  客户名称: {result2.get('customer', {}).get('name', 'N/A')}")
    logger.info(f"  商品名称列表: {result2.get('product_names', [])}")
    logger.info(f"  订单小计: ${result2.get('order_summary', {}).get('subtotal', 0):.2f}")
    logger.info(f"  商品总数: {result2.get('order_summary', {}).get('item_count', 0)}")
    logger.info(f"  平均价格: ${result2.get('order_summary', {}).get('avg_price', 0):.2f}")
    
    logger.info("\n--- 示例3: 使用模板操作符 ---")
    # 创建模板操作符，使用模板字符串格式化JSON数据
    template_op = JsonTemplateOperator(
        templates={
            # 简单拼接
            "formatted_user.display_name": "{user.first_name} {user.last_name}",
            
            # 带修饰符的模板
            "formatted_user.email_label": "{user.first_name|upper} <{user.email}>",
            
            # 格式化的订单信息
            "formatted_order.summary": "订单号: {order.id}, 状态: {order.status|title}, 商品数量: {items|length}",
            
            # 格式化的价格信息 - 注意使用条件判断避免错误
            "formatted_order.pricing": "小计: ${items[0].price} + ${items[1].price} + ${items[2].price}",
            
            # 格式化的送货地址
            "formatted_order.shipping": "送货地址: {shipping.address}, {shipping.city|title}, {shipping.state} {shipping.zipcode}",
            
            # 商品列表
            "formatted_order.items": "商品: {items[0].name}, {items[1].name}, {items[2].name}"
        },
        name="模板操作符"
    )
    
    # 处理数据，直接使用原始数据
    result3 = template_op.process(sample_data)
    
    # 输出结果
    logger.info("模板操作结果:")
    logger.info(f"  显示名称: {result3.get('formatted_user', {}).get('display_name', 'N/A')}")
    logger.info(f"  邮箱标签: {result3.get('formatted_user', {}).get('email_label', 'N/A')}")
    logger.info(f"  订单摘要: {result3.get('formatted_order', {}).get('summary', 'N/A')}")
    logger.info(f"  价格信息: {result3.get('formatted_order', {}).get('pricing', 'N/A')}")
    logger.info(f"  送货地址: {result3.get('formatted_order', {}).get('shipping', 'N/A')}")
    logger.info(f"  商品列表: {result3.get('formatted_order', {}).get('items', 'N/A')}")
    
    logger.info("\n--- 示例4: 组合操作符管道 ---")
    # 创建操作符管道，组合多个操作符
    pipeline = Pipeline([
        # 1. 首先进行表达式操作
        JsonExpressionOperator(
            expressions={
                "user.full_name": "$.user.first_name + ' ' + $.user.last_name",
                "order.total": lambda data: sum(item["price"] * item["quantity"] for item in data["items"]),
                "order.item_count": lambda data: len(data["items"])
            }
        ),
        
        # 2. 然后进行字段映射和重组
        JsonFieldMapper(
            mappings={
                "customer.name": "user.full_name",
                "customer.is_verified": "user.verified",
                "summary.total": "order.total",
                "summary.items": "items[*].name"
            }
        ),
        
        # 3. 最后应用模板格式化
        JsonTemplateOperator(
            templates={
                "invoice.title": "发票 - {order.id}",
                "invoice.customer": "{customer.name} - {user.email}",
                "invoice.details": "{order.item_count}件商品, 总计: ${order.total}",
                "invoice.items": "{summary.items|join:, }",
                "invoice.shipping": "{shipping.address}, {shipping.city}, {shipping.state} {shipping.zipcode}"
            }
        )
    ])
    
    # 处理数据
    result4 = pipeline.process(sample_data)
    
    # 输出结果
    logger.info("管道操作结果:")
    logger.info(f"  发票标题: {result4.get('invoice', {}).get('title', 'N/A')}")
    logger.info(f"  客户信息: {result4.get('invoice', {}).get('customer', 'N/A')}")
    logger.info(f"  订单详情: {result4.get('invoice', {}).get('details', 'N/A')}")
    logger.info(f"  商品列表: {result4.get('invoice', {}).get('items', 'N/A')}")
    logger.info(f"  送货地址: {result4.get('invoice', {}).get('shipping', 'N/A')}")
    
    logger.info("\n=== 示例结束 ===")

if __name__ == "__main__":
    run_json_expression_operations_example() 