# Using Claude Models with JSONFlow CLI

This guide demonstrates how to use Claude models with the JSONFlow command-line interface.

## Prerequisites

- JSONFlow installed (`pip install jsonflow`)
- OpenAI API key (used for authentication with Claude-compatible endpoints)
- Access to a Claude-compatible API endpoint

## Basic Usage

### Process a JSONL file with Claude

```bash
jsonflow model input.jsonl output.jsonl \
  --model "claude-3-7-sonnet-20250219" \
  --prompt-field "prompt" \
  --response-field "response" \
  --system-prompt "You are a helpful AI assistant." \
  --base-url "https://your-claude-compatible-api-endpoint.com/v1"
```

### Process with Environment Variables

You can also set the API key using environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
jsonflow model input.jsonl output.jsonl \
  --model "claude-3-7-sonnet-20250219" \
  --base-url "https://your-claude-compatible-api-endpoint.com/v1"
```

## Input Format

The input JSONL file should contain JSON objects with the prompt field (default is "prompt"):

```json
{"prompt": "Tell me a joke"}
{"prompt": "What is quantum computing?"}
```

## Output Format

The output will be a JSONL file with the original data plus the response field:

```json
{"prompt": "Tell me a joke", "response": "Why did the chicken cross the road? To get to the other side!"}
{"prompt": "What is quantum computing?", "response": "Quantum computing is a type of computing..."}
```

## Combining with Text Normalization

You can normalize text before sending it to Claude by first using the `normalize` command:

```bash
# First normalize the text
jsonflow normalize input.jsonl normalized.jsonl --fields prompt --lower

# Then process with Claude
jsonflow model normalized.jsonl output.jsonl \
  --model "claude-3-7-sonnet-20250219" \
  --base-url "https://your-claude-compatible-api-endpoint.com/v1"
```

## Supported Claude Models

- claude-3-opus-20240229
- claude-3-sonnet-20240229
- claude-3-haiku-20240307
- claude-3-7-sonnet-20250219
- (And other versions as they become available) 