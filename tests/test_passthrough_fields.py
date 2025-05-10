"""
透传字段功能测试模块
"""

import unittest
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer

class MockOperator:
    """用于测试的模拟操作符"""
    def process(self, json_data):
        # 简单返回一个新对象，不保留原有字段
        return {"result": "processed"}

class PassthroughFieldsTest(unittest.TestCase):

    def test_passthrough_single_field(self):
        """测试单个字段透传"""
        pipeline = Pipeline([MockOperator()])
        pipeline.set_passthrough_fields(['id'])
        
        input_data = {"id": "12345", "text": "test data"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["result"], "processed")
        self.assertNotIn("text", result)
    
    def test_passthrough_multiple_fields(self):
        """测试多个字段透传"""
        pipeline = Pipeline([MockOperator()])
        pipeline.set_passthrough_fields(['id', 'metadata'])
        
        input_data = {"id": "12345", "metadata": {"source": "test"}, "text": "test data"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["metadata"]["source"], "test")
        self.assertEqual(result["result"], "processed")
        self.assertNotIn("text", result)
    
    def test_passthrough_nonexistent_field(self):
        """测试不存在的字段透传"""
        pipeline = Pipeline([MockOperator()])
        pipeline.set_passthrough_fields(['id', 'nonexistent'])
        
        input_data = {"id": "12345", "text": "test data"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["result"], "processed")
        self.assertNotIn("nonexistent", result)
        self.assertNotIn("text", result)
    
    def test_passthrough_with_real_operator(self):
        """测试与真实操作符的集成"""
        pipeline = Pipeline([TextNormalizer(lower_case=True)])
        pipeline.set_passthrough_fields(['id'])
        
        input_data = {"id": "12345", "text": "TEST DATA"}
        result = pipeline.process(input_data)
        
        self.assertEqual(result["id"], "12345")
        self.assertEqual(result["text"], "test data")

if __name__ == '__main__':
    unittest.main() 