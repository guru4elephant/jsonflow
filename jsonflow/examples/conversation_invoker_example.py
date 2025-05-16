#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
多轮对话模型示例

这个示例演示如何扩展ModelInvoker创建支持多轮对话的ConversationInvoker，
并在交互式会话中使用它。
"""

import os
import json
from typing import Dict, Any, List
from jsonflow.operators.model import ModelInvoker

class ConversationInvoker(ModelInvoker):
    """支持多轮对话的模型操作符"""
    
    def __init__(self, 
                 model: str,
                 history_field: str = "history",
                 message_field: str = "message",
                 response_field: str = "response",
                 **kwargs):
        super().__init__(model=model, **kwargs)
        self.history_field = history_field
        self.message_field = message_field
        self.response_field = response_field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理多轮对话
        
        Args:
            json_data: 包含对话历史和当前消息的JSON数据
            
        Returns:
            dict: 添加了模型响应的JSON数据
        """
        if not json_data or self.message_field not in json_data:
            return json_data
            
        result = json_data.copy()
        
        # 从输入中获取对话历史和当前消息
        history = result.get(self.history_field, [])
        current_message = result[self.message_field]
        
        # 构建完整的消息列表
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        
        # 添加历史消息
        for msg in history:
            messages.append(msg)
            
        # 添加当前消息
        messages.append({"role": "user", "content": current_message})
        
        # 调用模型
        response = self.call_llm(messages)
        
        # 更新对话历史
        history.append({"role": "user", "content": current_message})
        history.append({"role": "assistant", "content": response})
        
        # 更新结果
        result[self.response_field] = response
        result[self.history_field] = history
        
        return result


def main():
    """
    运行多轮对话模型示例。
    
    这个函数：
    1. 创建一个ConversationInvoker示例
    2. 进行一个简单的交互式对话
    3. 保存对话历史
    """
    # 设置API密钥（或从环境变量中获取）
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("警告: 未设置OPENAI_API_KEY环境变量。请设置后再运行，或在代码中直接设置。")
        api_key = "your-api-key"  # 替换为你的实际API密钥
    
    # 创建对话调用器
    conversation = ConversationInvoker(
        model="gpt-3.5-turbo",
        api_key=api_key,
        system_prompt="你是一个友好的助手，专长于解释技术概念。请用简洁清晰的语言回答问题。"
    )
    
    # 初始化会话状态
    session = {
        "history": [],
        "message": ""
    }
    
    print("\n=== JSONFlow 多轮对话示例 ===")
    print("输入'exit'或'quit'结束对话\n")
    
    # 对话循环
    try:
        while True:
            # 获取用户输入
            user_input = input("你: ")
            if user_input.lower() in ["exit", "quit", "退出"]:
                break
                
            # 更新会话状态
            session["message"] = user_input
            
            # 处理消息
            result = conversation.process(session)
            
            # 更新会话状态
            session = result
            
            # 显示响应
            print(f"\n助手: {result['response']}\n")
        
        # 保存对话历史
        with open("conversation_history.json", "w", encoding="utf-8") as f:
            json.dump(session["history"], f, ensure_ascii=False, indent=2)
        print("\n对话历史已保存到 conversation_history.json")
        
    except KeyboardInterrupt:
        print("\n已退出对话")
    except Exception as e:
        print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main() 