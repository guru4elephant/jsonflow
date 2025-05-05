"""
系统字段功能测试模块
"""

import unittest
import re
from jsonflow.utils.system_field import SystemField
from jsonflow.operators.json_ops import IdAdder, TimestampAdder, DateTimeAdder, CustomFieldAdder, FieldRemover

class SystemFieldTest(unittest.TestCase):

    def test_add_id(self):
        """测试添加ID字段"""
        data = {"text": "test data"}
        result = SystemField.add_id(data)
        
        self.assertIn("id", result)
        self.assertIsInstance(result["id"], str)
        # 验证格式为UUID
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.assertTrue(re.match(uuid_pattern, result["id"]))
    
    def test_add_timestamp(self):
        """测试添加时间戳字段"""
        data = {"text": "test data"}
        result = SystemField.add_timestamp(data)
        
        self.assertIn("timestamp", result)
        self.assertIsInstance(result["timestamp"], int)
    
    def test_add_datetime(self):
        """测试添加日期时间字段"""
        data = {"text": "test data"}
        result = SystemField.add_datetime(data)
        
        self.assertIn("datetime", result)
        self.assertIsInstance(result["datetime"], str)
        # 验证格式为日期时间
        datetime_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        self.assertTrue(re.match(datetime_pattern, result["datetime"]))
    
    def test_add_custom_field(self):
        """测试添加自定义字段"""
        data = {"text": "test data"}
        result = SystemField.add_custom_field(data, "source", "test")
        
        self.assertIn("source", result)
        self.assertEqual(result["source"], "test")
    
    def test_remove_field(self):
        """测试移除字段"""
        data = {"id": "12345", "text": "test data"}
        result = SystemField.remove_field(data, "id")
        
        self.assertNotIn("id", result)
        self.assertIn("text", result)
    
    def test_id_adder_operator(self):
        """测试ID添加操作符"""
        operator = IdAdder()
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("id", result)
    
    def test_timestamp_adder_operator(self):
        """测试时间戳添加操作符"""
        operator = TimestampAdder()
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("timestamp", result)
    
    def test_datetime_adder_operator(self):
        """测试日期时间添加操作符"""
        operator = DateTimeAdder()
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("datetime", result)
    
    def test_custom_field_adder_operator(self):
        """测试自定义字段添加操作符"""
        operator = CustomFieldAdder("source", "test")
        data = {"text": "test data"}
        result = operator.process(data)
        
        self.assertIn("source", result)
        self.assertEqual(result["source"], "test")
    
    def test_field_remover_operator(self):
        """测试字段移除操作符"""
        operator = FieldRemover("id")
        data = {"id": "12345", "text": "test data"}
        result = operator.process(data)
        
        self.assertNotIn("id", result)
        self.assertIn("text", result)

if __name__ == '__main__':
    unittest.main() 