"""
JSON简单操作示例

这个示例展示了如何使用JSONFlow的表达式操作符快速处理JSON数据。
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
logger = get_logger("quick_json_operations")

def main():
    """主函数"""
    logger.info("=== 快速JSON操作示例 ===")
    
    # 创建示例数据
    data = {
        "profile": {
            "name": "张三",
            "age": 28,
            "email": "zhangsan@example.com"
        },
        "orders": [
            {"id": "A001", "product": "智能手机", "price": 4999.0, "quantity": 1},
            {"id": "A002", "product": "无线耳机", "price": 799.0, "quantity": 2}
        ],
        "preferences": {
            "language": "zh-CN",
            "notifications": True,
            "theme": "dark"
        }
    }
    
    logger.info("原始数据:")
    logger.info(f"  姓名: {data['profile']['name']}")
    logger.info(f"  订单数: {len(data['orders'])}")
    
    # 示例1: 使用表达式操作符进行基本计算和字符串处理
    logger.info("\n--- 示例1: 基本计算和字符串处理 ---")
    expr_op = JsonExpressionOperator({
        # Lambda函数简单明了
        "total_amount": lambda d: sum(order["price"] * order["quantity"] for order in d["orders"]),
        
        # 格式化表达
        "summary": lambda d: f"{d['profile']['name']}的订单总金额为¥{sum(o['price'] * o['quantity'] for o in d['orders']):.2f}",
        
        # 创建新字段
        "profile.greeting": lambda d: f"您好，{d['profile']['name']}！",
        
        # 提取嵌套信息
        "products": lambda d: [order["product"] for order in d["orders"]],
        
        # 转换类型
        "preferences.receive_emails": lambda d: "是" if d["preferences"]["notifications"] else "否"
    })
    
    # 处理数据
    result1 = expr_op.process(data)
    
    # 输出结果
    logger.info("表达式操作结果:")
    logger.info(f"  总金额: ¥{result1.get('total_amount', 0):.2f}")
    logger.info(f"  订单摘要: {result1.get('summary', '')}")
    logger.info(f"  问候语: {result1['profile'].get('greeting', '')}")
    logger.info(f"  商品列表: {result1.get('products', [])}")
    logger.info(f"  接收邮件: {result1['preferences'].get('receive_emails', '')}")
    
    # 示例2: 使用字段映射操作符进行字段重构
    logger.info("\n--- 示例2: 字段映射和重构 ---")
    mapper_op = JsonFieldMapper({
        # 字段路径简单映射
        "customer.name": "profile.name",
        "customer.contact": "profile.email",
        
        # 列表字段映射
        "order_ids": "orders[*].id",
        "products": "orders[*].product",
        
        # 使用Lambda函数
        "order_details": lambda d: [
            {
                "编号": o["id"],
                "商品": o["product"],
                "小计": o["price"] * o["quantity"]
            }
            for o in d["orders"]
        ],
        
        # 计算派生值
        "statistics.average_price": lambda d: sum(o["price"] for o in d["orders"]) / len(d["orders"]) if d["orders"] else 0
    })
    
    # 处理数据
    result2 = mapper_op.process(data)
    
    # 输出结果
    logger.info("字段映射结果:")
    logger.info(f"  客户名称: {result2.get('customer', {}).get('name', '')}")
    logger.info(f"  订单编号: {result2.get('order_ids', [])}")
    logger.info(f"  订单详情:")
    for i, detail in enumerate(result2.get("order_details", [])):
        logger.info(f"    {i+1}. {detail['编号']} - {detail['商品']} (¥{detail['小计']:.2f})")
    logger.info(f"  平均价格: ¥{result2.get('statistics', {}).get('average_price', 0):.2f}")
    
    # 示例3: 使用模板操作符格式化文本
    logger.info("\n--- 示例3: 使用模板进行文本格式化 ---")
    template_op = JsonTemplateOperator({
        "invoice.header": "发票详情 ({profile.name})",
        "invoice.customer_info": "客户: {profile.name}, 联系方式: {profile.email}",
        "invoice.products": "购买的商品: {products|join:、}",
        "invoice.footer": "总计: ¥{total_amount}, 感谢您的惠顾!",
        
        # 使用修饰符
        "notification.email_subject": "{profile.name|upper}的订单已确认",
        "notification.sms": "尊敬的{profile.name}，您的订单(共{orders|length}件商品)已确认，总金额¥{total_amount}。"
    })
    
    # 使用上一步的结果继续处理
    result3 = template_op.process(result1)
    
    # 输出结果
    logger.info("模板操作结果:")
    logger.info(f"  发票头部: {result3.get('invoice', {}).get('header', '')}")
    logger.info(f"  客户信息: {result3.get('invoice', {}).get('customer_info', '')}")
    logger.info(f"  商品列表: {result3.get('invoice', {}).get('products', '')}")
    logger.info(f"  发票底部: {result3.get('invoice', {}).get('footer', '')}")
    logger.info(f"  邮件主题: {result3.get('notification', {}).get('email_subject', '')}")
    logger.info(f"  短信内容: {result3.get('notification', {}).get('sms', '')}")
    
    # 示例4: 使用管道组合多个操作
    logger.info("\n--- 示例4: 使用管道组合多个操作 ---")
    
    # 创建处理管道
    pipeline = Pipeline([
        # 第1步: 计算和派生字段
        JsonExpressionOperator({
            "total_amount": lambda d: sum(order["price"] * order["quantity"] for order in d["orders"]),
            "profile.full_info": lambda d: f"{d['profile']['name']} ({d['profile']['email']})"
        }),
        
        # 第2步: 字段映射和结构化
        JsonFieldMapper({
            "receipt.customer": "profile.full_info",
            "receipt.amount": "total_amount",
            "receipt.items": lambda d: [
                f"{o['product']} x{o['quantity']}" for o in d["orders"]
            ]
        }),
        
        # 第3步: 格式化输出
        JsonTemplateOperator({
            "output.text": "收据\n客户: {receipt.customer}\n金额: ¥{receipt.amount}\n商品: {receipt.items|join:, }",
            "output.short": "收据 - {profile.name} - ¥{total_amount}"
        })
    ])
    
    # 处理数据
    result4 = pipeline.process(data)
    
    # 输出结果
    logger.info("管道处理结果:")
    logger.info(f"短收据: {result4.get('output', {}).get('short', '')}")
    logger.info("详细收据:")
    for line in result4.get('output', {}).get('text', '').split('\n'):
        logger.info(f"  {line}")
    
    logger.info("\n=== 示例结束 ===")

if __name__ == "__main__":
    main() 