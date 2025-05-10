#!/usr/bin/env python
# coding=utf-8

"""
Collection operators test module.
Tests JsonSplitter, JsonAggregator and Pipeline's handling of JSON lists.
"""

import unittest
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.json_ops.collection_ops import JsonSplitter, JsonAggregator

class MockOperator:
    """用于测试的模拟操作符"""
    def process(self, json_data):
        if isinstance(json_data, list):
            return [{"processed": True, "original": item} for item in json_data]
        return {"processed": True, "original": json_data}

class JsonSplitterTest(unittest.TestCase):
    """Test JsonSplitter operator"""
    
    def test_split_simple(self):
        """Test splitting a simple JSON object with a list field"""
        # 创建测试数据
        data = {
            "id": "test-1", 
            "items": ["item1", "item2", "item3"]
        }
        
        # 创建并执行拆分操作符
        splitter = JsonSplitter(split_field='items')
        results = splitter.process(data)
        
        # 验证结果
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["items"], "item1")
        self.assertEqual(results[1]["items"], "item2")
        self.assertEqual(results[2]["items"], "item3")
    
    def test_split_with_output_mapping(self):
        """Test splitting with output field mapping"""
        # 创建测试数据
        data = {
            "id": "test-1", 
            "items": ["item1", "item2"],
            "category": "test"
        }
        
        # 创建输出字段映射
        mapping = {
            "id": "original_id",
            "items": "content",
            "category": "type"
        }
        
        # 创建并执行拆分操作符
        splitter = JsonSplitter(split_field='items', output_key_map=mapping, keep_original=False)
        results = splitter.process(data)
        
        # 验证结果
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "item1")
        self.assertEqual(results[0]["original_id"], "test-1")
        self.assertEqual(results[0]["type"], "test")
        self.assertEqual(results[1]["content"], "item2")
        self.assertNotIn("items", results[0])
    
    def test_split_with_keep_original(self):
        """Test splitting while keeping original fields"""
        # 创建测试数据
        data = {
            "id": "test-1", 
            "items": ["item1", "item2"],
            "metadata": {"source": "test"}
        }
        
        # 创建并执行拆分操作符
        splitter = JsonSplitter(split_field='items', keep_original=True)
        results = splitter.process(data)
        
        # 验证结果
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["items"], "item1")
        self.assertEqual(results[0]["id"], "test-1")
        self.assertEqual(results[0]["metadata"]["source"], "test")
        self.assertEqual(results[1]["items"], "item2")
        
    def test_split_with_nonexistent_field(self):
        """Test splitting with nonexistent field"""
        # 创建测试数据
        data = {"id": "test-1", "text": "sample"}
        
        # 创建并执行拆分操作符
        splitter = JsonSplitter(split_field='nonexistent')
        results = splitter.process(data)
        
        # 验证结果 - 应该返回原对象的列表
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], data)

    def test_split_with_non_list_field(self):
        """Test splitting with field that is not a list"""
        # 创建测试数据
        data = {"id": "test-1", "items": "not-a-list"}
        
        # 创建并执行拆分操作符
        splitter = JsonSplitter(split_field='items')
        results = splitter.process(data)
        
        # 验证结果 - 应该返回原对象的列表
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], data)


class JsonAggregatorTest(unittest.TestCase):
    """Test JsonAggregator operator"""
    
    def test_aggregate_list_strategy(self):
        """Test aggregating to a list"""
        # 创建测试数据
        data = [
            {"id": "1", "text": "first"},
            {"id": "2", "text": "second"},
            {"id": "3", "text": "third"}
        ]
        
        # 创建并执行合并操作符
        aggregator = JsonAggregator(aggregate_field='items', strategy='list')
        result = aggregator.process(data)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn('items', result)
        self.assertEqual(len(result['items']), 3)
        self.assertEqual(result['items'][0]['id'], "1")
        self.assertEqual(result['items'][1]['text'], "second")
    
    def test_aggregate_list_no_field(self):
        """Test aggregating to a list without specifying a field"""
        # 创建测试数据
        data = [
            {"id": "1", "text": "first"},
            {"id": "2", "text": "second"}
        ]
        
        # 创建并执行合并操作符
        aggregator = JsonAggregator(strategy='list')
        result = aggregator.process(data)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], "1")
        self.assertEqual(result[1]['text'], "second")
    
    def test_aggregate_merge_strategy(self):
        """Test aggregating with merge strategy"""
        # 创建测试数据
        data = [
            {"id": "1", "name": "test1"},
            {"count": 5, "active": True},
            {"tags": ["tag1", "tag2"]}
        ]
        
        # 创建并执行合并操作符
        aggregator = JsonAggregator(strategy='merge')
        result = aggregator.process(data)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertEqual(result['id'], "1")
        self.assertEqual(result['name'], "test1")
        self.assertEqual(result['count'], 5)
        self.assertTrue(result['active'])
        self.assertEqual(result['tags'], ["tag1", "tag2"])
    
    def test_aggregate_with_condition(self):
        """Test aggregating with a condition"""
        # 创建测试数据
        data = [
            {"id": "1", "active": True},
            {"id": "2", "active": False},
            {"id": "3", "active": True}
        ]
        
        # 创建条件函数和合并操作符
        condition = lambda x: x.get('active', False)
        aggregator = JsonAggregator(aggregate_field='active_items', strategy='list', condition=condition)
        result = aggregator.process(data)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn('active_items', result)
        self.assertEqual(len(result['active_items']), 2)
        self.assertEqual(result['active_items'][0]['id'], "1")
        self.assertEqual(result['active_items'][1]['id'], "3")
    
    def test_aggregate_empty_list(self):
        """Test aggregating an empty list"""
        # 创建并执行合并操作符
        aggregator = JsonAggregator(aggregate_field='items')
        result = aggregator.process([])
        
        # 验证结果
        self.assertEqual(result, {})
    
    def test_aggregate_single_item(self):
        """Test processing a single item"""
        # 创建测试数据
        data = {"id": "1", "text": "single"}
        
        # 创建并执行合并操作符
        aggregator = JsonAggregator()
        result = aggregator.process(data)
        
        # 验证结果 - 应该直接返回输入
        self.assertEqual(result, data)


class PipelineCollectionTest(unittest.TestCase):
    """Test Pipeline handling of collection processing"""
    
    def test_pipeline_flatten_mode(self):
        """Test pipeline with flatten mode"""
        # 创建测试管道
        pipeline = Pipeline([
            JsonSplitter(split_field='items'),
            # 第二个操作符将处理拆分后的每个项目
            TextNormalizer()
        ], collection_mode=Pipeline.FLATTEN)
        
        # 创建测试数据
        data = {
            "id": "test-1",
            "items": [
                {"text": "ITEM ONE"},
                {"text": "ITEM TWO"}
            ]
        }
        
        # 执行管道
        results = pipeline.process(data)
        
        # 验证结果
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["text"], "item one")
        self.assertEqual(results[1]["text"], "item two")
        # 验证透传字段
        self.assertEqual(results[0]["id"], "test-1")
        self.assertEqual(results[1]["id"], "test-1")
    
    def test_pipeline_nested_mode(self):
        """Test pipeline with nested mode"""
        # 创建测试管道
        pipeline = Pipeline([
            JsonSplitter(split_field='items'),
            # 第二个操作符将处理整个列表
            JsonAggregator(aggregate_field='processed')
        ], collection_mode=Pipeline.NESTED)
        
        # 创建测试数据
        data = {
            "id": "test-1",
            "items": ["item1", "item2", "item3"]
        }
        
        # 执行管道
        result = pipeline.process(data)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("processed", result)
        self.assertEqual(len(result["processed"]), 3)
        # 验证透传字段 - 在嵌套模式下，合并结果中不会包含原始数据的透传字段
        self.assertNotIn("id", result)
    
    def test_pipeline_with_list_input(self):
        """Test pipeline with list input"""
        # 创建测试管道
        pipeline = Pipeline([
            TextNormalizer(),
            # 这个管道不包含拆分或合并操作符，只是处理每个项目
        ], collection_mode=Pipeline.FLATTEN)
        
        # 创建测试数据
        data = [
            {"text": "ITEM ONE"},
            {"text": "ITEM TWO"},
            {"text": "ITEM THREE"}
        ]
        
        # 执行管道
        results = pipeline.process(data)
        
        # 验证结果
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["text"], "item one")
        self.assertEqual(results[1]["text"], "item two")
        self.assertEqual(results[2]["text"], "item three")
    
    def test_complex_pipeline(self):
        """Test complex pipeline with multiple collection operations"""
        # 创建测试管道
        pipeline = Pipeline([
            # 拆分各个项目
            JsonSplitter(split_field='items', keep_original=True),
            # 处理拆分后的文本
            TextNormalizer(),
            # 再次拆分每项中的tags
            JsonSplitter(split_field='tags', output_key_map={'tags': 'tag'}, keep_original=True),
            # 收集所有结果
            JsonAggregator(aggregate_field='all_results')
        ], collection_mode=Pipeline.FLATTEN)
        
        # 创建测试数据
        data = {
            "id": "test-complex",
            "items": [
                {"text": "ITEM ONE", "tags": ["tag1", "tag2"]},
                {"text": "ITEM TWO", "tags": ["tag3"]}
            ]
        }
        
        # 执行管道
        result = pipeline.process(data)
        
        # 验证结果
        self.assertIsInstance(result, dict)
        self.assertIn("all_results", result)
        # 第一项拆分为2个标签项，第二项拆分为1个标签项，总共3个
        self.assertEqual(len(result["all_results"]), 3)
        # 检查文本规范化是否生效
        self.assertTrue(any(item["text"] == "item one" for item in result["all_results"]))
        self.assertTrue(any(item["text"] == "item two" for item in result["all_results"]))
        # 检查标签是否正确拆分
        self.assertTrue(any(item["tag"] == "tag1" for item in result["all_results"]))
        self.assertTrue(any(item["tag"] == "tag3" for item in result["all_results"]))


if __name__ == '__main__':
    unittest.main() 