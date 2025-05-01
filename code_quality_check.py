#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSONFlow代码质量检查工具

这个脚本检查代码库中可能存在的问题，包括:
1. 缺失的文档字符串
2. 实现与文档不一致的地方
3. 测试覆盖率情况
4. 代码风格问题

用法: python code_quality_check.py [--fix]
"""

import os
import sys
import re
import importlib
import inspect
import subprocess
from pathlib import Path

# 忽略的目录和文件
IGNORE_DIRS = [
    "__pycache__",
    ".git",
    "build",
    "dist",
    "*.egg-info",
]

# 检查项目结构
def check_project_structure():
    """检查项目结构是否完整"""
    print("检查项目结构...")
    
    required_dirs = [
        "jsonflow/core",
        "jsonflow/io",
        "jsonflow/operators",
        "jsonflow/utils",
        "jsonflow/examples",
        "tests",
    ]
    
    required_files = [
        "jsonflow/__init__.py",
        "jsonflow/core/__init__.py",
        "jsonflow/io/__init__.py",
        "jsonflow/operators/__init__.py",
        "jsonflow/utils/__init__.py",
        "setup.py",
        "README.md",
    ]
    
    missing_dirs = []
    missing_files = []
    
    for dir_path in required_dirs:
        if not os.path.isdir(dir_path):
            missing_dirs.append(dir_path)
    
    for file_path in required_files:
        if not os.path.isfile(file_path):
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"警告: 缺少以下目录: {', '.join(missing_dirs)}")
    
    if missing_files:
        print(f"警告: 缺少以下文件: {', '.join(missing_files)}")
    
    if not missing_dirs and not missing_files:
        print("✅ 项目结构完整")

# 检查文档字符串
def check_docstrings():
    """检查所有Python文件是否有文档字符串"""
    print("检查文档字符串...")
    
    missing_docstrings = []
    
    for root, dirs, files in os.walk("jsonflow"):
        # 跳过忽略的目录
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 检查模块文档字符串
                if not re.search(r'^""".*?"""', content, re.DOTALL):
                    missing_docstrings.append(f"{file_path} (缺少模块文档字符串)")
                
                # 检查类和函数文档字符串
                module_name = file_path.replace("/", ".").replace("\\", ".").replace(".py", "")
                try:
                    # 尝试导入模块
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 检查类和方法
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and obj.__module__ == module_name:
                                if not obj.__doc__:
                                    missing_docstrings.append(f"{file_path} :: class {name}")
                                
                                # 检查方法
                                for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                                    if not method.__doc__ and not method_name.startswith("_"):
                                        missing_docstrings.append(f"{file_path} :: class {name} :: method {method_name}")
                        
                        # 检查函数
                        for name, obj in inspect.getmembers(module, inspect.isfunction):
                            if obj.__module__ == module_name and not obj.__doc__ and not name.startswith("_"):
                                missing_docstrings.append(f"{file_path} :: function {name}")
                except (ImportError, SyntaxError) as e:
                    print(f"警告: 无法导入 {file_path}: {e}")
    
    if missing_docstrings:
        print(f"警告: 发现 {len(missing_docstrings)} 处缺少文档字符串:")
        for item in missing_docstrings[:10]:  # 只显示前10个
            print(f"  - {item}")
        if len(missing_docstrings) > 10:
            print(f"  ... 还有 {len(missing_docstrings) - 10} 处未显示")
    else:
        print("✅ 所有模块、类和函数都有文档字符串")

# 检查测试覆盖率
def check_test_coverage():
    """运行测试并检查测试覆盖率"""
    print("检查测试覆盖率...")
    
    try:
        result = subprocess.run(
            ["pytest", "--cov=jsonflow", "--cov-report=term-missing"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"⚠️ 测试失败，返回代码: {result.returncode}")
            if result.stderr:
                print(f"错误信息: {result.stderr}")
        
        # 提取覆盖率数据
        coverage_match = re.search(r"TOTAL\s+.*?(\d+)%", result.stdout)
        if coverage_match:
            coverage = int(coverage_match.group(1))
            if coverage < 70:
                print(f"⚠️ 测试覆盖率较低: {coverage}% (建议至少达到70%)")
            else:
                print(f"✅ 测试覆盖率: {coverage}%")
        else:
            print("⚠️ 无法确定测试覆盖率")
    
    except FileNotFoundError:
        print("⚠️ 无法运行测试，请确保已安装pytest和pytest-cov")

# 检查代码风格
def check_code_style():
    """使用flake8检查代码风格"""
    print("检查代码风格...")
    
    try:
        result = subprocess.run(
            ["flake8", "jsonflow", "tests"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.stdout:
            print(f"发现 {result.stdout.count(os.linesep)} 处代码风格问题:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("✅ 代码风格符合规范")
    
    except FileNotFoundError:
        print("⚠️ 无法检查代码风格，请确保已安装flake8")

# 检查实现与设计文档的一致性
def check_implementation_consistency():
    """检查实现与设计文档的一致性"""
    print("检查实现与设计文档的一致性...")
    
    if not os.path.isfile("architecture.md") or not os.path.isfile("implementation_design.md"):
        print("⚠️ 缺少设计文档，无法检查一致性")
        return
    
    # 读取设计文档
    with open("architecture.md", "r", encoding="utf-8") as f:
        architecture_content = f.read()
    
    with open("implementation_design.md", "r", encoding="utf-8") as f:
        implementation_content = f.read()
    
    # 从设计文档中提取关键类
    architecture_classes = set(re.findall(r"\b([A-Z][a-zA-Z]+(?:Operator|Executor|Loader|Saver))\b", architecture_content))
    
    # 从实现设计中提取关键类
    implementation_classes = set(re.findall(r"\b(class\s+([A-Z][a-zA-Z]+(?:Operator|Executor|Loader|Saver)))\b", implementation_content))
    implementation_classes = {match[1] for match in implementation_classes}
    
    # 检查实际代码中的类
    actual_classes = set()
    for root, dirs, files in os.walk("jsonflow"):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 查找类定义
                class_matches = re.findall(r"\bclass\s+([A-Z][a-zA-Z]+(?:Operator|Executor|Loader|Saver))\b", content)
                actual_classes.update(class_matches)
    
    # 检查不一致
    in_arch_not_impl = architecture_classes - implementation_classes
    in_impl_not_arch = implementation_classes - architecture_classes
    in_impl_not_actual = implementation_classes - actual_classes
    in_actual_not_impl = actual_classes - implementation_classes
    
    if in_arch_not_impl:
        print(f"⚠️ 架构文档中的类未在实现设计中找到: {', '.join(in_arch_not_impl)}")
    
    if in_impl_not_arch:
        print(f"⚠️ 实现设计中的类未在架构文档中找到: {', '.join(in_impl_not_arch)}")
    
    if in_impl_not_actual:
        print(f"⚠️ 实现设计中的类未在实际代码中找到: {', '.join(in_impl_not_actual)}")
    
    if in_actual_not_impl:
        print(f"⚠️ 实际代码中的类未在实现设计中找到: {', '.join(in_actual_not_impl)}")
    
    if not (in_arch_not_impl or in_impl_not_arch or in_impl_not_actual or in_actual_not_impl):
        print("✅ 实现与设计文档一致")

# 主函数
def main():
    """主函数"""
    print("=== JSONFlow代码质量检查 ===\n")
    
    check_project_structure()
    print()
    
    check_implementation_consistency()
    print()
    
    check_docstrings()
    print()
    
    check_code_style()
    print()
    
    check_test_coverage()
    print("\n=== 检查完成 ===")

if __name__ == "__main__":
    main() 