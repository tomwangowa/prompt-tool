#!/usr/bin/env python3
"""
對話式 UI 組件模組
實作所有對話式介面的 UI 渲染函數
"""

import streamlit as st
import time
import logging
from typing import Dict, Any, List, Optional, Callable

from conversation_types import Message, MessageRole, MessageType, ConversationSession, create_new_session
from conversation_flow import ConversationFlow

logger = logging.getLogger(__name__)


def add_chat_css():
    """添加對話式 UI 的自訂 CSS 樣式"""
    st.markdown("""
    <style>
    /* 訊息卡片樣式 */
    .stChatMessage {
        border-radius: 12px;
        margin-bottom: 12px;
        padding: 12px 16px;
    }

    /* 分析結果卡片樣式 */
    .analysis-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }

    /* 優化結果卡片樣式 */
    .optimization-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
    }

    /* Metric 卡片樣式 - 保持預設顏色以相容 light/dark 主題 */
    div[data-testid="stMetric"] {
        background: rgba(102, 126, 234, 0.08);
        border-radius: 8px;
        padding: 12px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
    }

    /* 對話容器調整 */
    .main .block-container {
        padding-bottom: 120px;
    }

    /* 固定底部輸入框樣式 */
    div[data-testid="stChatInput"] {
        position: sticky;
        bottom: 0;
        background: var(--secondary-background-color);
        padding: 16px 0;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)


def render_conversation_ui(t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    渲染對話式 UI 主介面（簡化版：單次優化流程）

    Args:
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """
    session = st.session_state.current_session

    # 添加 CSS 樣式
    add_chat_css()

    # 顯示對話歷史
    for msg in session.messages:
        render_message(msg, t_func)

    # 根據狀態渲染輸入區域（簡化：無追加對話）
    render_input_area_simple(session, t_func, create_llm_func)



def render_message(msg: Message, t_func: Callable[[str], str]):
    """
    渲染單個訊息

    Args:
        msg: 訊息物件
        t_func: 翻譯函數
    """
    if msg.role == MessageRole.USER:
        # 用戶訊息
        with st.chat_message("user", avatar="🧑"):
            st.write(msg.content)

    elif msg.role == MessageRole.ASSISTANT:
        # AI 訊息 - 根據類型渲染不同組件
        if msg.type == MessageType.ANALYSIS:
            render_analysis_card(msg, t_func)
        elif msg.type == MessageType.QUESTIONS:
            render_questions_card(msg, t_func)
        elif msg.type == MessageType.OPTIMIZATION:
            render_optimization_card(msg, t_func)
        else:
            # 一般文字訊息
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg.content)


def render_analysis_card(msg: Message, t_func: Callable[[str], str]):
    """
    渲染分析結果卡片

    Args:
        msg: 分析訊息物件
        t_func: 翻譯函數
    """
    with st.chat_message("assistant", avatar="📊"):
        st.markdown("#### " + t_func("analysis_result"))

        if msg.analysis_data:
            analysis = msg.analysis_data

            # 評分展示（使用 4 欄）
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    t_func("completeness_label"),
                    f"{analysis.get('completeness_score', 0)}/10"
                )
            with col2:
                st.metric(
                    t_func("clarity_label"),
                    f"{analysis.get('clarity_score', 0)}/10"
                )
            with col3:
                st.metric(
                    t_func("structure_label"),
                    f"{analysis.get('structure_score', 0)}/10"
                )
            with col4:
                st.metric(
                    t_func("specificity_label"),
                    f"{analysis.get('specificity_score', 0)}/10"
                )

            # 提示類型和複雜度
            st.info(
                f"**{t_func('prompt_type')}:** {analysis.get('prompt_type', 'unknown')} | "
                f"**{t_func('complexity_level')}:** {analysis.get('complexity_level', 'unknown')}"
            )

            # 詳細分析（可展開）
            with st.expander(t_func("view_details"), expanded=False):
                has_content = False

                if analysis.get('missing_elements'):
                    st.markdown(f"**{t_func('missing_elements')}:**")
                    for elem in analysis['missing_elements']:
                        st.markdown(f"- {elem}")
                    has_content = True

                if analysis.get('improvement_suggestions'):
                    st.markdown(f"**{t_func('improvement_suggestions')}:**")
                    for sugg in analysis['improvement_suggestions']:
                        st.markdown(f"- {sugg}")
                    has_content = True

                # 如果沒有具體建議且 analysis 有內容，顯示完整分析數據
                if not has_content and analysis:
                    st.json(analysis)


def render_questions_card(msg: Message, t_func: Callable[[str], str]):
    """
    渲染改進問題卡片

    Args:
        msg: 問題訊息物件
        t_func: 翻譯函數
    """
    with st.chat_message("assistant", avatar="💡"):
        st.markdown("#### " + t_func("improvement_header"))

        if msg.questions_data:
            questions = msg.questions_data

            # 檢查此訊息是否為最新的待回答問題
            session = st.session_state.current_session
            is_latest_questions = (
                session.pending_questions is not None and
                len(session.messages) > 0 and
                session.messages[-1].id == msg.id or
                (len(session.messages) > 1 and session.messages[-2].id == msg.id)
            )

            # 使用表單收集所有問題的回答
            with st.form(key=f"questions_form_{msg.id}"):
                responses = {}
                seen_types = set()  # 追蹤已見過的 type，檢測衝突

                for i, q in enumerate(questions):
                    question_text = q.get('question', '')
                    question_type = q.get('type', 'text')

                    # 使用 question_type 作為 key（與 PromptEvaluator.optimize_prompt 的期望一致）
                    # 設計假設：YAML 配置確保每個問題的 type 唯一（role, format, detail, scope, reasoning）
                    response_key = question_type

                    # 檢測 key 衝突（防禦性編程）
                    if response_key in seen_types:
                        # 如果檢測到重複，使用索引後綴
                        response_key = f"{question_type}_{i}"
                    seen_types.add(question_type)

                    # 根據問題類型渲染不同的輸入元件
                    if question_type == "reasoning" or q.get('input_type') == 'checkbox':
                        # Checkbox 類型
                        responses[response_key] = st.checkbox(
                            question_text,
                            key=f"q_{msg.id}_{i}",
                            disabled=not is_latest_questions
                        )

                    elif q.get('input_type') == 'selectbox' and q.get('options'):
                        # 下拉選單類型
                        options = q['options']
                        labels = [opt['label'] for opt in options]
                        keys = [opt['key'] for opt in options]

                        # 獲取預設值索引（從 YAML 配置的 default 欄位）
                        default_key = q.get('default', None)
                        default_index = 0  # 預設為第一個選項
                        if default_key and default_key in keys:
                            default_index = keys.index(default_key)

                        selected = st.selectbox(
                            question_text,
                            options=labels,
                            index=default_index,
                            key=f"q_{msg.id}_{i}",
                            disabled=not is_latest_questions
                        )

                        # 找到對應的 key
                        selected_index = labels.index(selected) if selected in labels else 0
                        responses[response_key] = keys[selected_index]

                    else:
                        # 文字輸入類型
                        responses[response_key] = st.text_input(
                            question_text,
                            key=f"q_{msg.id}_{i}",
                            disabled=not is_latest_questions
                        )

                # 檢查是否正在處理中
                is_processing = st.session_state.get('is_processing', False)

                # 提交按鈕（只有最新的問題可提交，且未在處理中）
                submitted = st.form_submit_button(
                    t_func("processing") if is_processing else t_func("generate_button"),
                    use_container_width=True,
                    disabled=not is_latest_questions or is_processing
                )

                if submitted and is_latest_questions and not is_processing:
                    # 保存回答到 session state
                    st.session_state.pending_responses = responses
                    st.session_state.trigger_optimization = True
                    st.rerun()


def render_optimization_card(msg: Message, t_func: Callable[[str], str]):
    """
    渲染優化結果卡片

    Args:
        msg: 優化訊息物件
        t_func: 翻譯函數
    """
    with st.chat_message("assistant", avatar="✨"):
        st.markdown("#### " + t_func("result_header"))

        if msg.optimization_data:
            result = msg.optimization_data

            # 獲取原始和優化後的提示
            original_prompt = st.session_state.current_session.original_prompt
            enhanced_prompt = result.get("enhanced_prompt", "")

            # 對比展示（左右兩欄）
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**📄 {t_func('original_prompt')}**")
                st.text_area(
                    label="original",
                    value=original_prompt,
                    height=250,
                    disabled=True,
                    key=f"orig_{msg.id}",
                    label_visibility="collapsed"
                )

            with col2:
                st.markdown(f"**✨ {t_func('enhanced_prompt')}**")
                st.text_area(
                    label="enhanced",
                    value=enhanced_prompt,
                    height=250,
                    key=f"enh_{msg.id}",
                    label_visibility="collapsed"
                )

            # 改進說明
            if result.get('improvements'):
                with st.expander(t_func("improvement_description"), expanded=True):
                    for improvement in result['improvements']:
                        st.markdown(f"- {improvement}")

            # 提示：可直接選擇上方文字複製
            st.info("💡 " + t_func("select_to_copy"))

            # 操作按鈕佈局
            st.markdown("---")

            # 保存提示按鈕
            if st.button(t_func("save_prompt"), key=f"save_{msg.id}", type="primary", use_container_width=True):
                st.session_state.active_save_msg_id = msg.id
                st.rerun()

            # 保存表單（只顯示當前選中的）
            if st.session_state.get('active_save_msg_id') == msg.id:
                with st.expander(t_func("save_prompt"), expanded=True):
                    render_save_prompt_form(original_prompt, enhanced_prompt, msg.analysis_data, t_func, msg.id)



def render_save_prompt_form(original_prompt: str, optimized_prompt: str, analysis_scores: Optional[Dict], t_func: Callable[[str], str], msg_id: str):
    """
    渲染保存提示表單

    Args:
        original_prompt: 原始提示
        optimized_prompt: 優化後的提示
        analysis_scores: 分析評分
        t_func: 翻譯函數
        msg_id: 訊息 ID（用於唯一性，必填）
    """
    save_name = st.text_input(t_func("save_name"), key=f"save_name_{msg_id}")
    save_tags = st.text_input(t_func("save_tags"), key=f"save_tags_{msg_id}")

    col_save, col_cancel = st.columns(2)

    with col_save:
        save_clicked = st.button(t_func("confirm"), key=f"confirm_save_{msg_id}", type="primary", use_container_width=True)

    with col_cancel:
        cancel_clicked = st.button(t_func("cancel"), key=f"cancel_save_{msg_id}", use_container_width=True)

    if cancel_clicked:
        # 關閉保存表單
        st.session_state.active_save_msg_id = None
        st.rerun()

    if save_clicked:
        if save_name:
            try:
                # 處理標籤
                tags = [tag.strip() for tag in save_tags.split(",") if tag.strip()] if save_tags else []

                # 保存到資料庫
                prompt_id = st.session_state.prompt_db.save_prompt(
                    name=save_name,
                    original_prompt=original_prompt,
                    optimized_prompt=optimized_prompt,
                    analysis_scores=analysis_scores,
                    tags=tags,
                    language=st.session_state.language
                )

                # 使快取失效
                st.session_state.export_cache_key = str(time.time())

                # 關閉保存表單
                st.session_state.active_save_msg_id = None

                st.success(t_func("save_success"))

                # 檢查是否有待處理的語言切換
                pending_lang = st.session_state.pop('pending_language_switch', None)
                if pending_lang:
                    st.session_state.language = pending_lang
                    st.session_state.language_change_confirmed = True

                st.rerun()

            except Exception as e:
                st.error(f"{t_func('save_error')}: {str(e)}")
        else:
            st.warning(t_func("please_enter_name"))



def render_new_conversation_button(t_func: Callable[[str], str]):
    """
    渲染「開始新對話」按鈕

    Args:
        t_func: 翻譯函數
    """
    if st.button("🔄 " + t_func("new_conversation"), use_container_width=True):
        # 重置所有對話狀態
        st.session_state.current_session = create_new_session()
        st.session_state.trigger_optimization = False
        st.session_state.pending_responses = {}
        st.session_state.active_save_msg_id = None
        st.session_state.is_processing = False
        st.rerun()


def get_conversation_ui_translations():
    """
    獲取對話式 UI 所需的額外翻譯鍵

    Returns:
        翻譯字典（需要合併到 app.py 的 translations）
    """
    return {
        "zh_TW": {
            "chat_input_placeholder": "輸入您要優化的提示...",
            "new_conversation": "開始新對話",
            "analysis_result": "提示分析結果",
            "completeness_label": "完整性",
            "clarity_label": "清晰度",
            "structure_label": "結構性",
            "specificity_label": "具體性",
            "complexity_level": "複雜度",
            "view_details": "查看詳細分析",
            "missing_elements": "缺失元素",
            "improvement_suggestions": "改進建議",
            "please_answer_questions": "請回答上方的改進問題",
            "please_wait": "請稍候...",
            "please_enter_name": "請輸入提示名稱",
            "select_to_copy": "選擇上方『優化後的提示』文字框中的內容即可複製",
            "optimization_complete_hint": "✅ 優化完成！",
            "confirm": "確定",
            "cancel": "取消",
            "loaded_prompt_label": "已載入的提示（可編輯）",
            "start_analysis": "開始分析",
            "clear_loaded": "清除"
        },
        "en": {
            "chat_input_placeholder": "Enter your prompt to optimize...",
            "new_conversation": "New Conversation",
            "analysis_result": "Prompt Analysis Result",
            "completeness_label": "Completeness",
            "clarity_label": "Clarity",
            "structure_label": "Structure",
            "specificity_label": "Specificity",
            "complexity_level": "Complexity",
            "view_details": "View Details",
            "missing_elements": "Missing Elements",
            "improvement_suggestions": "Improvement Suggestions",
            "please_answer_questions": "Please answer the improvement questions above",
            "please_wait": "Please wait...",
            "please_enter_name": "Please enter a name for the prompt",
            "select_to_copy": "Select text from the 'Enhanced Prompt' text area above to copy",
            "optimization_complete_hint": "✅ Optimization complete!",
            "confirm": "Confirm",
            "cancel": "Cancel",
            "loaded_prompt_label": "Loaded Prompt (Editable)",
            "start_analysis": "Start Analysis",
            "clear_loaded": "Clear"
        },
        "ja": {
            "chat_input_placeholder": "最適化したいプロンプトを入力してください...",
            "new_conversation": "新しい会話",
            "analysis_result": "プロンプト分析結果",
            "completeness_label": "完全性",
            "clarity_label": "明確性",
            "structure_label": "構造性",
            "specificity_label": "具体性",
            "complexity_level": "複雑度",
            "view_details": "詳細を表示",
            "missing_elements": "欠落要素",
            "improvement_suggestions": "改善提案",
            "please_answer_questions": "上記の改善質問に答えてください",
            "please_wait": "お待ちください...",
            "please_enter_name": "プロンプト名を入力してください",
            "select_to_copy": "上の「最適化されたプロンプト」テキストエリアからテキストを選択してコピーしてください",
            "optimization_complete_hint": "✅ 最適化完了！",
            "confirm": "確定",
            "cancel": "キャンセル",
            "loaded_prompt_label": "読み込まれたプロンプト（編集可能）",
            "start_analysis": "分析を開始",
            "clear_loaded": "クリア"
        }
    }


def render_input_area_simple(session: ConversationSession, t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    簡化版輸入區域（單次優化流程：輸入 → 分析 → 問題 → 優化 → 重新開始）

    Args:
        session: 對話會話
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """
    # 檢查是否有待處理的優化操作
    if st.session_state.get('trigger_optimization'):
        st.session_state.trigger_optimization = False
        st.session_state.is_processing = True
        responses = st.session_state.get('pending_responses', {})

        try:
            if responses:
                with st.spinner(t_func("processing")):
                    llm = create_llm_func()
                    flow = ConversationFlow(session, llm, st.session_state.language)
                    result = flow.handle_questions_response(responses)

                    optimization_result = result.get("optimization", {})
                    if "error" in optimization_result:
                        st.error(f"Error: {optimization_result.get('error')}")
                    else:
                        st.session_state.current_session = session
                        st.rerun()
        except Exception as e:
            logger.error("Error processing prompt", exc_info=True)
            st.error(f"An unexpected error occurred: {str(e)}")
        finally:
            st.session_state.is_processing = False

    # 檢查當前狀態
    has_messages = len(session.messages) > 0
    has_optimization = session.last_optimization is not None
    has_pending_questions = session.pending_questions is not None and len(session.pending_questions) > 0

    # 檢查是否正在處理
    is_processing = st.session_state.get('is_processing', False)

    # 定義處理提示的共用邏輯
    def process_prompt(prompt_text: str):
        """處理提示分析的共用邏輯"""
        st.session_state.is_processing = True
        try:
            with st.spinner(t_func("processing")):
                llm = create_llm_func()
                flow = ConversationFlow(session, llm, st.session_state.language)
                result = flow.handle_initial_prompt(prompt_text)

                analysis_result = result.get("analysis", {})
                if "error" in analysis_result:
                    st.error(f"Error: {analysis_result.get('error')}")
                else:
                    st.session_state.current_session = session
                    st.rerun()
        except Exception as e:
            logger.error("Error processing prompt", exc_info=True)
            st.error(f"An unexpected error occurred: {str(e)}")
        finally:
            st.session_state.is_processing = False

    # 渲染輸入區域
    if not has_messages:
        st.write(t_func("initial_prompt_header"))


        # 檢查是否有從提示詞庫載入的內容
        if session.current_prompt and session.current_prompt.strip():
            # 顯示已載入的提示（可編輯）
            loaded_prompt = st.text_area(
                t_func("loaded_prompt_label"),
                value=session.current_prompt,
                height=200,
                key="loaded_prompt_display"
            )

            # 提供開始分析或清除選項
            col1, col2 = st.columns(2)
            with col1:
                if st.button(t_func("start_analysis"), key="analyze_loaded", type="primary", use_container_width=True, disabled=is_processing):
                    # 保存編輯後的內容到 session
                    session.current_prompt = loaded_prompt
                    process_prompt(loaded_prompt)

            with col2:
                if st.button(t_func("clear_loaded"), key="clear_loaded", use_container_width=True):
                    session.current_prompt = ""
                    st.rerun()

        else:
            # 沒有載入內容：顯示 chat_input
            user_input = st.chat_input(
                placeholder=t_func("chat_input_placeholder"),
                key="initial_chat_input",
                disabled=is_processing
            )

            if user_input:
                process_prompt(user_input)

    elif has_optimization:
        # 優化完成：顯示提示與重新開始按鈕
        st.success(t_func("optimization_complete_hint"))

        if st.button("🔄 " + t_func("new_conversation"), key="restart_main_area", type="primary", use_container_width=True):
            # 重置所有對話狀態
            st.session_state.current_session = create_new_session()
            st.session_state.trigger_optimization = False
            st.session_state.pending_responses = {}
            st.session_state.active_save_msg_id = None
            st.session_state.is_processing = False
            st.rerun()

    elif has_pending_questions:
        # 等待用戶回答問題（問題已在 render_questions_card 中顯示）
        pass

    else:
        # 其他狀態
        st.info(t_func("please_wait"))
