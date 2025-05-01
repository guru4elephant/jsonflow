"""
JSONFlow - 一个用于处理JSON数据的流式处理库

JSONFlow是一个简单而强大的库，可以用于处理JSON格式的数据。
它提供了一种方便的方式来构建数据处理管道，并支持同步和异步执行。
"""

__version__ = "0.1.0"

from jsonflow.core import Operator, JsonOperator, ModelOperator, Pipeline
from jsonflow.core import Executor, SyncExecutor, AsyncExecutor, MultiThreadExecutor, MultiProcessExecutor
from jsonflow.io import JsonLoader, JsonSaver 