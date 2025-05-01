"""
执行器模块

该模块定义了各种执行器，用于执行Pipeline。
"""

import concurrent.futures
import asyncio
from typing import List, Dict, Any

class Executor:
    """
    执行器基类
    
    所有执行器都应该继承这个类，并实现execute和execute_all方法。
    """
    
    def __init__(self, pipeline):
        """
        初始化执行器
        
        Args:
            pipeline: 要执行的Pipeline实例
        """
        self.pipeline = pipeline
    
    def execute(self, json_data):
        """
        执行Pipeline处理单个JSON数据
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        return self.pipeline.process(json_data)
    
    def execute_all(self, json_data_list):
        """
        批量执行Pipeline处理多个JSON数据
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表
        """
        results = []
        for data in json_data_list:
            results.append(self.execute(data))
        return results


class SyncExecutor(Executor):
    """
    同步执行器
    
    这个执行器按顺序同步执行Pipeline。
    """
    pass


class AsyncExecutor(Executor):
    """
    异步执行器
    
    这个执行器使用asyncio异步执行Pipeline。
    """
    
    async def execute_async(self, json_data):
        """
        异步执行Pipeline处理单个JSON数据
        
        Args:
            json_data (dict): 输入的JSON数据
            
        Returns:
            dict: 处理后的JSON数据
        """
        # 这里假设Pipeline是同步的，在实际执行时包装为异步任务
        # 如果Pipeline本身支持异步，这里可以直接调用异步方法
        return await asyncio.to_thread(self.pipeline.process, json_data)
    
    async def execute_all_async(self, json_data_list):
        """
        异步批量执行Pipeline处理多个JSON数据
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表
        """
        tasks = [self.execute_async(data) for data in json_data_list]
        return await asyncio.gather(*tasks)
    
    def execute_all(self, json_data_list):
        """
        异步批量执行的同步封装
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表
        """
        return asyncio.run(self.execute_all_async(json_data_list))


class MultiThreadExecutor(Executor):
    """
    多线程执行器
    
    这个执行器使用线程池并发执行Pipeline。
    """
    
    def __init__(self, pipeline, max_workers=None):
        """
        初始化多线程执行器
        
        Args:
            pipeline: 要执行的Pipeline实例
            max_workers (int, optional): 最大工作线程数，默认为None（由线程池决定）
        """
        super().__init__(pipeline)
        self.max_workers = max_workers
    
    def execute_all(self, json_data_list):
        """
        使用多线程批量执行Pipeline处理多个JSON数据
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表，与输入列表顺序一致
        """
        results = [None] * len(json_data_list)
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.execute, data): i 
                for i, data in enumerate(json_data_list)
            }
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    # 在实际应用中可能需要更复杂的错误处理
                    print(f"Error processing item at index {index}: {e}")
                    results[index] = {"error": str(e)}
        return results


class MultiProcessExecutor(Executor):
    """
    多进程执行器
    
    这个执行器使用进程池并发执行Pipeline。
    """
    
    def __init__(self, pipeline, max_workers=None):
        """
        初始化多进程执行器
        
        Args:
            pipeline: 要执行的Pipeline实例
            max_workers (int, optional): 最大工作进程数，默认为None（由进程池决定）
        """
        super().__init__(pipeline)
        self.max_workers = max_workers
    
    def execute_all(self, json_data_list):
        """
        使用多进程批量执行Pipeline处理多个JSON数据
        
        注意: 由于使用了进程池，Pipeline中的操作符必须是可序列化的。
        
        Args:
            json_data_list (list): 输入的JSON数据列表
            
        Returns:
            list: 处理后的JSON数据列表，与输入列表顺序一致
        """
        results = [None] * len(json_data_list)
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self.execute, data): i 
                for i, data in enumerate(json_data_list)
            }
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    # 在实际应用中可能需要更复杂的错误处理
                    print(f"Error processing item at index {index}: {e}")
                    results[index] = {"error": str(e)}
        return results 