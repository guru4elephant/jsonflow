#!/usr/bin/env python
# coding=utf-8

"""
展示如何使用JSONFlow的BOS工具上传和下载文件
"""

import os
import sys
import argparse
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from jsonflow.utils.bos import (
    BosHelper, 
    upload_file, 
    download_file, 
    upload_directory, 
    download_directory
)
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import JsonTransformer


def upload_files_from_json(
    json_file, 
    local_dir, 
    remote_base_path, 
    bucket,
    access_key_id=None, 
    secret_access_key=None, 
    endpoint=None,
    max_workers=None
):
    """从JSON文件中读取文件路径进行上传"""
    # 处理JSON文件的简单Pipeline
    process_pipeline = Pipeline([
        # 添加本地和远程路径
        JsonTransformer(lambda data: {
            **data,
            "local_path": os.path.join(local_dir, data.get("filename", "")),
            "remote_key": os.path.join(remote_base_path, data.get("filename", "")).replace("\\", "/")
        })
    ])

    # 创建BOS辅助工具
    bos_helper = BosHelper(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint=endpoint,
        bucket=bucket,
        max_workers=max_workers
    )

    # 检查存储桶是否存在
    if not bos_helper.check_bucket_exists():
        print(f"Bucket '{bucket}' does not exist.")
        create_bucket = input("Do you want to create it? (y/n): ")
        if create_bucket.lower() == 'y':
            if bos_helper.create_bucket():
                print(f"Bucket '{bucket}' created successfully.")
            else:
                print("Failed to create bucket. Exiting.")
                return
        else:
            print("Exiting as bucket does not exist.")
            return

    # 从JSON文件加载数据
    json_loader = JsonLoader(json_file)
    
    # 创建结果保存器
    result_saver = JsonSaver(json_file.replace('.jsonl', '_results.jsonl'))
    
    # 处理并上传每个文件
    uploaded_count = 0
    failed_count = 0
    
    for json_item in json_loader:
        # 处理JSON数据
        processed_item = process_pipeline.process(json_item)
        
        # 检查文件是否存在
        local_path = processed_item.get("local_path")
        remote_key = processed_item.get("remote_key")
        
        if not local_path or not remote_key:
            print(f"Warning: Missing local_path or remote_key in: {processed_item}")
            processed_item["upload_success"] = False
            processed_item["error"] = "Missing local_path or remote_key"
            failed_count += 1
            result_saver.write(processed_item)
            continue
        
        if not os.path.exists(local_path):
            print(f"Warning: File does not exist: {local_path}")
            processed_item["upload_success"] = False
            processed_item["error"] = "File does not exist"
            failed_count += 1
            result_saver.write(processed_item)
            continue
        
        # 上传文件
        success, remote_url = bos_helper.upload_file(local_path, remote_key)
        
        if success:
            print(f"Uploaded: {local_path} -> {remote_url}")
            processed_item["upload_success"] = True
            processed_item["remote_url"] = remote_url
            uploaded_count += 1
        else:
            print(f"Failed to upload: {local_path}")
            processed_item["upload_success"] = False
            processed_item["error"] = "Upload failed"
            failed_count += 1
        
        # 保存结果
        result_saver.write(processed_item)
    
    print(f"\nUpload completed: {uploaded_count} succeeded, {failed_count} failed")


def download_files_to_json(
    remote_prefix,
    local_dir,
    bucket,
    output_file="download_results.jsonl",
    access_key_id=None,
    secret_access_key=None,
    endpoint=None,
    max_workers=None
):
    """从BOS下载文件并将结果保存到JSON文件"""
    # 创建BOS辅助工具
    bos_helper = BosHelper(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint=endpoint,
        bucket=bucket,
        max_workers=max_workers
    )
    
    # 检查存储桶是否存在
    if not bos_helper.check_bucket_exists():
        print(f"Bucket '{bucket}' does not exist. Exiting.")
        return
    
    # 下载文件
    downloaded_files, failed_keys = bos_helper.download_directory(
        remote_prefix=remote_prefix,
        local_dir=local_dir
    )
    
    # 创建结果保存器
    result_saver = JsonSaver(output_file)
    
    # 保存结果
    for file_path in downloaded_files:
        result_saver.write({
            "status": "success",
            "local_path": file_path,
            "filename": os.path.basename(file_path)
        })
    
    for key in failed_keys:
        result_saver.write({
            "status": "failed",
            "remote_key": key,
            "filename": os.path.basename(key)
        })
    
    print(f"\nDownload completed: {len(downloaded_files)} succeeded, {len(failed_keys)} failed")
    print(f"Results saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='JSONFlow BOS Tools Example')
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 上传命令
    upload_parser = subparsers.add_parser('upload', help='Upload files from JSON list')
    upload_parser.add_argument('--json-file', '-j', type=str, required=True,
                              help='JSONL file with file information')
    upload_parser.add_argument('--local-dir', '-l', type=str, required=True,
                              help='Local directory containing files')
    upload_parser.add_argument('--remote-path', '-r', type=str, required=True,
                              help='Remote base path for uploaded files')
    upload_parser.add_argument('--bucket', '-b', type=str, required=True,
                              help='BOS bucket name')
    upload_parser.add_argument('--access-key', type=str, 
                              help='BOS access key ID (default from BOS_ACCESS_KEY env)')
    upload_parser.add_argument('--secret-key', type=str,
                              help='BOS secret key (default from BOS_SECRET_KEY env)')
    upload_parser.add_argument('--endpoint', type=str, 
                              help='BOS endpoint (default from BOS_HOST env or bj.bcebos.com)')
    upload_parser.add_argument('--max-workers', type=int, default=None,
                              help='Maximum number of workers for concurrent uploads')
    
    # 下载命令
    download_parser = subparsers.add_parser('download', help='Download files from BOS')
    download_parser.add_argument('--remote-prefix', '-r', type=str, required=True,
                                help='Remote prefix/directory to download from')
    download_parser.add_argument('--local-dir', '-l', type=str, required=True,
                                help='Local directory to save files')
    download_parser.add_argument('--bucket', '-b', type=str, required=True,
                                help='BOS bucket name')
    download_parser.add_argument('--output-file', '-o', type=str, default='download_results.jsonl',
                                help='Output JSONL file to save results')
    download_parser.add_argument('--access-key', type=str,
                                help='BOS access key ID (default from BOS_ACCESS_KEY env)')
    download_parser.add_argument('--secret-key', type=str,
                                help='BOS secret key (default from BOS_SECRET_KEY env)')
    download_parser.add_argument('--endpoint', type=str,
                                help='BOS endpoint (default from BOS_HOST env or bj.bcebos.com)')
    download_parser.add_argument('--max-workers', type=int, default=None,
                                help='Maximum number of workers for concurrent downloads')
    
    # 解析参数
    args = parser.parse_args()
    
    if args.command == 'upload':
        upload_files_from_json(
            json_file=args.json_file,
            local_dir=args.local_dir,
            remote_base_path=args.remote_path,
            bucket=args.bucket,
            access_key_id=args.access_key,
            secret_access_key=args.secret_key,
            endpoint=args.endpoint,
            max_workers=args.max_workers
        )
    elif args.command == 'download':
        download_files_to_json(
            remote_prefix=args.remote_prefix,
            local_dir=args.local_dir,
            bucket=args.bucket,
            output_file=args.output_file,
            access_key_id=args.access_key,
            secret_access_key=args.secret_key,
            endpoint=args.endpoint,
            max_workers=args.max_workers
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 