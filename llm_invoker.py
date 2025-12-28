import streamlit as st
import boto3
import json
import time
import datetime
import pandas as pd
import uuid
import os
import tiktoken
import google.generativeai as genai
from google.cloud import aiplatform

# 定義缺少的全局變量
# 初始化 tiktoken 編碼器 (用於計算 tokens) - 適用於 Claude 的 tokenizer
ENCODING_NAME = "cl100k_base"  # Claude uses this encoding
tokenizer = tiktoken.get_encoding(ENCODING_NAME)
anthropic_version = "bedrock-2023-05-31"  # Anthropic API 版本
claude_3_7 = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"

max_token_length = 131072  # Claude 的最大 tokens 限制

# Gemini model constants
GEMINI_FLASH_MODEL = "gemini-3-flash-preview"
GEMINI_PRO_MODEL = "gemini-3-pro-preview"

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

class GeminiInvoker(LLMInvoker):
    """Google Gemini 調用類 (API Key 模式)"""

    def __init__(self, api_key=None, model=GEMINI_FLASH_MODEL):
        super().__init__()
        self.name = "Gemini (Google AI)"
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.default_model = model

        # 配置 Gemini API
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def invoke(self, prompt, system_prompt="", temperature=0.7, top_p=0.9, top_k=40, max_tokens=max_token_length, model=None):
        """調用 Gemini API"""
        if not self.api_key:
            raise ValueError("未設置 GEMINI_API_KEY")

        model_name = model or self.default_model

        # 配置生成參數
        generation_config = {
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": min(max_tokens, 8192),  # Gemini 限制
        }

        try:
            # 創建模型實例
            model_instance = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_prompt if system_prompt else None
            )

            start_time = time.time()

            # 生成回應
            response = model_instance.generate_content(prompt)

            process_time = time.time() - start_time

            # 解析回應
            content = response.text if response.text else ""

            # 計算 token 使用量 (估算)
            input_tokens = self.num_tokens_from_string(prompt + (system_prompt or ""))
            output_tokens = self.num_tokens_from_string(content)

            return {
                "content": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "process_time": process_time
            }

        except Exception as e:
            raise Exception(f"Gemini API 調用失敗: {str(e)}")

    def check_connection(self):
        """檢查 Gemini API 連接"""
        if not self.api_key:
            return False, "未設置 GEMINI_API_KEY"

        try:
            # 使用簡單提示測試連接
            model_instance = genai.GenerativeModel(model_name=self.default_model)
            response = model_instance.generate_content("Hello")
            return True, "連接正常"
        except Exception as e:
            return False, f"連接錯誤: {str(e)}"

class GeminiVertexInvoker(LLMInvoker):
    """Google Gemini 調用類 (Vertex AI 模式 - 企業用戶)"""

    def __init__(self, project_id=None, location="us-central1", model=GEMINI_FLASH_MODEL):
        super().__init__()
        self.name = "Gemini (Vertex AI)"
        self.project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.default_model = model

        # 初始化 Vertex AI
        if self.project_id:
            aiplatform.init(project=self.project_id, location=self.location)

    def invoke(self, prompt, system_prompt="", temperature=0.7, top_p=0.9, top_k=40, max_tokens=max_token_length, model=None):
        """調用 Vertex AI Gemini API"""
        if not self.project_id:
            raise ValueError("未設置 GOOGLE_CLOUD_PROJECT")

        model_name = model or self.default_model

        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel, GenerationConfig

            # 初始化 Vertex AI
            vertexai.init(project=self.project_id, location=self.location)

            # 配置生成參數
            generation_config = GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                max_output_tokens=min(max_tokens, 8192),
            )

            # 創建模型實例
            model_instance = GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
                system_instruction=system_prompt if system_prompt else None
            )

            start_time = time.time()

            # 生成回應
            response = model_instance.generate_content(prompt)

            process_time = time.time() - start_time

            # 解析回應
            content = response.text if response.text else ""

            # 計算 token 使用量 (估算)
            input_tokens = self.num_tokens_from_string(prompt + (system_prompt or ""))
            output_tokens = self.num_tokens_from_string(content)

            return {
                "content": content,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                },
                "process_time": process_time
            }

        except Exception as e:
            raise Exception(f"Vertex AI Gemini 調用失敗: {str(e)}")

    def check_connection(self):
        """檢查 Vertex AI 連接"""
        if not self.project_id:
            return False, "未設置 GOOGLE_CLOUD_PROJECT"

        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel

            # 初始化 Vertex AI
            vertexai.init(project=self.project_id, location=self.location)

            # 使用簡單提示測試連接
            model_instance = GenerativeModel(model_name=self.default_model)
            response = model_instance.generate_content("Hello")
            return True, "連接正常"
        except Exception as e:
            return False, f"連接錯誤: {str(e)}"

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
        elif llm_type.lower() == "gemini":
            return GeminiInvoker(**kwargs)
        elif llm_type.lower() == "gemini-vertex":
            return GeminiVertexInvoker(**kwargs)
        else:
            raise ValueError(f"不支持的 LLM 類型: {llm_type}")

    @staticmethod
    def get_available_models():
        """獲取所有可用的模型選項 (預設: Gemini API Key)"""
        return {
            "Gemini (API Key)": {
                "type": "gemini",
                "models": [
                    GEMINI_FLASH_MODEL,
                    GEMINI_PRO_MODEL
                ]
            },
            "Claude (AWS Bedrock)": {
                "type": "claude",
                "models": [
                    "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                    "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                    "us.anthropic.claude-3-haiku-20240307-v1:0"
                ]
            },
            "Gemini (Vertex AI)": {
                "type": "gemini-vertex",
                "models": [
                    GEMINI_PRO_MODEL,
                    GEMINI_FLASH_MODEL
                ]
            }
        }

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
