"""
ModelInvoker 测试模块
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from jsonflow.operators.model import ModelInvoker

class TestModelInvoker(unittest.TestCase):
    """测试 ModelInvoker 类"""
    
    def setUp(self):
        """设置测试环境"""
        # 模拟环境变量
        os.environ["OPENAI_API_KEY"] = "fake-api-key"
        
        # 创建一个ModelInvoker实例用于测试
        self.invoker = ModelInvoker(
            model="gpt-3.5-turbo",
            prompt_field="prompt",
            response_field="response",
            system_prompt="You are a helpful assistant."
        )
    
    @patch('openai.OpenAI')
    def test_process(self, mock_openai):
        """测试基本的process方法"""
        # 设置mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        
        mock_choice = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_choice.message.content = "这是一个测试回复"
        
        # 测试数据
        test_json = {"prompt": "测试提示", "id": "test-1"}
        
        # 执行测试
        result = self.invoker.process(test_json)
        
        # 验证结果
        self.assertEqual(result["response"], "这是一个测试回复")
        self.assertEqual(result["id"], "test-1")  # 确保其他字段保持不变
        
        # 验证调用参数
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        
        # 验证消息格式
        messages = call_kwargs["messages"]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "You are a helpful assistant.")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "测试提示")
    
    @patch('openai.OpenAI')
    def test_call_llm(self, mock_openai):
        """测试call_llm方法"""
        # 设置mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_completion = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        
        mock_choice = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_choice.message.content = "这是一个直接调用的回复"
        
        # 测试消息
        test_messages = [
            {"role": "system", "content": "You are a coding assistant."},
            {"role": "user", "content": "写一个简单的Python函数"}
        ]
        
        # 执行测试
        response = self.invoker.call_llm(test_messages)
        
        # 验证结果
        self.assertEqual(response, "这是一个直接调用的回复")
        
        # 验证调用参数
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        
        # 验证消息被正确传递
        self.assertEqual(call_kwargs["messages"], test_messages)
        self.assertEqual(call_kwargs["model"], "gpt-3.5-turbo")
    
    @patch('openai.OpenAI')
    def test_custom_endpoint(self, mock_openai):
        """测试自定义端点设置"""
        # 创建带自定义端点的实例
        custom_invoker = ModelInvoker(
            model="gpt-3.5-turbo",
            api_key="custom-api-key",
            base_url="https://custom-openai-endpoint.com"
        )
        
        # 验证OpenAI客户端的初始化
        custom_invoker.call_llm([{"role": "user", "content": "test"}])
        
        # 验证客户端初始化参数
        mock_openai.assert_called_with(
            api_key="custom-api-key", 
            base_url="https://custom-openai-endpoint.com"
        )
    
    def test_process_empty_json(self):
        """测试处理空的JSON数据"""
        # 空JSON
        result = self.invoker.process({})
        self.assertEqual(result, {})
        
        # None
        result = self.invoker.process(None)
        self.assertIsNone(result)
    
    def test_missing_prompt_field(self):
        """测试缺少提示字段的JSON数据"""
        test_json = {"id": "test-1", "other_field": "value"}
        result = self.invoker.process(test_json)
        
        # 应该原样返回，不做修改
        self.assertEqual(result, test_json)
    
    @patch('openai.OpenAI')
    def test_api_error_handling(self, mock_openai):
        """测试API错误处理"""
        # 设置mock以抛出异常
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API error")
        
        # 测试数据
        test_json = {"prompt": "测试提示", "id": "test-1"}
        
        # 执行测试，应该抛出异常
        with self.assertRaises(Exception) as context:
            self.invoker.process(test_json)
            
        self.assertIn("OpenAI API call failed", str(context.exception))

if __name__ == "__main__":
    unittest.main() 