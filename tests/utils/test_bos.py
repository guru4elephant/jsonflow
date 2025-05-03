#!/usr/bin/env python
# coding=utf-8

"""
BOS工具单元测试
"""

import os
import unittest
from unittest import mock
import tempfile
from pathlib import Path

# 创建模拟对象
mock_bce_client_configuration = mock.MagicMock()
mock_bce_credentials = mock.MagicMock()
mock_bos_client = mock.MagicMock()
mock_exception = mock.MagicMock()

# 添加模拟导入
with mock.patch.dict('sys.modules', {
    'baidubce.bce_client_configuration': mock.MagicMock(BceClientConfiguration=mock_bce_client_configuration),
    'baidubce.auth.bce_credentials': mock.MagicMock(BceCredentials=mock_bce_credentials),
    'baidubce.services.bos.bos_client': mock.MagicMock(BosClient=mock_bos_client),
    'baidubce': mock.MagicMock(exception=mock_exception),
}):
    from jsonflow.utils.bos import BosHelper, upload_file, download_file


class TestBosHelper(unittest.TestCase):
    """测试BOS辅助工具类"""
    
    def setUp(self):
        """设置单元测试环境"""
        # 重置模拟对象
        mock_bos_client.reset_mock()
        
        # 设置环境变量
        os.environ['BOS_ACCESS_KEY'] = 'test_access_key'
        os.environ['BOS_SECRET_KEY'] = 'test_secret_key'
        os.environ['BOS_HOST'] = 'test.bcebos.com'
        os.environ['BOS_BUCKET'] = 'test-bucket'
        
        # 创建临时文件
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file_path = os.path.join(self.temp_dir.name, 'test_file.txt')
        with open(self.temp_file_path, 'w') as f:
            f.write('Test content')
        
        # 设置模拟返回值
        self.instance = mock_bos_client.return_value
        self.instance.does_bucket_exist.return_value = True
        
    def tearDown(self):
        """清理单元测试环境"""
        self.temp_dir.cleanup()
        
    def test_init_from_env(self):
        """测试从环境变量初始化"""
        helper = BosHelper()
        self.assertEqual(helper.access_key_id, 'test_access_key')
        self.assertEqual(helper.secret_access_key, 'test_secret_key')
        self.assertEqual(helper.endpoint, 'test.bcebos.com')
        self.assertEqual(helper.bucket, 'test-bucket')
        
    def test_init_from_params(self):
        """测试从参数初始化"""
        helper = BosHelper(
            access_key_id='param_access_key',
            secret_access_key='param_secret_key',
            endpoint='param.bcebos.com',
            bucket='param-bucket'
        )
        self.assertEqual(helper.access_key_id, 'param_access_key')
        self.assertEqual(helper.secret_access_key, 'param_secret_key')
        self.assertEqual(helper.endpoint, 'param.bcebos.com')
        self.assertEqual(helper.bucket, 'param-bucket')
        
    def test_upload_file(self):
        """测试上传单个文件"""
        helper = BosHelper()
        success, url = helper.upload_file(self.temp_file_path, 'test/file.txt')
        
        # 验证客户端方法调用
        self.instance.put_object_from_file.assert_called_once_with(
            'test-bucket', 'test/file.txt', self.temp_file_path
        )
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(url, 'https://test-bucket.test.bcebos.com/test/file.txt')
        
    def test_download_file(self):
        """测试下载单个文件"""
        helper = BosHelper()
        download_path = os.path.join(self.temp_dir.name, 'downloaded.txt')
        success = helper.download_file('test/file.txt', download_path)
        
        # 验证客户端方法调用
        self.instance.get_object_to_file.assert_called_once_with(
            'test-bucket', 'test/file.txt', download_path
        )
        
        # 验证结果
        self.assertTrue(success)
        
    def test_check_bucket_exists(self):
        """测试检查存储桶是否存在"""
        helper = BosHelper()
        
        # 测试存在的桶
        self.instance.does_bucket_exist.return_value = True
        self.assertTrue(helper.check_bucket_exists())
        
        # 测试不存在的桶
        self.instance.does_bucket_exist.return_value = False
        self.assertFalse(helper.check_bucket_exists())
        
    def test_create_bucket(self):
        """测试创建存储桶"""
        helper = BosHelper()
        result = helper.create_bucket()
        
        # 验证客户端方法调用
        self.instance.create_bucket.assert_called_once_with('test-bucket')
        
        # 验证结果
        self.assertTrue(result)
        
    def test_simplified_functions(self):
        """测试简化函数"""
        # 测试上传文件
        success, url = upload_file(
            self.temp_file_path, 
            'test/simple.txt', 
            'test-bucket'
        )
        self.assertTrue(success)
        
        # 测试下载文件
        download_path = os.path.join(self.temp_dir.name, 'simple_downloaded.txt')
        success = download_file(
            'test/simple.txt', 
            download_path, 
            'test-bucket'
        )
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main() 