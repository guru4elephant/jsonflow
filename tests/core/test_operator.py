"""
操作符测试模块

该模块包含对Operator基类及其子类的单元测试。
"""

import unittest
from jsonflow.core import Operator, JsonOperator, ModelOperator

class TestOperator(unittest.TestCase):
    """Operator基类的测试类"""
    
    def test_init(self):
        """测试Operator初始化"""
        # 使用默认值
        op = MockOperator()
        self.assertEqual(op.name, "MockOperator")
        self.assertEqual(op.description, "MockOperator operator")
        
        # 指定名称和描述
        op = MockOperator(name="Custom", description="Custom description")
        self.assertEqual(op.name, "Custom")
        self.assertEqual(op.description, "Custom description")
    
    def test_call(self):
        """测试__call__方法"""
        op = MockOperator()
        json_data = {"key": "value"}
        result = op(json_data)
        self.assertEqual(result, {"key": "value", "processed": True})
    
    def test_process_not_implemented(self):
        """测试未实现process方法的情况"""
        op = Operator()
        with self.assertRaises(NotImplementedError):
            op.process({"key": "value"})


class TestJsonOperator(unittest.TestCase):
    """JsonOperator类的测试类"""
    
    def test_init(self):
        """测试JsonOperator初始化"""
        # 使用默认值
        op = JsonOperator()
        self.assertEqual(op.name, "JsonOperator")
        self.assertEqual(op.description, "JSON data operator")
        
        # 指定名称和描述
        op = JsonOperator(name="Custom", description="Custom description")
        self.assertEqual(op.name, "Custom")
        self.assertEqual(op.description, "Custom description")


class TestModelOperator(unittest.TestCase):
    """ModelOperator类的测试类"""
    
    def test_init(self):
        """测试ModelOperator初始化"""
        # 使用默认值
        op = ModelOperator()
        self.assertEqual(op.name, "ModelOperator")
        self.assertEqual(op.description, "Model operator")
        self.assertEqual(op.model_params, {})
        
        # 指定名称、描述和模型参数
        op = ModelOperator(name="Custom", description="Custom description", model="gpt-3.5-turbo", temperature=0.7)
        self.assertEqual(op.name, "Custom")
        self.assertEqual(op.description, "Custom description")
        self.assertEqual(op.model_params, {"model": "gpt-3.5-turbo", "temperature": 0.7})


class MockOperator(Operator):
    """用于测试的模拟Operator"""
    
    def process(self, json_data):
        """添加processed字段"""
        result = json_data.copy()
        result["processed"] = True
        return result


if __name__ == "__main__":
    unittest.main() 