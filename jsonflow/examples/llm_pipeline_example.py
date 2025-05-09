#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Claude Model Example

This example demonstrates how to use a Claude model with the jsonflow library
via the ModelInvoker operator.
"""

import os
import json
from jsonflow.core import Pipeline
from jsonflow.io import JsonLoader, JsonSaver
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

def main():
    """
    Run the Claude model pipeline example.
    
    This function:
    1. Sets up a pipeline with a TextNormalizer and ModelInvoker for Claude
    2. Processes a sample input with the pipeline
    3. Saves the result to a file
    """
    # Set API key and base URL for the Claude model
    os.environ["OPENAI_API_KEY"] = "sk-ns5Vw38U9BiOfMX7nuf4gEtzKmE9avkr74Gb85U0EkyObec4"  # Replace with your actual API key
    
    # Create a pipeline with Claude model
    pipeline = Pipeline([
        TextNormalizer(text_fields=["prompt"]),
        ModelInvoker(
            model="claude-3-7-sonnet-20250219",
            prompt_field="prompt",
            response_field="response",
            system_prompt="You are a helpful AI assistant. Please provide concise, accurate responses.",
            openai_params={"base_url": "http://ai.wenyue8.com:15588/v1"}  # Claude-compatible API endpoint
        )
    ])
    
    # Sample input data
    sample_input = {
        "id": "sample-1",
        "prompt": "Explain the concept of JSON streaming in data processing pipelines.",
        "metadata": {
            "category": "technical",
            "max_tokens": 200
        }
    }
    
    # Process the input
    result = pipeline.process(sample_input)
    
    # Print the result
    print(f"Input prompt: {sample_input['prompt']}\n")
    print(f"Claude response: {result['response']}\n")
    
    # Save the result to a file
    with JsonSaver("claude_response.jsonl") as saver:
        saver.write(result)
    print("Result saved to claude_response.jsonl")

    # Process a JSONL file if it exists
    try:
        # Check if input.jsonl exists
        if os.path.exists("input.jsonl"):
            print("\nProcessing input.jsonl...")
            
            # Load and process the JSONL file
            json_loader = JsonLoader("input.jsonl")
            processed_results = []
            
            for json_data in json_loader:
                processed_data = pipeline.process(json_data)
                processed_results.append(processed_data)
            
            # Using write_all method to save all results at once
            JsonSaver.to_file("claude_results.jsonl", processed_results)
            print("JSONL processing complete. Results saved to claude_results.jsonl")
    except Exception as e:
        print(f"Error processing JSONL file: {e}")

if __name__ == "__main__":
    main() 