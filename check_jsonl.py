#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查JSONL文件，验证每行是否有效JSON，并可以选择过滤无效行
"""

import argparse
import json
import sys
import re
from pathlib import Path

def is_valid_json(line):
    """检查一行是否是有效的JSON"""
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False

def clean_line(line, normalize_whitespace=False):
    """清理行内容，处理特殊字符"""
    if normalize_whitespace:
        # 规范化空白字符：将制表符、回车等替换为空格
        line = re.sub(r'\s+', ' ', line)
    return line.strip()

def process_jsonl_file(input_file, output_file=None, remove_invalid=False, verbose=False, 
                       count_only=False, normalize_whitespace=False, fix_errors=False):
    """处理JSONL文件，验证每行是否有效JSON，根据选项过滤无效行"""
    valid_count = 0
    invalid_count = 0
    fixed_count = 0
    total_count = 0
    
    # 如果输入是'-'，从标准输入读取
    if input_file == '-':
        input_stream = sys.stdin
    else:
        input_stream = open(input_file, 'r', encoding='utf-8')
    
    # 如果输出是'-'，输出到标准输出
    if output_file == '-':
        output_stream = sys.stdout
    elif output_file is not None:
        output_stream = open(output_file, 'w', encoding='utf-8')
    elif remove_invalid:
        output_stream = sys.stdout
    else:
        output_stream = None
    
    try:
        for line_number, line in enumerate(input_stream, 1):
            original_line = line
            line = clean_line(line, normalize_whitespace)
            total_count += 1
            
            # 跳过空行
            if not line:
                invalid_count += 1
                if verbose:
                    print(f"行 {line_number}: 空行", file=sys.stderr)
                continue
            
            is_valid = is_valid_json(line)
            
            if is_valid:
                valid_count += 1
                # 如果需要输出有效行
                if remove_invalid and output_stream:
                    print(line, file=output_stream)
            else:
                fixed_line = None
                if fix_errors:
                    # 尝试修复一些常见错误
                    try_fixes = [
                        # 缺少右括号
                        lambda l: l + '}' if l.count('{') > l.count('}') else None,
                        # 缺少右方括号
                        lambda l: l + ']' if l.count('[') > l.count(']') else None,
                        # 缺少引号的键
                        lambda l: re.sub(r'([{,])\s*(\w+)(?=\s*:)', r'\1"\2"', l),
                        # 缺少引号的值
                        lambda l: re.sub(r':\s*(\w+)(?=[,}])', r':"\1"', l),
                        # 尾部多余的逗号
                        lambda l: re.sub(r',\s*([}\]])', r'\1', l),
                    ]
                    
                    for fix in try_fixes:
                        attempt = fix(line)
                        if attempt and is_valid_json(attempt):
                            fixed_line = attempt
                            fixed_count += 1
                            break
                
                if fixed_line:
                    if verbose:
                        print(f"行 {line_number}: 已修复 - {line[:50]}... -> {fixed_line[:50]}...", file=sys.stderr)
                    if remove_invalid and output_stream:
                        print(fixed_line, file=output_stream)
                else:
                    invalid_count += 1
                    if verbose:
                        print(f"行 {line_number}: 无效JSON - {line[:50]}...", file=sys.stderr)
    
    finally:
        # 关闭文件
        if input_stream != sys.stdin:
            input_stream.close()
        if output_stream and output_stream != sys.stdout:
            output_stream.close()
    
    # 输出统计信息
    if count_only or verbose:
        print(f"总行数: {total_count}", file=sys.stderr)
        print(f"有效JSON行: {valid_count}", file=sys.stderr)
        if fix_errors:
            print(f"已修复的JSON行: {fixed_count}", file=sys.stderr)
            print(f"无效JSON行: {invalid_count}", file=sys.stderr)
        else:
            print(f"无效JSON行: {invalid_count}", file=sys.stderr)
    
    return valid_count, invalid_count, fixed_count, total_count

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='检查JSONL文件，验证每行是否有效JSON，并可以选择过滤无效行')
    parser.add_argument('input', help='输入JSONL文件 (使用 "-" 从标准输入读取)')
    parser.add_argument('-o', '--output', help='输出文件 (使用 "-" 输出到标准输出)')
    parser.add_argument('-r', '--remove-invalid', action='store_true', help='移除无效的JSON行')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('-c', '--count-only', action='store_true', help='仅显示统计信息')
    parser.add_argument('-n', '--normalize-whitespace', action='store_true', help='规范化空白字符')
    parser.add_argument('-f', '--fix-errors', action='store_true', help='尝试修复简单的JSON错误')
    
    args = parser.parse_args()
    
    if args.count_only and args.remove_invalid:
        parser.error("--count-only 和 --remove-invalid 选项不能同时使用")
    
    # 检查输入文件是否存在
    if args.input != '-' and not Path(args.input).exists():
        print(f"错误: 输入文件 '{args.input}' 不存在", file=sys.stderr)
        return 1
    
    # 处理JSONL文件
    valid_count, invalid_count, fixed_count, total_count = process_jsonl_file(
        args.input, args.output, args.remove_invalid, args.verbose, args.count_only, 
        args.normalize_whitespace, args.fix_errors
    )
    
    # 根据是否存在无效行返回状态码
    if args.fix_errors:
        return 0 if invalid_count - fixed_count == 0 else 1
    else:
        return 0 if invalid_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 