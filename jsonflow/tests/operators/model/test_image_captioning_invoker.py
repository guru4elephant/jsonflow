"""
ImageCaptioningInvoker 测试模块
"""

import unittest
import os
import json
import base64
from unittest.mock import patch, MagicMock, mock_open
from jsonflow.examples.image_captioning_example import ImageCaptioningInvoker

class TestImageCaptioningInvoker(unittest.TestCase):
    """测试 ImageCaptioningInvoker 类"""
    
    def setUp(self):
        """设置测试环境"""
        # 模拟环境变量
        os.environ["OPENAI_API_KEY"] = "fake-api-key"
        
        # 创建一个ImageCaptioningInvoker实例用于测试
        self.invoker = ImageCaptioningInvoker(
            model="gpt-4-vision-preview",
            image_field="image_path",
            caption_field="caption",
            caption_prompt="请描述这张图片。",
            system_prompt="你是一个图像描述专家。"
        )
        
        # 模拟图像数据
        self.mock_image_data = "fake_base64_encoded_image_data"
        
        # 测试数据
        self.test_json = {
            "id": "test-img-1",
            "image_path": "/path/to/test_image.jpg",
            "metadata": {"type": "test"}
        }
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_binary_data')
    @patch('base64.b64encode')
    @patch.object(ImageCaptioningInvoker, 'call_llm')
    def test_process_success(self, mock_call_llm, mock_b64encode, mock_file):
        """测试成功处理图像"""
        # 设置模拟返回值
        mock_b64encode.return_value = self.mock_image_data.encode('utf-8')
        mock_call_llm.return_value = "这是一张风景照片，展示了山脉和湖泊。"
        
        # 执行测试
        result = self.invoker.process(self.test_json)
        
        # 验证结果
        self.assertEqual(result["id"], "test-img-1")  # 保留原始字段
        self.assertEqual(result["caption"], "这是一张风景照片，展示了山脉和湖泊。")  # 添加了标题字段
        
        # 验证文件打开操作
        mock_file.assert_called_once_with("/path/to/test_image.jpg", "rb")
        
        # 验证base64编码
        mock_b64encode.assert_called_once()
        
        # 验证调用LLM
        mock_call_llm.assert_called_once()
        call_args = mock_call_llm.call_args[0][0]
        
        # 验证消息格式
        self.assertEqual(len(call_args), 2)
        self.assertEqual(call_args[0]["role"], "system")
        self.assertEqual(call_args[0]["content"], "你是一个图像描述专家。")
        self.assertEqual(call_args[1]["role"], "user")
        self.assertIsInstance(call_args[1]["content"], list)
        self.assertEqual(len(call_args[1]["content"]), 2)
        self.assertEqual(call_args[1]["content"][0]["type"], "text")
        self.assertEqual(call_args[1]["content"][0]["text"], "请描述这张图片。")
        self.assertEqual(call_args[1]["content"][1]["type"], "image_url")
    
    @patch('builtins.open')
    def test_process_file_error(self, mock_open):
        """测试文件读取错误处理"""
        # 设置模拟抛出异常
        mock_open.side_effect = FileNotFoundError("文件不存在")
        
        # 执行测试
        result = self.invoker.process(self.test_json)
        
        # 验证结果
        self.assertEqual(result["id"], "test-img-1")  # 保留原始字段
        self.assertTrue("图像读取错误" in result["caption"])  # 错误信息
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'fake_image_binary_data')
    @patch('base64.b64encode')
    @patch.object(ImageCaptioningInvoker, 'call_llm')
    def test_process_model_error(self, mock_call_llm, mock_b64encode, mock_file):
        """测试模型调用错误处理"""
        # 设置模拟返回值
        mock_b64encode.return_value = self.mock_image_data.encode('utf-8')
        mock_call_llm.side_effect = Exception("模型调用失败")
        
        # 执行测试
        result = self.invoker.process(self.test_json)
        
        # 验证结果
        self.assertEqual(result["id"], "test-img-1")  # 保留原始字段
        self.assertTrue("模型调用错误" in result["caption"])  # 错误信息
    
    def test_process_missing_field(self):
        """测试缺少图像路径字段的处理"""
        # 没有image_path字段的测试数据
        test_json_no_image = {
            "id": "test-img-2",
            "metadata": {"type": "test"}
        }
        
        # 执行测试
        result = self.invoker.process(test_json_no_image)
        
        # 验证结果：应该原样返回，不做修改
        self.assertEqual(result, test_json_no_image)
    
    def test_process_empty_json(self):
        """测试处理空JSON"""
        # 执行测试
        result = self.invoker.process({})
        
        # 验证结果：应该原样返回空JSON
        self.assertEqual(result, {})
        
        # 测试None输入
        result = self.invoker.process(None)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main() 