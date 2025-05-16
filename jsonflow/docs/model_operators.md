# 模型操作符 (Model Operators)

模型操作符是 JSONFlow 中用于调用大语言模型的特殊操作符。这些操作符允许将 JSON 数据中的文本字段发送到 LLM 进行处理，并将模型的响应存储回 JSON 中。

## ModelInvoker

`ModelInvoker` 是 JSONFlow 的核心模型操作符，用于调用各种大语言模型。目前实现了基本的文本补全功能，支持通过 OpenAI 兼容的 API 调用各种模型，如 OpenAI 的 GPT 系列、Claude 等。

### 架构说明

当前的 ModelInvoker 是一个简单的文本补全操作符，它的工作流程如下：

1. 从输入 JSON 中提取提示文本
2. 构建消息列表（system 提示 + user 提示）
3. 调用 `call_llm` 方法获取模型响应
4. 将响应存储回 JSON 中

`call_llm` 方法是核心功能，它接收消息列表，使用 OpenAI SDK 调用模型 API，并返回模型响应。

### 使用方法

#### 基本用法

```python
from jsonflow.operators.model import ModelInvoker

# 创建一个模型调用操作符
model_op = ModelInvoker(
    model="gpt-3.5-turbo",
    prompt_field="input_text",
    response_field="ai_response",
    system_prompt="You are a helpful assistant.",
    api_key="your-api-key"  # 也可以通过 OPENAI_API_KEY 环境变量设置
)

# 处理单个 JSON 数据
result = model_op.process({
    "id": "example-1",
    "input_text": "解释什么是 JSON 数据流处理？",
    "metadata": {"category": "technical"}
})

# 结果将包含模型响应
print(result["ai_response"])
```

#### 在 Pipeline 中使用

```python
from jsonflow.core import Pipeline
from jsonflow.operators.json_ops import TextNormalizer
from jsonflow.operators.model import ModelInvoker

# 创建包含模型操作符的 Pipeline
pipeline = Pipeline([
    TextNormalizer(text_fields=["prompt"]),
    ModelInvoker(
        model="gpt-3.5-turbo",
        prompt_field="prompt",
        response_field="response",
        system_prompt="You are a helpful assistant."
    )
])

# 处理数据
result = pipeline.process({
    "id": "example-2",
    "prompt": "用简单的语言解释 JSON 格式。"
})
```

#### 直接调用 LLM (call_llm 方法)

ModelInvoker 提供了一个直接调用 LLM 的方法 `call_llm`，可以绕过 JSON 处理流程，直接发送消息列表到模型。这对于构建复杂的交互非常有用。

```python
from jsonflow.operators.model import ModelInvoker

# 创建模型调用操作符
model_op = ModelInvoker(
    model="gpt-3.5-turbo",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"  # 可选，用于自定义端点
)

# 准备消息列表
messages = [
    {"role": "system", "content": "You are a data science expert."},
    {"role": "user", "content": "解释 JSON 和 XML 之间的主要区别。"}
]

# 直接调用 LLM
response = model_op.call_llm(messages)
print(response)
```

### 自定义 API 端点

ModelInvoker 支持通过 `base_url` 参数连接到自定义 API 端点，这对于使用兼容 OpenAI API 的自托管模型或其他 API 服务（如 Claude）非常有用。

```python
# 使用自定义端点创建操作符
claude_op = ModelInvoker(
    model="claude-3-sonnet-20240229",
    api_key="your-api-key",
    base_url="https://api.anthropic.com/v1",  # Claude API 端点
    system_prompt="You are Claude, a helpful AI assistant."
)

# 处理数据
result = claude_op.process({"prompt": "Explain what JSONFlow is."})
```

### 参数说明

ModelInvoker 构造函数支持以下参数：

| 参数名 | 类型 | 描述 |
|--------|------|------|
| model | str | 模型名称，如 "gpt-3.5-turbo" |
| prompt_field | str | 输入字段名，默认为 "prompt" |
| response_field | str | 输出字段名，默认为 "response" |
| system_prompt | str, optional | 系统提示，用于设置模型的角色或行为 |
| api_key | str, optional | API 密钥，如不提供则从环境变量获取 |
| base_url | str, optional | 模型 API 的基础 URL，用于自定义端点 |
| max_tokens | int, optional | 生成的最大令牌数 |
| temperature | float | 采样温度，默认为 0.7 |
| **model_params | dict | 其他模型参数，会传递给 API 调用 |

## 高级用法

### 批量处理

ModelInvoker 可以处理 JSON 列表，对列表中的每个项目进行模型调用。

```python
# 处理 JSON 列表
results = model_op.process([
    {"prompt": "什么是 JSON？"},
    {"prompt": "什么是 Pipeline？"}
])
```

## 扩展 ModelInvoker

### 为什么扩展 ModelInvoker？

当前的 ModelInvoker 实现是一个简单的文本补全操作符，它有以下限制：

1. 只支持单轮对话（一个提示，一个回复）
2. 只支持文本输入和输出
3. 没有对话历史管理
4. 不支持工具调用、函数调用等高级功能

要实现更复杂的功能，如多轮对话、多模态输入输出、函数调用等，需要扩展 ModelInvoker 类。

### 如何扩展 ModelInvoker

扩展 ModelInvoker 的关键是继承该类并重写 `process` 方法来实现自定义逻辑，同时可以复用 `call_llm` 方法来实际调用模型。

#### 示例1：多轮对话操作符

```python
from jsonflow.operators.model import ModelInvoker
from typing import Dict, Any, List

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
```

#### 示例2：多模态输入操作符

```python
import base64
from jsonflow.operators.model import ModelInvoker
from typing import Dict, Any, List

class MultimodalInvoker(ModelInvoker):
    """支持多模态输入的模型操作符"""
    
    def __init__(self, 
                 model: str,
                 text_field: str = "text",
                 image_field: str = "image_path",
                 response_field: str = "response",
                 **kwargs):
        super().__init__(model=model, **kwargs)
        self.text_field = text_field
        self.image_field = image_field
        self.response_field = response_field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理包含文本和图像输入的请求
        
        Args:
            json_data: 包含文本和图像路径的JSON数据
            
        Returns:
            dict: 添加了模型响应的JSON数据
        """
        if not json_data or self.text_field not in json_data or self.image_field not in json_data:
            return json_data
            
        result = json_data.copy()
        
        # 获取文本和图像路径
        text = result[self.text_field]
        image_path = result[self.image_field]
        
        # 读取并编码图像
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error reading image: {e}")
            return result
        
        # 构建多模态消息
        messages = [
            {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }
        ]
        
        # 调用模型
        response = self.call_llm(messages)
        
        # 更新结果
        result[self.response_field] = response
        
        return result
```

#### 示例3：函数调用操作符

```python
import json
from jsonflow.operators.model import ModelInvoker
from typing import Dict, Any, List

class FunctionCallingInvoker(ModelInvoker):
    """支持函数调用的模型操作符"""
    
    def __init__(self, 
                 model: str,
                 prompt_field: str = "prompt",
                 response_field: str = "response",
                 functions_field: str = "functions",
                 function_results_field: str = "function_results",
                 **kwargs):
        super().__init__(model=model, **kwargs)
        self.prompt_field = prompt_field
        self.response_field = response_field
        self.functions_field = functions_field
        self.function_results_field = function_results_field
    
    def process(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理函数调用请求
        
        Args:
            json_data: 包含提示和可用函数的JSON数据
            
        Returns:
            dict: 添加了模型响应和函数调用结果的JSON数据
        """
        if not json_data or self.prompt_field not in json_data:
            return json_data
            
        result = json_data.copy()
        
        # 获取提示和函数定义
        prompt = result[self.prompt_field]
        functions = result.get(self.functions_field, [])
        
        if not functions:
            # 如果没有函数定义，就使用普通的处理逻辑
            messages = [
                {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            response = self.call_llm(messages)
            result[self.response_field] = response
            return result
        
        # 构建带函数定义的请求
        messages = [
            {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        # 添加函数调用相关参数
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
            
        try:
            import openai
            client = openai.OpenAI(**client_kwargs)
            
            # 调用API请求函数调用
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **self.model_params
            )
            
            function_calling_results = []
            
            # 处理函数调用响应
            message = response.choices[0].message
            result[self.response_field] = message.content or ""
            
            # 如果有函数调用
            if hasattr(message, 'function_call') and message.function_call:
                function_call = message.function_call
                function_calling_results.append({
                    "name": function_call.name,
                    "arguments": json.loads(function_call.arguments)
                })
            
            # 存储函数调用结果
            result[self.function_results_field] = function_calling_results
            
        except Exception as e:
            print(f"Error in function calling: {e}")
            messages = [
                {"role": "system", "content": self.system_prompt or "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
            # 出错时回退到普通响应
            response = self.call_llm(messages)
            result[self.response_field] = response
        
        return result
```

这些示例展示了如何通过继承 ModelInvoker 并重写 `process` 方法来实现更复杂的功能，同时复用 `call_llm` 方法来实际调用模型。根据你的具体需求，可以组合这些示例或创建自己的实现。

## 自定义模型操作符

如果需要支持更多的模型类型或特定的调用逻辑，可以通过继承 ModelOperator 基类来创建自定义的模型操作符。

```python
from jsonflow.core import ModelOperator

class MyCustomModelOperator(ModelOperator):
    """自定义模型操作符示例"""
    
    def __init__(self, model, **kwargs):
        super().__init__(name="MyModel", description="Custom model operator")
        self.model = model
        # 其他初始化逻辑
    
    def process_item(self, json_data):
        # 实现处理单个 JSON 项的逻辑
        # ...
        return processed_data 