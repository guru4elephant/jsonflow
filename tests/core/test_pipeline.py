"""
管道测试模块

该模块包含对Pipeline类的单元测试。
"""

import unittest
from jsonflow.core import Pipeline, Operator

class TestPipeline(unittest.TestCase):
    """Pipeline类的测试类"""
    
    def test_init(self):
        """测试Pipeline初始化"""
        # 空的Pipeline
        pipeline = Pipeline()
        self.assertEqual(len(pipeline.operators), 0)
        
        # 包含操作符的Pipeline
        op1 = MockOperator(name="Op1")
        op2 = MockOperator(name="Op2")
        pipeline = Pipeline([op1, op2])
        self.assertEqual(len(pipeline.operators), 2)
        self.assertEqual(pipeline.operators[0].name, "Op1")
        self.assertEqual(pipeline.operators[1].name, "Op2")
    
    def test_add(self):
        """测试add方法"""
        pipeline = Pipeline()
        op1 = MockOperator(name="Op1")
        op2 = MockOperator(name="Op2")
        
        # 添加第一个操作符
        result = pipeline.add(op1)
        self.assertEqual(len(pipeline.operators), 1)
        self.assertEqual(pipeline.operators[0].name, "Op1")
        self.assertEqual(result, pipeline)  # 测试链式调用返回
        
        # 添加第二个操作符
        pipeline.add(op2)
        self.assertEqual(len(pipeline.operators), 2)
        self.assertEqual(pipeline.operators[1].name, "Op2")
    
    def test_process(self):
        """测试process方法"""
        op1 = AddFieldOperator("field1", "value1")
        op2 = AddFieldOperator("field2", "value2")
        pipeline = Pipeline([op1, op2])
        
        # 处理JSON数据
        json_data = {"original": "data"}
        result = pipeline.process(json_data)
        
        # 检查结果
        expected = {"original": "data", "field1": "value1", "field2": "value2"}
        self.assertEqual(result, expected)
    
    def test_iter(self):
        """测试__iter__方法"""
        op1 = MockOperator(name="Op1")
        op2 = MockOperator(name="Op2")
        pipeline = Pipeline([op1, op2])
        
        # 使用迭代器
        ops = list(pipeline)
        self.assertEqual(len(ops), 2)
        self.assertEqual(ops[0].name, "Op1")
        self.assertEqual(ops[1].name, "Op2")
    
    def test_len(self):
        """测试__len__方法"""
        op1 = MockOperator(name="Op1")
        op2 = MockOperator(name="Op2")
        pipeline = Pipeline([op1, op2])
        
        # 使用len函数
        self.assertEqual(len(pipeline), 2)


class MockOperator(Operator):
    """用于测试的模拟Operator"""
    
    def process(self, json_data):
        """返回原始数据的副本"""
        return json_data.copy()


class AddFieldOperator(Operator):
    """用于测试的添加字段操作符"""
    
    def __init__(self, field, value, name=None, description=None):
        super().__init__(name, description)
        self.field = field
        self.value = value
    
    def process(self, json_data):
        """添加指定的字段和值"""
        result = json_data.copy()
        result[self.field] = self.value
        return result


if __name__ == "__main__":
    unittest.main() 