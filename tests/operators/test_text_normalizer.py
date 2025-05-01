"""
文本规范化操作符测试模块

该模块包含对TextNormalizer操作符的单元测试。
"""

import unittest
from jsonflow.operators.json_ops import TextNormalizer

class TestTextNormalizer(unittest.TestCase):
    """TextNormalizer类的测试类"""
    
    def test_init(self):
        """测试TextNormalizer初始化"""
        # 使用默认值
        normalizer = TextNormalizer()
        self.assertEqual(normalizer.name, "TextNormalizer")
        self.assertEqual(normalizer.description, "Normalizes text fields in JSON data")
        self.assertIsNone(normalizer.text_fields)
        self.assertTrue(normalizer.strip)
        self.assertFalse(normalizer.lower_case)
        self.assertFalse(normalizer.upper_case)
        self.assertTrue(normalizer.remove_extra_spaces)
        
        # 指定参数
        normalizer = TextNormalizer(
            text_fields=["field1", "field2"],
            strip=False,
            lower_case=True,
            name="Custom",
            description="Custom description"
        )
        self.assertEqual(normalizer.name, "Custom")
        self.assertEqual(normalizer.description, "Custom description")
        self.assertEqual(normalizer.text_fields, ["field1", "field2"])
        self.assertFalse(normalizer.strip)
        self.assertTrue(normalizer.lower_case)
        self.assertFalse(normalizer.upper_case)
        self.assertTrue(normalizer.remove_extra_spaces)
    
    def test_conflicting_options(self):
        """测试冲突选项"""
        # lower_case和upper_case不能同时为True
        with self.assertRaises(ValueError):
            TextNormalizer(lower_case=True, upper_case=True)
    
    def test_process_empty(self):
        """测试处理空数据"""
        normalizer = TextNormalizer()
        self.assertEqual(normalizer.process({}), {})
        self.assertEqual(normalizer.process(None), None)
    
    def test_process_flat(self):
        """测试处理扁平JSON"""
        normalizer = TextNormalizer()
        json_data = {
            "text1": "  Hello  World  ",
            "text2": "  ANOTHER   TEXT  ",
            "number": 42
        }
        result = normalizer.process(json_data)
        
        # 检查结果
        expected = {
            "text1": "Hello World",
            "text2": "ANOTHER TEXT",
            "number": 42
        }
        self.assertEqual(result, expected)
    
    def test_process_nested(self):
        """测试处理嵌套JSON"""
        normalizer = TextNormalizer()
        json_data = {
            "outer": "  Outer  Text  ",
            "nested": {
                "inner": "  Inner  Text  ",
                "number": 42
            },
            "list": ["  List  Item  1  ", "  List  Item  2  ", 42]
        }
        result = normalizer.process(json_data)
        
        # 检查结果
        expected = {
            "outer": "Outer Text",
            "nested": {
                "inner": "Inner Text",
                "number": 42
            },
            "list": ["List Item 1", "List Item 2", 42]
        }
        self.assertEqual(result, expected)
    
    def test_specific_fields(self):
        """测试只处理特定字段"""
        normalizer = TextNormalizer(text_fields=["field1", "nested.inner"])
        json_data = {
            "field1": "  Field  1  ",
            "field2": "  Field  2  ",
            "nested": {
                "inner": "  Inner  Field  ",
                "outer": "  Outer  Field  "
            }
        }
        result = normalizer.process(json_data)
        
        # 检查结果
        expected = {
            "field1": "Field 1",
            "field2": "  Field  2  ",  # 未处理
            "nested": {
                "inner": "Inner Field",
                "outer": "  Outer  Field  "  # 未处理
            }
        }
        self.assertEqual(result, expected)
    
    def test_custom_normalize_func(self):
        """测试自定义规范化函数"""
        def custom_normalize(text):
            return text.strip().upper()
        
        normalizer = TextNormalizer(normalize_func=custom_normalize)
        json_data = {
            "text": "  hello world  "
        }
        result = normalizer.process(json_data)
        
        # 检查结果
        expected = {
            "text": "HELLO WORLD"
        }
        self.assertEqual(result, expected)
    
    def test_lower_case(self):
        """测试转换为小写"""
        normalizer = TextNormalizer(lower_case=True)
        json_data = {
            "text": "  Hello WORLD  "
        }
        result = normalizer.process(json_data)
        
        # 检查结果
        expected = {
            "text": "hello world"
        }
        self.assertEqual(result, expected)
    
    def test_upper_case(self):
        """测试转换为大写"""
        normalizer = TextNormalizer(upper_case=True)
        json_data = {
            "text": "  Hello world  "
        }
        result = normalizer.process(json_data)
        
        # 检查结果
        expected = {
            "text": "HELLO WORLD"
        }
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main() 