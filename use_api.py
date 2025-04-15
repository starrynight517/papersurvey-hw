import requests
import json
import base64
import os
import mimetypes
import webbrowser
from urllib.parse import quote_plus

# 用户提供的API密钥
API_KEY = "YOUR_API_KEY_HERE"

# Gemini 2.5 Pro Exp模型API端点
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent"



import os
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

def encode_file(file_path):
    """将文件编码为base64格式"""
    try:
        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # 如果无法确定MIME类型，使用通用二进制类型
            mime_type = 'application/octet-stream'
        
        # 读取文件并进行base64编码
        with open(file_path, 'rb') as file:
            file_content = file.read()
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
        return {
            "mime_type": mime_type,
            "data": encoded_content
        }
    except Exception as e:
        print(f"文件编码错误: {e}")
        return None

def generate_content(prompt, file_path=None):
    """调用Gemini 2.5 Pro Exp模型API生成内容，支持文本和文件上传"""
    headers = {
        "Content-Type": "application/json"
    }
    
    # 准备请求内容
    parts = []
    
    # 添加文本提示
    if prompt:
        parts.append({"text": prompt})
    
    # 添加文件（如果提供）
    if file_path and os.path.exists(file_path):
        file_data = encode_file(file_path)
        if file_data:
            parts.append({
                "inline_data": {
                    "mime_type": file_data["mime_type"],
                    "data": file_data["data"]
                }
            })
    
    data = {
        "contents": [{
            "parts": parts
        }]
    }
    
    # 构建包含API密钥的URL
    url_with_key = f"{URL}?key={API_KEY}"
    
    try:
        # 增加超时设置，防止大文件上传时请求过早结束
        response = requests.post(url_with_key, headers=headers, json=data, timeout=120)
        response.raise_for_status()  # 检查请求是否成功
        
        result = response.json()
        return result
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        print("可能原因: 文件过大或网络连接问题，请尝试使用较小的文件或检查网络连接")
        return None
    except json.JSONDecodeError as e:
        print(f"无法解析响应JSON: {e}")
        return None


if __name__ == "__main__":
    while True:
        print("\n请选择功能:")
        print("1. 使用Gemini AI回答问题")
        print("2. 上传文件并使用Gemini AI分析")
        print("3. 退出")
        
        choice = input("请输入选项(1-3): ")
        
        if choice == "1":
            # 示例1：仅文本提示
            print("\n使用Gemini AI回答问题")
            user_prompt = input("请输入您的问题: ")
            result = generate_content(user_prompt)
            
            if result and "candidates" in result:
                # 提取生成的文本
                generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                print("\nGemini回复:")
                print(generated_text)
            else:
                print("\n无法获取有效响应")
                print("API返回:", result)
        
        elif choice == "2":
            # 示例2：上传文件并提问
            print("\n上传文件并使用Gemini AI分析")
            file_path = input("请输入要上传的文件路径: ")
            if os.path.exists(file_path):
                user_prompt = input("请输入关于此文件的问题: ")
                result = generate_content(user_prompt, file_path)
                
                if result and "candidates" in result:
                    # 提取生成的文本
                    generated_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    print("\nGemini回复:")
                    print(generated_text)
                else:
                    print("\n无法获取有效响应")
                    print("API返回:", result)
            else:
                print(f"文件 {file_path} 不存在")
        
            
        elif choice == "3":
            print("\n感谢使用，再见！")
            break
            
        else:
            print("\n无效选项，请重新输入")