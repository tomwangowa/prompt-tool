#!/usr/bin/env python3
"""
對話流程控制模組
管理對話式 UI 的狀態機和流程邏輯
"""

from typing import Dict, Any, Optional
import logging

from conversation_types import (
    ConversationSession,
    Message,
    MessageRole,
    MessageType,
    ConversationState
)
from prompt_eval import PromptEvaluator
from llm_invoker import ParameterPresets

logger = logging.getLogger(__name__)


class ConversationFlow:
    """對話流程控制器"""

    # 錯誤訊息翻譯
    ERROR_MESSAGES = {
        "zh_TW": {
            "analysis_error": "抱歉，分析過程發生錯誤：{error}",
            "questions_error": "抱歉，生成改進問題時發生錯誤：{error}",
            "modification_error": "抱歉，處理您的修改請求時發生錯誤：{error}",
            "conversation_error": "抱歉，處理您的問題時發生錯誤：{error}"
        },
        "en": {
            "analysis_error": "Sorry, an error occurred during analysis: {error}",
            "questions_error": "Sorry, an error occurred while generating questions: {error}",
            "modification_error": "Sorry, an error occurred while processing your modification request: {error}",
            "conversation_error": "Sorry, an error occurred while processing your question: {error}"
        },
        "ja": {
            "analysis_error": "申し訳ございません。分析中にエラーが発生しました：{error}",
            "questions_error": "申し訳ございません。質問の生成中にエラーが発生しました：{error}",
            "modification_error": "申し訳ございません。修正リクエストの処理中にエラーが発生しました：{error}",
            "conversation_error": "申し訳ございません。ご質問の処理中にエラーが発生しました：{error}"
        }
    }

    # LLM Prompt 模板翻譯
    PROMPT_TEMPLATES = {
        "zh_TW": {
            "modification": """基於以下當前提示進行調整：

<current_prompt>
{current_prompt}
</current_prompt>

<user_request>
{user_input}
</user_request>

請根據用戶要求調整提示，保持其他部分不變。只輸出調整後的完整提示。""",
            "conversation": """對話上下文：
{context}

當前優化的提示：
<current_prompt>
{current_prompt}
</current_prompt>

用戶問題：
<user_question>
{user_input}
</user_question>

請根據對話上下文回答用戶的問題。"""
        },
        "en": {
            "modification": """Adjust based on the current prompt:

<current_prompt>
{current_prompt}
</current_prompt>

<user_request>
{user_input}
</user_request>

Please adjust the prompt according to the user's request, keeping other parts unchanged. Output only the complete adjusted prompt.""",
            "conversation": """Conversation context:
{context}

Current optimized prompt:
<current_prompt>
{current_prompt}
</current_prompt>

User question:
<user_question>
{user_input}
</user_question>

Please answer the user's question based on the conversation context."""
        },
        "ja": {
            "modification": """以下の現在のプロンプトに基づいて調整してください：

<current_prompt>
{current_prompt}
</current_prompt>

<user_request>
{user_input}
</user_request>

ユーザーの要求に従ってプロンプトを調整し、他の部分は変更しないでください。調整後の完全なプロンプトのみを出力してください。""",
            "conversation": """会話の文脈：
{context}

現在の最適化されたプロンプト：
<current_prompt>
{current_prompt}
</current_prompt>

ユーザーの質問：
<user_question>
{user_input}
</user_question>

会話の文脈に基づいてユーザーの質問に答えてください。"""
        }
    }

    def __init__(self, session: ConversationSession, llm_instance: Any, language: str = "zh_TW"):
        """
        初始化對話流程控制器

        Args:
            session: 對話會話
            llm_instance: LLM 實例
            language: 語言代碼
        """
        self.session = session
        self.llm = llm_instance
        self.language = language
        self.evaluator = PromptEvaluator(llm_instance=llm_instance)
        self.state = ConversationState.IDLE

    def _get_error_message(self, key: str, error: str) -> str:
        """獲取本地化的錯誤訊息"""
        messages = self.ERROR_MESSAGES.get(self.language, self.ERROR_MESSAGES["zh_TW"])
        return messages.get(key, "Error: {error}").format(error=error)

    def _sanitize_input(self, text: str) -> str:
        """防止 Prompt Injection（轉義 XML 標籤）"""
        if not text:
            return ""
        return text.replace("<", "&lt;").replace(">", "&gt;")

    def handle_initial_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        處理初始 prompt 輸入

        Args:
            prompt: 用戶輸入的提示

        Returns:
            包含分析和問題的結果字典
        """
        # 記錄用戶訊息
        user_msg = self.session.add_message(
            role=MessageRole.USER,
            msg_type=MessageType.TEXT,
            content=prompt
        )

        # 更新會話的 prompt
        self.session.original_prompt = prompt
        self.session.current_prompt = prompt

        # 自動觸發分析
        self.state = ConversationState.ANALYZING
        analysis_result = self.analyze_prompt(prompt)

        # 檢查分析是否失敗
        if "error" in analysis_result:
            self.state = ConversationState.IDLE
            return {
                "user_message": user_msg,
                "analysis": analysis_result,
                "questions": None,
                "state": self.state
            }

        # 自動生成改進問題
        self.state = ConversationState.AWAITING_QUESTIONS
        questions_result = self.generate_questions()

        # 檢查問題生成是否失敗
        if "error" in questions_result:
            return {
                "user_message": user_msg,
                "analysis": analysis_result,
                "questions": questions_result,
                "state": self.state
            }

        return {
            "user_message": user_msg,
            "analysis": analysis_result,
            "questions": questions_result,
            "state": self.state
        }

    def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        執行 prompt 分析

        Args:
            prompt: 要分析的提示

        Returns:
            分析結果字典
        """
        try:
            # 調用 PromptEvaluator 進行分析
            analysis = self.evaluator.analyze_prompt(prompt, self.language)

            # 格式化分析內容
            analysis_content = self._format_analysis_content(analysis)

            # 添加分析結果訊息
            analysis_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.ANALYSIS,
                content=analysis_content,
                analysis_data=analysis
            )

            # 保存分析結果
            self.session.last_analysis = analysis

            return {
                "message": analysis_msg,
                "analysis": analysis
            }

        except Exception as e:
            # 錯誤處理：返回友好的錯誤訊息
            logger.error("Error analyzing prompt", exc_info=True)
            error_msg = self._get_error_message("analysis_error", str(e))
            error_message = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=error_msg
            )
            return {
                "message": error_message,
                "error": str(e)
            }

    def generate_questions(self) -> Dict[str, Any]:
        """
        生成改進問題

        Returns:
            問題結果字典
        """
        if not self.session.last_analysis:
            raise ValueError("必須先執行分析才能生成問題")

        try:
            # 調用 PromptEvaluator 生成問題
            questions = self.evaluator.generate_questions(
                self.session.last_analysis,
                self.language
            )

            # 格式化問題內容
            questions_content = self._format_questions_content(questions)

            # 添加問題訊息
            questions_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.QUESTIONS,
                content=questions_content,
                questions_data=questions
            )

            # 保存待回答的問題
            self.session.pending_questions = questions

            return {
                "message": questions_msg,
                "questions": questions
            }

        except Exception as e:
            # 錯誤處理：返回友好的錯誤訊息
            logger.error("Error generating questions", exc_info=True)
            error_msg = self._get_error_message("questions_error", str(e))
            error_message = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=error_msg
            )
            return {
                "message": error_message,
                "error": str(e)
            }

    def handle_questions_response(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理用戶對改進問題的回答

        Args:
            responses: 用戶回答字典

        Returns:
            優化結果字典
        """
        # 記錄用戶回答
        responses_content = self._format_responses_content(responses)
        user_msg = self.session.add_message(
            role=MessageRole.USER,
            msg_type=MessageType.TEXT,
            content=responses_content,
            metadata={"responses": responses}
        )

        # 保存回答
        self.session.question_answers = responses

        # 執行優化
        self.state = ConversationState.OPTIMIZING
        optimization_result = self.optimize_prompt(responses)

        self.state = ConversationState.COMPLETED

        return {
            "user_message": user_msg,
            "optimization": optimization_result,
            "state": self.state
        }

    def optimize_prompt(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        執行 prompt 優化

        Args:
            responses: 用戶回答字典

        Returns:
            優化結果字典
        """
        if not self.session.last_analysis:
            raise ValueError("必須先執行分析才能優化")

        try:
            # 調用 PromptEvaluator 進行優化
            result = self.evaluator.optimize_prompt(
                self.session.current_prompt,
                responses,
                self.session.last_analysis,
                self.language
            )

            # 添加優化結果訊息
            optimization_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.OPTIMIZATION,
                content=result["enhanced_prompt"],
                optimization_data=result
            )

            # 更新會話狀態
            self.session.last_optimization = result
            self.session.current_prompt = result["enhanced_prompt"]
            self.session.iteration_count += 1

            return {
                "message": optimization_msg,
                "result": result
            }

        except Exception as e:
            # 錯誤處理：返回友好的錯誤訊息（使用 conversation_error 作為通用錯誤）
            logger.error("Error optimizing prompt", exc_info=True)
            error_msg = self._get_error_message("conversation_error", str(e))
            error_message = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=error_msg
            )
            return {
                "message": error_message,
                "error": str(e)
            }

    def handle_followup_message(self, user_input: str) -> Dict[str, Any]:
        """
        處理優化完成後的持續對話

        Args:
            user_input: 用戶輸入

        Returns:
            處理結果字典
        """
        # 記錄用戶訊息
        user_msg = self.session.add_message(
            role=MessageRole.USER,
            msg_type=MessageType.TEXT,
            content=user_input
        )

        # 根據用戶意圖決定下一步
        intent = self._classify_user_intent(user_input)

        if intent == "iterate":
            # 用戶想要再次優化
            return self.handle_initial_prompt(self.session.current_prompt)
        elif intent == "modify":
            # 用戶想要調整某個方面
            return self._handle_modification_request(user_input)
        else:
            # 一般性對話
            return self._handle_general_conversation(user_input)

    def _classify_user_intent(self, user_input: str) -> str:
        """
        分類用戶意圖（使用關鍵字匹配）

        Args:
            user_input: 用戶輸入

        Returns:
            意圖類型：iterate, modify, general
        """
        input_lower = user_input.lower()

        # 迭代關鍵字（優先檢查，較為明確）
        iterate_keywords = ["再次優化", "繼續優化", "optimize again", "iterate", "もう一度最適化"]
        if any(kw in input_lower for kw in iterate_keywords):
            return "iterate"

        # 修改關鍵字
        modify_keywords = ["修改", "調整", "改一下", "modify", "adjust", "change", "変更"]
        if any(kw in input_lower for kw in modify_keywords):
            return "modify"

        return "general"

    def _handle_modification_request(self, user_input: str) -> Dict[str, Any]:
        """
        處理修改請求

        Args:
            user_input: 用戶輸入

        Returns:
            處理結果字典
        """
        # 使用本地化的提示模板，並防止 Prompt Injection
        templates = self.PROMPT_TEMPLATES.get(self.language, self.PROMPT_TEMPLATES["zh_TW"])
        modification_prompt = templates["modification"].format(
            current_prompt=self._sanitize_input(self.session.current_prompt),
            user_input=self._sanitize_input(user_input)
        )

        try:
            # 使用精確參數預設（適合修改任務）
            precise_params = ParameterPresets.get_preset("精確")
            # 移除 description（invoke 不接受此參數）
            llm_params = {k: v for k, v in precise_params.items() if k != 'description'}
            result = self.llm.invoke(
                prompt=modification_prompt,
                **llm_params
            )

            modified_prompt = result["content"].strip()

            # 添加 AI 回應
            response_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=modified_prompt
            )

            # 更新當前提示
            self.session.current_prompt = modified_prompt

            return {
                "message": response_msg,
                "modified_prompt": modified_prompt
            }

        except Exception as e:
            # 錯誤處理：返回友好的錯誤訊息
            logger.error("Error handling modification request", exc_info=True)
            error_msg = self._get_error_message("modification_error", str(e))
            response_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=error_msg
            )
            return {
                "message": response_msg,
                "error": str(e)
            }

    def _handle_general_conversation(self, user_input: str) -> Dict[str, Any]:
        """
        處理一般性對話

        Args:
            user_input: 用戶輸入

        Returns:
            處理結果字典
        """
        # 構建對話上下文
        context = self._build_conversation_context()

        # 使用本地化的提示模板，並防止 Prompt Injection
        templates = self.PROMPT_TEMPLATES.get(self.language, self.PROMPT_TEMPLATES["zh_TW"])
        conversation_prompt = templates["conversation"].format(
            context=context,
            current_prompt=self._sanitize_input(self.session.current_prompt),
            user_input=self._sanitize_input(user_input)
        )

        try:
            # 使用平衡參數預設（適合一般對話）
            balanced_params = ParameterPresets.get_preset("平衡")
            # 移除 description（invoke 不接受此參數）
            llm_params = {k: v for k, v in balanced_params.items() if k != 'description'}
            result = self.llm.invoke(
                prompt=conversation_prompt,
                **llm_params
            )

            response_content = result["content"].strip()

            # 添加 AI 回應
            response_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=response_content
            )

            return {
                "message": response_msg,
                "response": response_content
            }

        except Exception as e:
            # 錯誤處理：返回友好的錯誤訊息
            logger.error("Error handling general conversation", exc_info=True)
            error_msg = self._get_error_message("conversation_error", str(e))
            response_msg = self.session.add_message(
                role=MessageRole.ASSISTANT,
                msg_type=MessageType.TEXT,
                content=error_msg
            )
            return {
                "message": response_msg,
                "error": str(e)
            }

    def _build_conversation_context(self) -> str:
        """
        構建對話上下文（最近的訊息）

        Returns:
            格式化的對話上下文
        """
        # 獲取最近 5 條訊息
        recent_messages = self.session.messages[-5:] if len(self.session.messages) > 5 else self.session.messages

        context_lines = []
        for msg in recent_messages:
            role_label = "用戶" if msg.role == MessageRole.USER else "AI 助手"
            # 不截斷內容 - Prompt Engineering 工具需要完整上下文
            # Token 管理由 LLM invoke 層處理
            context_lines.append(f"{role_label}: {msg.content}")

        return "\n".join(context_lines)

    def _format_analysis_content(self, analysis: Dict[str, Any]) -> str:
        """
        格式化分析結果內容

        Args:
            analysis: 分析結果字典

        Returns:
            格式化的文字內容
        """
        content_parts = [
            "📊 提示分析結果",
            "",
            f"完整性：{analysis.get('completeness_score', 0)}/10",
            f"清晰度：{analysis.get('clarity_score', 0)}/10",
            f"結構性：{analysis.get('structure_score', 0)}/10",
            f"具體性：{analysis.get('specificity_score', 0)}/10",
            "",
            f"提示類型：{analysis.get('prompt_type', '未知')}",
            f"複雜度：{analysis.get('complexity_level', '未知')}"
        ]

        return "\n".join(content_parts)

    def _format_questions_content(self, questions: list) -> str:
        """
        格式化問題內容

        Args:
            questions: 問題列表

        Returns:
            格式化的文字內容
        """
        if not questions:
            return "沒有需要回答的問題。"

        content_parts = ["💡 讓我們一起改進您的提示", ""]
        for i, q in enumerate(questions, 1):
            content_parts.append(f"{i}. {q.get('question', '')}")

        return "\n".join(content_parts)

    def _format_responses_content(self, responses: Dict[str, Any]) -> str:
        """
        格式化用戶回答內容

        Args:
            responses: 回答字典

        Returns:
            格式化的文字內容
        """
        content_parts = ["我的回答：", ""]
        for key, value in responses.items():
            content_parts.append(f"- {key}: {value}")

        return "\n".join(content_parts)

    def reset_conversation(self):
        """重置對話狀態"""
        self.session.clear_messages()
        self.session.current_prompt = ""
        self.session.original_prompt = ""
        self.session.last_analysis = None
        self.session.last_optimization = None
        self.session.pending_questions = None
        self.session.question_answers = {}
        self.session.iteration_count = 0
        self.state = ConversationState.IDLE

    def can_optimize(self) -> bool:
        """檢查是否可以執行優化"""
        return (
            self.session.last_analysis is not None and
            self.session.question_answers is not None and
            len(self.session.question_answers) > 0
        )

    def get_state_summary(self) -> Dict[str, Any]:
        """獲取當前狀態摘要"""
        return {
            "state": self.state.value,
            "message_count": len(self.session.messages),
            "iteration_count": self.session.iteration_count,
            "has_analysis": self.session.last_analysis is not None,
            "has_optimization": self.session.last_optimization is not None,
            "pending_questions_count": len(self.session.pending_questions) if self.session.pending_questions else 0
        }
