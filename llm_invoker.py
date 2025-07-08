import streamlit as st
import boto3
import json
import time
import datetime
import pandas as pd
import uuid
import os
import tiktoken

# 定義缺少的全局變量
# 初始化 tiktoken 編碼器 (用於計算 tokens) - 適用於 Claude 的 tokenizer
ENCODING_NAME = "cl100k_base"  # Claude uses this encoding
tokenizer = tiktoken.get_encoding(ENCODING_NAME)
anthropic_version = "bedrock-2023-05-31"  # Anthropic API 版本
claude_3_7 = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

max_token_length = 131072  # Claude 的最大 tokens 限制

class LLMInvoker:
    """LLM 調用基礎類"""
    
    def __init__(self):
        self.name = "Base LLM"
    
    def invoke(self, prompt, system_prompt="", temperature=0.7, top_p=0.9, top_k=40, max_tokens=max_token_length):
        """基礎調用方法，子類需要重寫"""
        raise NotImplementedError("子類必須實現此方法")
    
    def check_connection(self):
        """檢查連接，子類需要重寫"""
        raise NotImplementedError("子類必須實現此方法")
    
    def num_tokens_from_string(self, string):
        """估算令牌數量"""
        try:
            encoding = tiktoken.encoding_for_model("cl100k_base")  # 通用編碼器
            return len(encoding.encode(string))
        except:
            # 簡易估算
            return len(string) // 4

class ClaudeInvoker(LLMInvoker):
    """Anthropic Claude 調用類"""
    
    def __init__(self, region="us-east-2"):
        super().__init__()
        self.name = "Claude (Anthropic)"
        self.anthropic_version = anthropic_version
        self.default_model = claude_3_7
        self.region = region
    
    def get_client(self, region=None):
        """獲取 Bedrock 客戶端"""
        region = region or self.region
        bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        return bedrock_runtime
    
    def invoke(self, prompt, system_prompt="", temperature=0.7, top_p=0.9, top_k=40, max_tokens=max_token_length, model=None):
        """調用 Claude API"""
        bedrock = self.get_client()
        model_id = model or self.default_model
        
        # 構建請求體
        request_body = {
            "anthropic_version": self.anthropic_version,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # 如果有系統提示，添加到請求中
        if system_prompt:
            request_body["system"] = system_prompt
        
        start_time = time.time()
        
        # 調用 API
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # 解析響應
        response_body = json.loads(response.get("body").read().decode("utf-8"))
        process_time = time.time() - start_time
        
        return {
            "content": response_body["content"][0]["text"],
            "usage": response_body.get("usage", {"input_tokens": 0, "output_tokens": 0}),
            "process_time": process_time
        }
    
    def check_connection(self):
        """檢查連接是否正常"""
        try:
            bedrock = self.get_client()
            # 使用簡單提示測試連接
            request_body = {
                "anthropic_version": self.anthropic_version,
                "max_tokens": 10,
                "temperature": 0,
                "messages": [
                    {
                        "role": "user",
                        "content": "Hello, can you hear me?"
                    }
                ]
            }
            
            response = bedrock.invoke_model(
                modelId=self.default_model,
                body=json.dumps(request_body)
            )
            
            # 如果能獲取到響應，則連接正常
            return True, "連接正常"
        except Exception as e:
            return False, f"連接錯誤: {str(e)}"

class OpenAIInvoker(LLMInvoker):
    """OpenAI GPT 調用類 (示例實現)"""
    
    def __init__(self, api_key=None):
        super().__init__()
        self.name = "GPT (OpenAI)"
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.default_model = "gpt-4o"
    
    def invoke(self, prompt, system_prompt="", temperature=0.7, top_p=0.9, top_k=None, max_tokens=max_token_length, model=None):
        """調用 OpenAI API (示例實現)"""
        # 這裡需要實際實現 OpenAI API 的調用邏輯
        # 為了示例，返回一個模擬的響應
        return {
            "content": f"OpenAI 響應: {prompt[:30]}...",
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "process_time": 0.5
        }
    
    def check_connection(self):
        """檢查連接是否正常 (示例實現)"""
        if self.api_key:
            return True, "連接正常"
        else:
            return False, "未設置 API Key"

def process_image(image_file):
    """處理上傳的圖片，返回 Base64 編碼或使用 OCR 提取文本"""
    import base64
    import io
    
    # 將圖片轉換為 Base64
    image_bytes = io.BytesIO(image_file.getvalue())
    encoded = base64.b64encode(image_bytes.read()).decode('utf-8')
    
    return encoded

# 如果使用 Claude 3 Vision，可以添加以下代碼
class ClaudeVisionInvoker(ClaudeInvoker):
    """Claude Vision 調用類"""
    
    def __init__(self, region="us-east-1"):
        super().__init__(region)
        self.name = "Claude Vision (Anthropic)"
        self.default_model = "anthropic.claude-3-sonnet-20240229-v1:0"  # 確保使用支持圖片的模型
    
    def invoke_with_image(self, prompt, image_base64, system_prompt="", temperature=0.7, top_p=0.9, top_k=40, max_tokens=max_token_length):
        """調用 Claude Vision API"""
        bedrock = self.get_client()
        
        # 構建請求體
        request_body = {
            "anthropic_version": self.anthropic_version,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        if system_prompt:
            request_body["system"] = system_prompt
        
        start_time = time.time()
        
        # 調用 API
        response = bedrock.invoke_model(
            modelId=self.default_model,
            body=json.dumps(request_body)
        )
        
        # 解析響應
        response_body = json.loads(response.get("body").read().decode("utf-8"))
        process_time = time.time() - start_time
        
        return {
            "content": response_body["content"][0]["text"],
            "usage": response_body.get("usage", {"input_tokens": 0, "output_tokens": 0}),
            "process_time": process_time
        }

# LLM 工廠類
class LLMFactory:
    """LLM 工廠類，用於創建不同的 LLM 調用實例"""
    
    @staticmethod
    def create_llm(llm_type, **kwargs):
        """創建 LLM 實例"""
        if llm_type.lower() == "claude":
            return ClaudeInvoker(**kwargs)
        elif llm_type.lower() == "openai":
            return OpenAIInvoker(**kwargs)
        else:
            raise ValueError(f"不支持的 LLM 類型: {llm_type}")

# 在 llm_invoker.py 中修改 ParameterPresets 類

class ParameterPresets:
    """預定義的參數組合"""
    
    @staticmethod
    def get_presets():
        """獲取所有預設參數組合"""
        return {
            "平衡": {
                "description": "平衡的設置，適合一般對話",
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 1024
            },
            "創意": {
                "description": "高創造力設置，適合腦洞大開的討論和創意寫作",
                "temperature": 0.9,
                "top_p": 0.95,
                "top_k": 50,
                "max_tokens": 2048
            },
            "精確": {
                "description": "低溫度設置，適合需要精確回答的場景",
                "temperature": 0.2,
                "top_p": 0.8,
                "top_k": 30,
                "max_tokens": 1024
            },
            "編程": {
                "description": "適合程式碼生成的設置",
                "temperature": 0.1,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 4096
            },
            "分析": {
                "description": "適合深度分析和規劃的設置",
                "temperature": 0.4,
                "top_p": 0.85,
                "top_k": 40,
                "max_tokens": 3072
            }
        }
    
    @staticmethod
    def get_preset(name):
        """獲取指定名稱的預設參數"""
        presets = ParameterPresets.get_presets()
        return presets.get(name, presets["平衡"])