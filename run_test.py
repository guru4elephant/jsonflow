#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSONFlow测试运行脚本

运行此脚本以执行JSONFlow的所有单元测试。
"""

import unittest
import sys

if __name__ == "__main__":
    # 发现并运行所有测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 根据测试结果设置退出代码
    sys.exit(not result.wasSuccessful()) 