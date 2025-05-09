import json
import requests
import time

# 火山引擎API配置
api_key = "XXXXXXXXX"  # API密钥
api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"  # 正确的API端点

def send_request(prompt, image_url=None, model="doubao-1-5-vision-pro-32k-250115"):
    """
    向火山引擎API发送请求
    
    参数:
        prompt (str): 发送给API的提示文本
        image_url (str, optional): 图片URL，如果提供则会发送多模态请求
        model (str): 使用的模型名称
    
    返回:
        dict: API响应结果
    """
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 构建content数组
    content = [{"type": "text", "text": prompt}]
    
    # 如果提供了图片URL，添加到content中
    if image_url:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        })
    
    # 请求体，按照CURL示例格式
    data = {
        "model": model,
        "messages": [
            {
                "role": "user", 
                "content": content
            }
        ]
    }
    
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=data,  # 使用json参数而不是data+dumps，处理序列化更简洁
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"请求失败: 状态码 {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"发送请求时出错: {str(e)}")
        return None

def main():
    """主函数，演示如何使用API"""
    # 用户输入提示
    user_prompt = input("请输入您的问题: ")
    
    # 询问是否要包含图片
    include_image = input("是否包含图片? (y/n): ").lower() == 'y'
    image_url = None
    if include_image:
        image_url = input("请输入图片URL: ")
    
    print("正在发送请求...")
    start_time = time.time()
    
    # 发送请求并获取响应
    result = send_request(user_prompt, image_url)
    
    end_time = time.time()
    print(f"请求耗时: {end_time - start_time:.2f} 秒")
    
    # 处理响应
    if result:
        try:
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
                print("\n回答:")
                print(answer)
            else:
                print("响应格式不符合预期:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
        except Exception as e:
            print(f"处理响应时出错: {str(e)}")
            print("原始响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("未能获取有效回答")

if __name__ == "__main__":
    main()

