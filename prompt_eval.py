import json
from llm_invoker import LLMFactory

class PromptEvaluator:
    """提示評估類，用於分析和優化提示"""
    
    def __init__(self, llm_type="claude", **llm_kwargs):
        """初始化評估器"""
        self.llm = LLMFactory.create_llm(llm_type, **llm_kwargs)
        self.translations = {
            "zh_TW": {
                "system_analyze": "你是一個專業的提示工程專家。請分析以下提示並識別可以改進的地方。",
                "user_analyze": "請分析以下提示並識別可以改進的區域。返回JSON格式，包含完整性評分（1-10），清晰度評分（1-10），缺失元素列表，以及改進建議列表。\n\n提示：\n{prompt}",
                "system_optimize": "你是一個專業的提示工程專家。請優化以下提示使其更加清晰和有效。",
                "user_optimize": "請優化以下提示使其更加清晰、具體和有效。保持原始意圖但添加必要的結構和指導。\n\n原始提示：\n{prompt}",
                "role_added": "添加了角色定義：",
                "format_added": "添加了輸出格式指示：",
                "reasoning_added": "添加了思考過程指示",
                "final_improvement": "利用AI專家知識進一步優化了提示的結構和清晰度"
            },
            "en": {
                "system_analyze": "You are a professional prompt engineering expert. Please analyze the following prompt and identify areas for improvement.",
                "user_analyze": "Please analyze the following prompt and identify areas for improvement. Return in JSON format with completeness score (1-10), clarity score (1-10), missing elements list, and improvement suggestions list.\n\nPrompt:\n{prompt}",
                "system_optimize": "You are a professional prompt engineering expert. Please optimize the following prompt to make it clearer and more effective.",
                "user_optimize": "Please optimize the following prompt to make it clearer, more specific, and more effective. Maintain the original intent but add necessary structure and guidance.\n\nOriginal prompt:\n{prompt}",
                "role_added": "Added role definition: ",
                "format_added": "Added output format instruction: ",
                "reasoning_added": "Added reasoning process instruction",
                "final_improvement": "Further optimized the prompt structure and clarity using AI expert knowledge"
            },
            "ja": {
                "system_analyze": "あなたはプロのプロンプトエンジニアリングの専門家です。以下のプロンプトを分析し、改善できる領域を特定してください。",
                "user_analyze": "以下のプロンプトを分析し、改善できる領域を特定してください。完全性スコア（1〜10）、明確性スコア（1〜10）、欠けている要素のリスト、改善提案のリストを含むJSON形式で返してください。\n\nプロンプト：\n{prompt}",
                "system_optimize": "あなたはプロのプロンプトエンジニアリングの専門家です。以下のプロンプトをより明確で効果的になるように最適化してください。",
                "user_optimize": "以下のプロンプトをより明確、具体的、効果的になるように最適化してください。元の意図を維持しながら、必要な構造とガイダンスを追加してください。\n\n元のプロンプト：\n{prompt}",
                "role_added": "役割定義を追加しました：",
                "format_added": "出力形式の指示を追加しました：",
                "reasoning_added": "推論プロセスの指示を追加しました",
                "final_improvement": "AI専門家の知識を活用してプロンプトの構造と明確さをさらに最適化しました"
            }
        }
    
    def t(self, key, language="zh_TW"):
        """獲取翻譯"""
        return self.translations.get(language, self.translations["zh_TW"]).get(key, key)
    
    def analyze_prompt(self, prompt, language="zh_TW"):
        """分析提示並識別可改進的區域"""
        system_instruction = self.t("system_analyze", language)
        user_prompt = self.t("user_analyze", language).format(prompt=prompt)
        
        result = self.llm.invoke(
            prompt=user_prompt,
            system_prompt=system_instruction,
            temperature=0.1,
            top_p=0.9,
            top_k=40,
            max_tokens=1000
        )
        
        try:
            # 嘗試解析 JSON 格式的回复
            analysis = json.loads(result["content"])
            return analysis
        except:
            # 如果無法解析為 JSON，返回簡化的分析
            return {
                "completeness_score": 5,
                "clarity_score": 5,
                "missing_elements": [],
                "improvement_areas": []
            }
    
    def generate_questions(self, analysis, language="zh_TW"):
        """根據分析結果生成問題"""
        questions = []
        
        # 基於分析結果生成問題
        if analysis["completeness_score"] < 7:
            if language == "zh_TW":
                questions.append({
                    "question": "您希望AI扮演什麼角色？(例如：專家、教師、顧問等)",
                    "type": "role"
                })
            elif language == "en":
                questions.append({
                    "question": "What role should the AI play? (e.g., expert, teacher, consultant)",
                    "type": "role"
                })
            else:  # 日文
                questions.append({
                    "question": "AIにどのような役割を担ってほしいですか？（例：専門家、教師、コンサルタントなど）",
                    "type": "role"
                })
        
        # 檢查是否缺少輸出格式指定
        if "missing_elements" in analysis and analysis["missing_elements"]:
            for element in analysis["missing_elements"]:
                if isinstance(element, str) and "format" in element.lower():
                    if language == "zh_TW":
                        questions.append({
                            "question": "您希望輸出內容採用什麼格式？(例如：JSON、列表、段落等)",
                            "type": "format"
                        })
                    elif language == "en":
                        questions.append({
                            "question": "What output format do you prefer? (e.g., JSON, list, paragraphs)",
                            "type": "format"
                        })
                    else:  # 日文
                        questions.append({
                            "question": "どの出力形式を希望しますか？（例：JSON、リスト、段落など）",
                            "type": "format"
                        })
                    break
        
        # 添加關於思考鏈的問題
        if language == "zh_TW":
            questions.append({
                "question": "您是否需要模型展示其思考過程？",
                "type": "reasoning"
            })
        elif language == "en":
            questions.append({
                "question": "Do you want the model to show its reasoning process?",
                "type": "reasoning"
            })
        else:  # 日文
            questions.append({
                "question": "モデルに推論プロセスを表示させますか？",
                "type": "reasoning"
            })
        
        return questions
    
    def optimize_prompt(self, original_prompt, user_responses, analysis, language="zh_TW"):
        """基於用戶回答和分析生成優化提示"""
        enhanced_prompt = original_prompt
        improvements = []
        
        # 添加角色定義
        if "role" in user_responses and user_responses["role"]:
            if language == "zh_TW":
                role_text = f"你是一個{user_responses['role']}。"
                improvements.append(f"{self.t('role_added', language)}{role_text}")
            elif language == "en":
                role_text = f"You are a {user_responses['role']}."
                improvements.append(f"{self.t('role_added', language)}{role_text}")
            else:  # 日文
                role_text = f"あなたは{user_responses['role']}です。"
                improvements.append(f"{self.t('role_added', language)}{role_text}")
            
            enhanced_prompt = role_text + "\n\n" + enhanced_prompt
        
        # 添加輸出格式
        if "format" in user_responses and user_responses["format"]:
            if language == "zh_TW":
                format_text = f"\n\n請以{user_responses['format']}格式提供回答。"
                improvements.append(f"{self.t('format_added', language)}{format_text}")
            elif language == "en":
                format_text = f"\n\nPlease provide your response in {user_responses['format']} format."
                improvements.append(f"{self.t('format_added', language)}{format_text}")
            else:  # 日文
                format_text = f"\n\n回答を{user_responses['format']}形式で提供してください。"
                improvements.append(f"{self.t('format_added', language)}{format_text}")
            
            enhanced_prompt += format_text
        
        # 添加思考過程指示
        if "reasoning" in user_responses and user_responses["reasoning"]:
            if language == "zh_TW":
                reasoning_text = "\n\n請一步步思考，顯示你的推理過程。"
                improvements.append(self.t("reasoning_added", language))
            elif language == "en":
                reasoning_text = "\n\nPlease think step by step and show your reasoning process."
                improvements.append(self.t("reasoning_added", language))
            else:  # 日文
                reasoning_text = "\n\nステップバイステップで考え、推論プロセスを示してください。"
                improvements.append(self.t("reasoning_added", language))
            
            enhanced_prompt += reasoning_text
        
        # 使用 LLM 進一步優化提示
        system_instruction = self.t("system_optimize", language)
        user_prompt = self.t("user_optimize", language).format(prompt=enhanced_prompt)
        
        result = self.llm.invoke(
            prompt=user_prompt,
            system_prompt=system_instruction,
            temperature=0.1,
            top_p=0.9,
            top_k=40,
            max_tokens=2000
        )
        
        # 添加一個最終改進說明
        improvements.append(self.t("final_improvement", language))
        
        return {
            "enhanced_prompt": result["content"],
            "improvements": improvements
        }