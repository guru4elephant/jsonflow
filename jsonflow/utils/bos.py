#!/usr/bin/env python
# coding=utf-8

"""
Baidu Object Storage (BOS) utility module for JSONFlow.
Provides concurrent upload and download functionality.
"""

import os
import logging
import concurrent.futures
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union, Any

# Import Baidu BOS SDK
try:
    from baidubce.bce_client_configuration import BceClientConfiguration
    from baidubce.auth.bce_credentials import BceCredentials
    from baidubce.services.bos.bos_client import BosClient
    from baidubce import exception
except ImportError:
    raise ImportError(
        "Baidu BOS SDK is required. Please install it using: "
        "pip install bce-python-sdk"
    )


class BosHelper:
    """
    Helper class for Baidu Object Storage (BOS) operations.
    Supports concurrent upload and download of files.
    """

    def __init__(
        self,
        access_key_id: str = None,
        secret_access_key: str = None,
        endpoint: str = None,
        bucket: str = None,
        max_workers: int = None,
    ):
        """
        Initialize BOS Helper.

        Args:
            access_key_id (str, optional): BOS access key ID. Defaults to env var BOS_ACCESS_KEY.
            secret_access_key (str, optional): BOS secret access key. Defaults to env var BOS_SECRET_KEY.
            endpoint (str, optional): BOS endpoint. Defaults to env var BOS_HOST or 'bj.bcebos.com'.
            bucket (str, optional): Default bucket name. Defaults to env var BOS_BUCKET.
            max_workers (int, optional): Maximum number of worker threads/processes for concurrent operations.
        """
        self.access_key_id = access_key_id or os.environ.get("BOS_ACCESS_KEY")
        self.secret_access_key = secret_access_key or os.environ.get("BOS_SECRET_KEY")
        self.endpoint = endpoint or os.environ.get("BOS_HOST", "bj.bcebos.com")
        self.bucket = bucket or os.environ.get("BOS_BUCKET")
        self.max_workers = max_workers
        self.client = self._create_client()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for BOS operations."""
        logger = logging.getLogger("jsonflow.utils.bos")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _create_client(self) -> BosClient:
        """Create and return a BOS client."""
        if not self.access_key_id or not self.secret_access_key:
            raise ValueError(
                "BOS credentials not provided. Set access_key_id and secret_access_key "
                "or environment variables BOS_ACCESS_KEY and BOS_SECRET_KEY."
            )

        config = BceClientConfiguration(
            credentials=BceCredentials(self.access_key_id, self.secret_access_key),
            endpoint=self.endpoint,
        )
        return BosClient(config)

    def upload_file(
        self, local_file: str, remote_key: str, bucket: str = None
    ) -> Tuple[bool, str]:
        """
        Upload a single file to BOS.

        Args:
            local_file (str): Path to local file
            remote_key (str): Remote object key
            bucket (str, optional): Bucket name. Defaults to self.bucket.

        Returns:
            Tuple[bool, str]: (success, remote_url)
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        if not os.path.exists(local_file):
            self.logger.error(f"File not found: {local_file}")
            return False, ""

        try:
            self.client.put_object_from_file(bucket, remote_key, local_file)
            remote_url = f"https://{bucket}.{self.endpoint}/{remote_key}"
            self.logger.info(f"Uploaded: {local_file} -> {remote_url}")
            return True, remote_url
        except exception.BceHttpClientError as e:
            self.logger.error(f"Upload failed: {local_file} - {str(e)}")
            return False, ""

    def download_file(
        self, remote_key: str, local_file: str, bucket: str = None
    ) -> bool:
        """
        Download a single file from BOS.

        Args:
            remote_key (str): Remote object key
            local_file (str): Path to save the downloaded file
            bucket (str, optional): Bucket name. Defaults to self.bucket.

        Returns:
            bool: Success status
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(local_file)), exist_ok=True)
            
            # Download the file
            self.client.get_object_to_file(bucket, remote_key, local_file)
            self.logger.info(f"Downloaded: {remote_key} -> {local_file}")
            return True
        except exception.BceHttpClientError as e:
            self.logger.error(f"Download failed: {remote_key} - {str(e)}")
            return False

    def upload_directory(
        self,
        local_dir: str,
        remote_base_path: str,
        bucket: str = None,
        include_pattern: str = None,
        exclude_pattern: str = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Upload a directory to BOS with concurrent workers.

        Args:
            local_dir (str): Local directory path
            remote_base_path (str): Remote base path
            bucket (str, optional): Bucket name. Defaults to self.bucket.
            include_pattern (str, optional): Pattern to include files.
            exclude_pattern (str, optional): Pattern to exclude files.

        Returns:
            Tuple[List[str], List[str]]: (uploaded_urls, failed_files)
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        if not os.path.isdir(local_dir):
            self.logger.error(f"Directory not found: {local_dir}")
            return [], []

        # Get all files in the directory
        all_files = []
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(local_file_path, local_dir)
                remote_key = os.path.join(remote_base_path, rel_path).replace("\\", "/")
                all_files.append((local_file_path, remote_key))

        self.logger.info(f"Found {len(all_files)} files to upload")
        if not all_files:
            return [], []

        # Upload files concurrently
        uploaded_urls = []
        failed_files = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(
                    self.upload_file, local_file, remote_key, bucket
                ): (local_file, remote_key)
                for local_file, remote_key in all_files
            }

            for future in concurrent.futures.as_completed(future_to_file):
                local_file, remote_key = future_to_file[future]
                try:
                    success, url = future.result()
                    if success:
                        uploaded_urls.append(url)
                    else:
                        failed_files.append(local_file)
                except Exception as e:
                    self.logger.error(f"Error uploading {local_file}: {str(e)}")
                    failed_files.append(local_file)

        self.logger.info(
            f"Upload completed: {len(uploaded_urls)} succeeded, {len(failed_files)} failed"
        )
        return uploaded_urls, failed_files

    def download_directory(
        self,
        remote_prefix: str,
        local_dir: str,
        bucket: str = None,
        include_pattern: str = None,
        exclude_pattern: str = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Download files with a common prefix from BOS with concurrent workers.

        Args:
            remote_prefix (str): Remote prefix/directory
            local_dir (str): Local directory path
            bucket (str, optional): Bucket name. Defaults to self.bucket.
            include_pattern (str, optional): Pattern to include files.
            exclude_pattern (str, optional): Pattern to exclude files.

        Returns:
            Tuple[List[str], List[str]]: (downloaded_files, failed_keys)
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        # Create the local directory if it doesn't exist
        os.makedirs(local_dir, exist_ok=True)

        # List objects with the given prefix
        try:
            response = self.client.list_objects(bucket, prefix=remote_prefix)
        except exception.BceHttpClientError as e:
            self.logger.error(f"Failed to list objects: {str(e)}")
            return [], []

        if not hasattr(response, "contents") or not response.contents:
            self.logger.info(f"No objects found with prefix {remote_prefix}")
            return [], []

        # Prepare download tasks
        download_tasks = []
        for obj in response.contents:
            remote_key = obj.key
            rel_path = remote_key
            if remote_prefix and remote_key.startswith(remote_prefix):
                rel_path = remote_key[len(remote_prefix):].lstrip("/")
            
            local_file_path = os.path.join(local_dir, rel_path)
            download_tasks.append((remote_key, local_file_path))

        self.logger.info(f"Found {len(download_tasks)} files to download")

        # Download files concurrently
        downloaded_files = []
        failed_keys = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_key = {
                executor.submit(
                    self.download_file, remote_key, local_file, bucket
                ): (remote_key, local_file)
                for remote_key, local_file in download_tasks
            }

            for future in concurrent.futures.as_completed(future_to_key):
                remote_key, local_file = future_to_key[future]
                try:
                    success = future.result()
                    if success:
                        downloaded_files.append(local_file)
                    else:
                        failed_keys.append(remote_key)
                except Exception as e:
                    self.logger.error(f"Error downloading {remote_key}: {str(e)}")
                    failed_keys.append(remote_key)

        self.logger.info(
            f"Download completed: {len(downloaded_files)} succeeded, {len(failed_keys)} failed"
        )
        return downloaded_files, failed_keys

    def check_bucket_exists(self, bucket: str = None) -> bool:
        """
        Check if a bucket exists.

        Args:
            bucket (str, optional): Bucket name. Defaults to self.bucket.

        Returns:
            bool: True if the bucket exists, False otherwise
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        try:
            return self.client.does_bucket_exist(bucket)
        except exception.BceHttpClientError as e:
            self.logger.error(f"Failed to check bucket: {str(e)}")
            return False

    def create_bucket(self, bucket: str = None) -> bool:
        """
        Create a new bucket.

        Args:
            bucket (str, optional): Bucket name. Defaults to self.bucket.

        Returns:
            bool: True if successful, False otherwise
        """
        bucket = bucket or self.bucket
        if not bucket:
            raise ValueError("Bucket name not provided.")

        try:
            self.client.create_bucket(bucket)
            self.logger.info(f"Created bucket: {bucket}")
            return True
        except exception.BceHttpClientError as e:
            self.logger.error(f"Failed to create bucket: {str(e)}")
            return False


# Simplified functions for direct use
def upload_file(
    local_file: str,
    remote_key: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
) -> Tuple[bool, str]:
    """
    Simple function to upload a single file to BOS.

    Args:
        local_file (str): Path to local file
        remote_key (str): Remote object key
        bucket (str): Bucket name
        access_key_id (str, optional): BOS access key ID
        secret_access_key (str, optional): BOS secret access key
        endpoint (str, optional): BOS endpoint

    Returns:
        Tuple[bool, str]: (success, remote_url)
    """
    helper = BosHelper(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint=endpoint,
        bucket=bucket,
    )
    return helper.upload_file(local_file, remote_key)


def download_file(
    remote_key: str,
    local_file: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
) -> bool:
    """
    Simple function to download a single file from BOS.

    Args:
        remote_key (str): Remote object key
        local_file (str): Path to save the downloaded file
        bucket (str): Bucket name
        access_key_id (str, optional): BOS access key ID
        secret_access_key (str, optional): BOS secret access key
        endpoint (str, optional): BOS endpoint

    Returns:
        bool: Success status
    """
    helper = BosHelper(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint=endpoint,
        bucket=bucket,
    )
    return helper.download_file(remote_key, local_file)


def upload_directory(
    local_dir: str,
    remote_base_path: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
    max_workers: int = None,
) -> Tuple[List[str], List[str]]:
    """
    Simple function to upload a directory to BOS with concurrent workers.

    Args:
        local_dir (str): Local directory path
        remote_base_path (str): Remote base path
        bucket (str): Bucket name
        access_key_id (str, optional): BOS access key ID
        secret_access_key (str, optional): BOS secret access key
        endpoint (str, optional): BOS endpoint
        max_workers (int, optional): Maximum number of worker threads

    Returns:
        Tuple[List[str], List[str]]: (uploaded_urls, failed_files)
    """
    helper = BosHelper(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint=endpoint,
        bucket=bucket,
        max_workers=max_workers,
    )
    return helper.upload_directory(local_dir, remote_base_path)


def download_directory(
    remote_prefix: str,
    local_dir: str,
    bucket: str,
    access_key_id: str = None,
    secret_access_key: str = None,
    endpoint: str = None,
    max_workers: int = None,
) -> Tuple[List[str], List[str]]:
    """
    Simple function to download files with a common prefix from BOS with concurrent workers.

    Args:
        remote_prefix (str): Remote prefix/directory
        local_dir (str): Local directory path
        bucket (str): Bucket name
        access_key_id (str, optional): BOS access key ID
        secret_access_key (str, optional): BOS secret access key
        endpoint (str, optional): BOS endpoint
        max_workers (int, optional): Maximum number of worker threads

    Returns:
        Tuple[List[str], List[str]]: (downloaded_files, failed_keys)
    """
    helper = BosHelper(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        endpoint=endpoint,
        bucket=bucket,
        max_workers=max_workers,
    )
    return helper.download_directory(remote_prefix, local_dir) 