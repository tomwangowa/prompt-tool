#!/usr/bin/env python3
"""
對話式 UI 組件模組
實作所有對話式介面的 UI 渲染函數
"""

import streamlit as st
import time
from typing import Dict, Any, List, Optional, Callable

from conversation_types import Message, MessageRole, MessageType, ConversationSession
from conversation_flow import ConversationFlow


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
        box-shadow: 0 -4px 12px rgba(0,0,0,0.08);
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)


def render_conversation_ui(t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    渲染對話式 UI 主介面

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

    # 根據狀態渲染輸入區域（包含 token 指示器）
    render_input_area(session, t_func, create_llm_func)


def render_token_indicator(session: ConversationSession, t_func: Callable[[str], str], compact: bool = True):
    """
    渲染 Token 使用狀態指示器

    Args:
        session: 對話會話
        t_func: 翻譯函數
        compact: 是否使用緊湊模式（適合輸入框旁邊）
    """
    if session.current_context_tokens == 0:
        return  # 沒有 token 使用時不顯示

    usage_percentage = session.get_token_usage_percentage()

    # 根據使用率選擇圖示
    if usage_percentage >= 90:
        icon = "🔴"
    elif usage_percentage >= 70:
        icon = "🟡"
    else:
        icon = "🟢"

    if compact:
        # 緊湊模式：單行顯示 + 90% 時的快速操作
        status_text = f"{icon} {session.current_context_tokens:,} / {session.context_window_limit:,} ({usage_percentage:.1f}%)"

        if usage_percentage >= 90:
            # 高危狀態：顯示錯誤和保存按鈕
            col1, col2 = st.columns([4, 1])
            with col1:
                st.error(status_text, icon=icon)
            with col2:
                if st.button("💾", key="save_warning_compact", help=t_func("save_now"), type="primary"):
                    st.session_state.show_save_dialog = True
        elif usage_percentage >= 70:
            st.warning(status_text, icon=icon)
        else:
            st.info(status_text, icon=icon)
    else:
        # 完整模式：進度條 + 詳細資訊
        col1, col2 = st.columns([3, 1])

        with col1:
            st.progress(
                min(usage_percentage / 100, 1.0),
                text=f"{icon} {t_func('context_usage')}: {session.current_context_tokens:,} / {session.context_window_limit:,} ({usage_percentage:.1f}%)"
            )

        with col2:
            # 當接近限制時顯示警告按鈕
            if usage_percentage >= 90:
                if st.button("💾 " + t_func("save_now"), key="save_warning", type="primary"):
                    st.session_state.show_save_dialog = True

        # 顯示警告訊息
        if usage_percentage >= 90:
            st.error(t_func("token_limit_warning"))
        elif usage_percentage >= 70:
            st.warning(t_func("token_limit_notice"))


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
        st.markdown("#### 📊 " + t_func("analysis_result"))

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
        st.markdown("#### 💡 " + t_func("improvement_header"))

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

                        selected = st.selectbox(
                            question_text,
                            options=labels,
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
        st.markdown("#### ✨ " + t_func("result_header"))

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

            # 操作按鈕
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 " + t_func("optimize_again"), key=f"iterate_{msg.id}", use_container_width=True):
                    # 觸發新一輪優化
                    st.session_state.trigger_iterate = True
                    st.rerun()

            with col2:
                # 保存提示按鈕
                with st.popover(t_func("save_prompt"), use_container_width=True):
                    render_save_prompt_form(original_prompt, enhanced_prompt, msg.analysis_data, t_func)


def render_save_prompt_form(original_prompt: str, optimized_prompt: str, analysis_scores: Optional[Dict], t_func: Callable[[str], str]):
    """
    渲染保存提示表單

    Args:
        original_prompt: 原始提示
        optimized_prompt: 優化後的提示
        analysis_scores: 分析評分
        t_func: 翻譯函數
    """
    save_name = st.text_input(t_func("save_name"))
    save_tags = st.text_input(t_func("save_tags"))

    if st.button(t_func("save_prompt"), key="confirm_save_in_form"):
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
                st.success(t_func("save_success"))
                st.rerun()

            except Exception as e:
                st.error(f"{t_func('save_error')}: {str(e)}")
        else:
            st.warning(t_func("please_enter_name"))


def render_input_area(session: ConversationSession, t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    根據會話狀態渲染輸入區域

    Args:
        session: 對話會話
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """
    # 檢查是否有待處理的操作
    if st.session_state.get('trigger_optimization'):
        # 執行優化
        st.session_state.trigger_optimization = False
        st.session_state.is_processing = True  # 標記處理中
        responses = st.session_state.get('pending_responses', {})

        try:
            if responses:
                with st.spinner(t_func("processing")):
                    llm = create_llm_func()
                    flow = ConversationFlow(session, llm, st.session_state.language)
                    result = flow.handle_questions_response(responses)

                    # 檢查是否有錯誤
                    optimization_result = result.get("optimization", {})
                    if "error" in optimization_result:
                        st.error(f"Error: {optimization_result.get('error')}")
                        # 錯誤時不 rerun，讓錯誤訊息保持可見
                    else:
                        st.session_state.current_session = session
                        st.rerun()  # 成功時才 rerun
        except Exception as e:
            # 捕捉未預期的異常
            st.error(f"An unexpected error occurred: {str(e)}")
        finally:
            st.session_state.is_processing = False  # 確保處理標記被重置

    if st.session_state.get('trigger_iterate'):
        # 觸發新一輪優化
        st.session_state.trigger_iterate = False
        st.session_state.is_processing = True  # 標記處理中

        try:
            with st.spinner(t_func("processing")):
                llm = create_llm_func()
                flow = ConversationFlow(session, llm, st.session_state.language)
                result = flow.handle_initial_prompt(session.current_prompt)

                # 檢查是否有錯誤
                analysis_result = result.get("analysis", {})
                if "error" in analysis_result:
                    st.error(f"Error: {analysis_result.get('error')}")
                    # 錯誤時不 rerun，讓錯誤訊息保持可見
                else:
                    st.session_state.current_session = session
                    st.rerun()  # 成功時才 rerun
        except Exception as e:
            # 捕捉未預期的異常
            st.error(f"An unexpected error occurred: {str(e)}")
        finally:
            st.session_state.is_processing = False  # 確保處理標記被重置

    # 判斷當前階段
    has_messages = len(session.messages) > 0
    has_optimization = session.last_optimization is not None
    has_pending_questions = session.pending_questions is not None and len(session.pending_questions) > 0

    # 檢查是否正在處理中
    is_processing = st.session_state.get('is_processing', False)

    # 顯示 Token 使用狀態（緊湊模式，在輸入框上方）
    render_token_indicator(session, t_func, compact=True)

    # 輸入區域
    if not has_messages:
        # 初始狀態：顯示提示輸入
        st.markdown("### " + t_func("initial_prompt_header"))

        user_input = st.chat_input(
            placeholder=t_func("chat_input_placeholder"),
            key="initial_chat_input",
            disabled=is_processing
        )

        if user_input:
            # 處理初始輸入
            st.session_state.is_processing = True
            try:
                with st.spinner(t_func("processing")):
                    llm = create_llm_func()
                    flow = ConversationFlow(session, llm, st.session_state.language)
                    result = flow.handle_initial_prompt(user_input)

                    # 檢查是否有錯誤
                    analysis_result = result.get("analysis", {})
                    if "error" in analysis_result:
                        st.error(f"Error: {analysis_result.get('error')}")
                        # 錯誤時不 rerun，讓錯誤訊息保持可見
                    else:
                        # 更新 session
                        st.session_state.current_session = session
                        st.rerun()  # 成功時才 rerun
            except Exception as e:
                # 捕捉未預期的異常
                st.error(f"An unexpected error occurred: {str(e)}")
            finally:
                st.session_state.is_processing = False

    elif has_optimization:
        # 優化完成後：支援持續對話
        user_input = st.chat_input(
            placeholder=t_func("followup_input_placeholder"),
            key="followup_chat_input",
            disabled=is_processing
        )

        if user_input:
            # 處理後續對話
            st.session_state.is_processing = True
            try:
                with st.spinner(t_func("processing")):
                    llm = create_llm_func()
                    flow = ConversationFlow(session, llm, st.session_state.language)
                    result = flow.handle_followup_message(user_input)

                    # 檢查是否有錯誤
                    if "error" in result:
                        st.error(f"Error: {result.get('error')}")
                        # 錯誤時不 rerun，讓錯誤訊息保持可見
                    else:
                        # 更新 session
                        st.session_state.current_session = session
                        st.rerun()  # 成功時才 rerun
            except Exception as e:
                # 捕捉未預期的異常
                st.error(f"An unexpected error occurred: {str(e)}")
            finally:
                st.session_state.is_processing = False

    elif has_pending_questions:
        # 等待用戶回答問題（問題已在 render_questions_card 中顯示）
        # 這裡只需提示
        st.info(t_func("please_answer_questions"))

    else:
        # 其他狀態
        st.info(t_func("please_wait"))


def render_new_conversation_button(t_func: Callable[[str], str]):
    """
    渲染「開始新對話」按鈕

    Args:
        t_func: 翻譯函數
    """
    if st.button("🔄 " + t_func("new_conversation"), use_container_width=True):
        from conversation_types import create_new_session
        st.session_state.current_session = create_new_session()
        # 清除觸發器
        st.session_state.trigger_optimization = False
        st.session_state.trigger_iterate = False
        st.session_state.pending_responses = {}
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
            "followup_input_placeholder": "想要進一步調整嗎？試試「加上範例」或「更正式一點」",
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
            "select_to_copy": "選擇上方文字框中的內容即可複製",
            "context_usage": "上下文使用量",
            "save_now": "立即保存",
            "token_limit_warning": "⚠️ Token 使用量已達 90%！建議立即保存當前結果，以免超出限制。",
            "token_limit_notice": "💡 Token 使用量已達 70%，請注意對話長度。"
        },
        "en": {
            "chat_input_placeholder": "Enter your prompt to optimize...",
            "followup_input_placeholder": "Want to adjust further? Try 'add examples' or 'make it more formal'",
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
            "select_to_copy": "Select text from the text area above to copy",
            "context_usage": "Context Usage",
            "save_now": "Save Now",
            "token_limit_warning": "⚠️ Token usage has reached 90%! Please save your results to avoid exceeding the limit.",
            "token_limit_notice": "💡 Token usage has reached 70%. Please monitor conversation length."
        },
        "ja": {
            "chat_input_placeholder": "最適化したいプロンプトを入力してください...",
            "followup_input_placeholder": "さらに調整しますか？「例を追加」または「よりフォーマルに」など試してください",
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
            "select_to_copy": "上のテキストエリアからテキストを選択してコピーしてください",
            "context_usage": "コンテキスト使用量",
            "save_now": "今すぐ保存",
            "token_limit_warning": "⚠️ トークン使用量が90%に達しました！制限を超えないように結果を保存してください。",
            "token_limit_notice": "💡 トークン使用量が70%に達しました。会話の長さにご注意ください。"
        }
    }
