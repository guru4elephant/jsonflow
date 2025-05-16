#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Direct Call Example

This example demonstrates how to use the ModelInvoker's call_llm method
to directly call a large language model with a custom endpoint.
"""

import os
from jsonflow.operators.model import ModelInvoker

def main():
    """
    Run the LLM direct call example.
    
    This function:
    1. Creates a ModelInvoker with a custom endpoint
    2. Sends a direct message to the LLM using call_llm
    3. Prints the response
    """
    # Set your API key (or it will use OPENAI_API_KEY from environment)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Warning: OPENAI_API_KEY environment variable not set. Please set it before running.")
        api_key = "your-api-key"  # Replace with your actual API key
    
    # Initialize the ModelInvoker with endpoint
    model_invoker = ModelInvoker(
        model="gpt-3.5-turbo",
        api_key=api_key,
        base_url="https://api.openai.com/v1",  # Default OpenAI endpoint (can be changed for other providers)
        system_prompt="You are a helpful assistant, expert in JSON data processing."
    )
    
    # Prepare messages for a direct call
    messages = [
        {"role": "system", "content": "You are an AI assistant that specializes in explaining technical concepts simply."},
        {"role": "user", "content": "请用简单的语言解释什么是 JSON 数据流处理？"}
    ]
    
    # Make the direct call
    print("\n=== JSONFlow Direct LLM Call Example ===\n")
    print("Sending message to LLM...\n")
    
    try:
        response = model_invoker.call_llm(messages)
        print(f"Response from LLM:\n\n{response}\n")
    except Exception as e:
        print(f"Error calling LLM: {e}")
    
    # Example: Process a JSON object using the standard process method
    print("\n=== Using ModelInvoker.process method ===\n")
    
    json_data = {
        "id": "example-1",
        "prompt": "用简单的语言解释什么是 Pipeline 模式？",
        "metadata": {"category": "technical"}
    }
    
    try:
        result = model_invoker.process(json_data)
        print(f"Input prompt: {json_data['prompt']}\n")
        print(f"Response: {result['response']}\n")
    except Exception as e:
        print(f"Error processing JSON: {e}")


if __name__ == "__main__":
    main() 