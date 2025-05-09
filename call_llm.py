#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import argparse
from openai import OpenAI
from openai import APIError, APIConnectionError, AuthenticationError

# API Configuration
API_CONFIG = {
    "key": "sk-ns5Vw38U9BiOfMX7nuf4gEtzKmE9avkr74Gb85U0EkyObec4",  # API密钥可能需要更新
    "url": "http://ai.wenyue8.com:15588/v1",
    "models": [
        "gpt-3.5-turbo",
        "gpt-4",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229"
    ],
    "max_concurrency": 5,
    "timeout": 240,
}


client = OpenAI(api_key=API_CONFIG["key"], base_url="http://ai.wenyue8.com:15588/v1")

response = client.chat.completions.create(
    model="claude-3-7-sonnet-20250219",
    messages=[
        {"role": "system", "content": "请用中文回答"},
        {"role": "user", "content": "你好"},
    ],
    stream=False
)

print(response.choices[0].message.content)