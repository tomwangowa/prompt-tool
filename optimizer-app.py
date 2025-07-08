import streamlit as st
import os
import time
from llm_invoker import LLMFactory, ParameterPresets
from prompt_eval import PromptEvaluator

max_token_length = 131072  # Claude 的最大 tokens 限制


# 翻譯字典
translations = {
    "zh_TW": {  # 繁體中文
        "app_title": "AI 提示工程顧問",
        "initial_prompt_header": "輸入您的初始提示",
        "initial_prompt_label": "在此輸入您想要優化的提示",
        "analyze_button": "分析提示",
        "please_input": "請先輸入提示",
        "improvement_header": "讓我們改進您的提示",
        "generate_button": "生成優化提示",
        "result_header": "優化提示結果",
        "original_prompt": "原始提示",
        "enhanced_prompt": "優化後的提示",
        "copy_text": "可以複製使用",
        "improvement_description": "改進說明",
        "optimize_again": "再次優化",
        "restart": "重新開始",
        "test_connection": "測試連接",
        "connection_success": "連接正常",
        "connection_error": "連接錯誤",
        "aws_settings": "LLM 設置",
        "select_llm": "選擇 LLM 模型",
        "select_preset": "選擇參數預設",
        "select_region": "選擇 AWS 區域",
        "model_params": "模型參數",
        "max_tokens": "最大輸出令牌數",
        "system_prompt": "系統提示",
        "user_prompt": "用戶提示",
        "estimated_tokens": "估計輸入令牌數量",
        "execute_button": "執行",
        "processing": "正在處理...",
        "output_result": "輸出結果",
        "usage_info": "使用情況",
        "input_tokens": "輸入令牌",
        "output_tokens": "輸出令牌",
        "total_tokens": "總令牌",
        "processing_time": "處理時間",
        "api_error": "調用 API 時發生錯誤",
        "custom_preset": "自定義",
        "prompt_type": "提示類型",
        "prompt_types": {
            "zero_shot": "零樣本提示",
            "one_shot": "單樣本提示",
            "few_shot": "少樣本提示",
            "cot": "思維鏈提示",
            "zero_shot_cot": "零樣本思維鏈提示", 
            "step_back": "回退思考提示",
            "react": "推理與行動提示",
            "role": "角色扮演提示",
            "other": "其他類型提示"
        },
    },
    "en": {  # 英文
        "app_title": "AI Prompt Engineering Consultant",
        "initial_prompt_header": "Enter Your Initial Prompt",
        "initial_prompt_label": "Enter the prompt you want to optimize",
        "analyze_button": "Analyze Prompt",
        "please_input": "Please enter a prompt first",
        "improvement_header": "Let's Improve Your Prompt",
        "generate_button": "Generate Optimized Prompt",
        "result_header": "Optimized Prompt Result",
        "original_prompt": "Original Prompt",
        "enhanced_prompt": "Enhanced Prompt",
        "copy_text": "Ready to copy and use",
        "improvement_description": "Improvement Description",
        "optimize_again": "Optimize Again",
        "restart": "Start Over",
        "test_connection": "Test Connection",
        "connection_success": "Connection Successful",
        "connection_error": "Connection Error",
        "aws_settings": "LLM Settings",
        "select_llm": "Select LLM Model",
        "select_preset": "Select Parameter Preset",
        "select_region": "Select AWS Region",
        "model_params": "Model Parameters",
        "max_tokens": "Maximum Output Tokens",
        "system_prompt": "System Prompt",
        "user_prompt": "User Prompt",
        "estimated_tokens": "Estimated Input Tokens",
        "execute_button": "Execute",
        "processing": "Processing...",
        "output_result": "Output Result",
        "usage_info": "Usage Information",
        "input_tokens": "Input Tokens",
        "output_tokens": "Output Tokens",
        "total_tokens": "Total Tokens",
        "processing_time": "Processing Time",
        "api_error": "Error calling API",
        "custom_preset": "Custom",
        "prompt_type": "Prompt Type",
        "prompt_types": {
            "zero_shot": "Zero-Shot Prompt",
            "one_shot": "One-Shot Prompt",
            "few_shot": "Few-Shot Prompt",
            "cot": "Chain of Thought Prompt",
            "zero_shot_cot": "Zero-Shot Chain of Thought Prompt",
            "step_back": "Step-Back Prompt",
            "react": "ReAct (Reason+Act) Prompt",
            "role": "Role-Playing Prompt",
            "other": "Other Prompt Type"
        },
    },
    "ja": {  # 日文
        "app_title": "AI プロンプトエンジニアリングコンサルタント",
        "initial_prompt_header": "初期プロンプトを入力してください",
        "initial_prompt_label": "最適化したいプロンプトをここに入力してください",
        "analyze_button": "プロンプトを分析",
        "please_input": "最初にプロンプトを入力してください",
        "improvement_header": "プロンプトを改善しましょう",
        "generate_button": "最適化されたプロンプトを生成",
        "result_header": "最適化プロンプト結果",
        "original_prompt": "元のプロンプト",
        "enhanced_prompt": "強化されたプロンプト",
        "copy_text": "コピーして使用できます",
        "improvement_description": "改善の説明",
        "optimize_again": "再度最適化",
        "restart": "最初からやり直す",
        "test_connection": "接続テスト",
        "connection_success": "接続成功",
        "connection_error": "接続エラー",
        "aws_settings": "LLM設定",
        "select_llm": "LLMモデルを選択",
        "select_preset": "パラメータプリセットを選択",
        "select_region": "AWSリージョンを選択",
        "model_params": "モデルパラメータ",
        "max_tokens": "最大出力トークン数",
        "system_prompt": "システムプロンプト",
        "user_prompt": "ユーザープロンプト",
        "estimated_tokens": "推定入力トークン数",
        "execute_button": "実行",
        "processing": "処理中...",
        "output_result": "出力結果",
        "usage_info": "使用情報",
        "input_tokens": "入力トークン",
        "output_tokens": "出力トークン",
        "total_tokens": "合計トークン",
        "processing_time": "処理時間",
        "api_error": "API呼び出しエラー",
        "custom_preset": "カスタム",
        "prompt_type": "プロンプトタイプ",
        "prompt_types": {
            "zero_shot": "ゼロショットプロンプト",
            "one_shot": "ワンショットプロンプト",
            "few_shot": "フューショットプロンプト",
            "cot": "思考の連鎖プロンプト",
            "zero_shot_cot": "ゼロショット思考の連鎖プロンプト",
            "step_back": "ステップバックプロンプト",
            "react": "推論と行動プロンプト",
            "role": "ロールプレイプロンプト",
            "other": "その他のプロンプト"
        },
   
    }
}

# 獲取翻譯
def t(key):
    return translations[st.session_state.language].get(key, key)

# 初始化會話狀態
def initialize_session_state():
    if 'language' not in st.session_state:
        st.session_state.language = "zh_TW"
    
    # 固定使用 Claude 和 us-west-2 區域
    st.session_state.llm_type = "claude"
    st.session_state.aws_region = "us-west-2"
    
    if 'preset' not in st.session_state:
        st.session_state.preset = "平衡"
    
    if 'custom_params' not in st.session_state:
        st.session_state.custom_params = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 1024
        }
    


# 創建 LLM 實例
def create_llm():
    return LLMFactory.create_llm(
        st.session_state.llm_type,
        region=st.session_state.aws_region
    )

# 獲取當前參數
def get_current_params():
    if st.session_state.preset == "自定義" or st.session_state.preset == "Custom" or st.session_state.preset == "カスタム":
        return st.session_state.custom_params
    else:
        return ParameterPresets.get_preset(st.session_state.preset)

# 顯示側邊欄
def show_sidebar():
    st.sidebar.header(t("aws_settings"))
    
    
    # 參數預設選擇
    preset_options = {
        "zh_TW": ["平衡", "創意", "精確", "編程", "分析", "自定義"],
        "en": ["Balanced", "Creative", "Precise", "Coding", "Analytical", "Custom"],
        "ja": ["バランス", "クリエイティブ", "精密", "コーディング", "分析的", "カスタム"]
    }
    # preset_values = ["平衡", "創意", "精確", "編程", "分析", "自定義"]
    preset_map = {
        "平衡": "平衡", "創意": "創意", "精確": "精確", "編程": "編程", "分析": "分析", "自定義": "自定義",
        "Balanced": "平衡", "Creative": "創意", "Precise": "精確", "Coding": "編程", "Analytical": "分析", "Custom": "自定義",
        "バランス": "平衡", "クリエイティブ": "創意", "精密": "精確", "コーディング": "編程", "分析的": "分析", "カスタム": "自定義"
    }
    
    current_preset_display = None
    for lang in preset_options:
        for i, preset in enumerate(preset_options[lang]):
            if preset_map.get(preset) == st.session_state.preset:
                current_preset_display = preset_options[st.session_state.language][i]
                break
        if current_preset_display:
            break
    
    if not current_preset_display:
        current_preset_display = preset_options[st.session_state.language][-1]  # 自定義
    
    selected_preset = st.sidebar.selectbox(
        t("select_preset"),
        preset_options[st.session_state.language],
        index=preset_options[st.session_state.language].index(current_preset_display)
    )
    
    # 轉換顯示名稱到實際值
    st.session_state.preset = preset_map.get(selected_preset, "平衡")
    
    # 模型參數部分 - 改為始終顯示滑塊
    st.sidebar.header(t("model_params"))
    
    # 獲取當前預設的參數
    params = get_current_params()
    
    # 如果選擇自定義，直接修改 custom_params，否則創建臨時參數用於顯示
    if st.session_state.preset == "自定義" or st.session_state.preset == "Custom" or st.session_state.preset == "カスタム":
        # Temperature 滑塊
        st.session_state.custom_params["temperature"] = st.sidebar.slider(
            "Temperature", 0.0, 1.0, st.session_state.custom_params["temperature"]
        )
        
        # Top P 滑塊
        st.session_state.custom_params["top_p"] = st.sidebar.slider(
            "Top P", 0.0, 1.0, st.session_state.custom_params["top_p"]
        )
        
        # Top K 滑塊
        st.session_state.custom_params["top_k"] = st.sidebar.slider(
            "Top K", 0, 100, st.session_state.custom_params["top_k"]
        )
        
        # 最大輸出令牌數滑塊 - 更新範圍為 200-4096
        st.session_state.custom_params["max_tokens"] = st.sidebar.slider(
            t("max_tokens"), 200, 4096, st.session_state.custom_params["max_tokens"]
        )
    else:
        # 顯示預設參數的滑塊，並禁用它們
        st.sidebar.slider(
            "Temperature", 0.0, 1.0, params["temperature"], disabled=True
        )
        
        st.sidebar.slider(
            "Top P", 0.0, 1.0, params["top_p"], disabled=True
        )
        
        st.sidebar.slider(
            "Top K", 0, 100, params["top_k"], disabled=True
        )
        
        st.sidebar.slider(
            t("max_tokens"), 200, 4096, params["max_tokens"], disabled=True
        )

    # # 如果選擇自定義，顯示參數滑塊
    # if selected_preset == preset_options[st.session_state.language][-1]:  # 自定義選項
    #     st.sidebar.header(t("model_params"))
    #     st.session_state.custom_params["temperature"] = st.sidebar.slider(
    #         "Temperature", 0.0, 1.0, st.session_state.custom_params["temperature"]
    #     )
    #     st.session_state.custom_params["top_p"] = st.sidebar.slider(
    #         "Top P", 0.0, 1.0, st.session_state.custom_params["top_p"]
    #     )
    #     st.session_state.custom_params["top_k"] = st.sidebar.slider(
    #         "Top K", 0, 100, st.session_state.custom_params["top_k"]
    #     )
    #     st.session_state.custom_params["max_tokens"] = st.sidebar.slider(
    #         t("max_tokens"), 100, 4096, st.session_state.custom_params["max_tokens"]
    #     )
    # else:
    #     # 顯示當前預設的參數值
    #     preset_params = ParameterPresets.get_preset(st.session_state.preset)
    #     st.sidebar.header(t("model_params"))
    #     st.sidebar.info(f"Temperature: {preset_params['temperature']}")
    #     st.sidebar.info(f"Top P: {preset_params['top_p']}")
    #     st.sidebar.info(f"Top K: {preset_params['top_k']}")
    #     st.sidebar.info(f"{t('max_tokens')}: {preset_params['max_tokens']}")
    
    # 連接測試
    st.sidebar.header(t("test_connection"))
    if st.sidebar.button(t("test_connection")):
        with st.sidebar:
            llm = create_llm()
            is_connected, message = llm.check_connection()
            if is_connected:
                st.success(message)
            else:
                st.error(message)
    


# 顯示提示優化界面
def show_optimize_ui():
    st.header(t("app_title"))
    
    # 如果處於起始階段或重新開始
    if not hasattr(st.session_state, 'current_stage') or st.session_state.current_stage == "initial":
        st.header(t("initial_prompt_header"))
        initial_prompt = st.text_area(t("initial_prompt_label"), height=200)
        
        # 顯示識別的提示類型
        if initial_prompt:
            prompt_type = identify_prompt_type(initial_prompt)
            type_display = translations[st.session_state.language]["prompt_types"][prompt_type]
            st.info(f"**{t('prompt_type')}**: {type_display}")

        if st.button(t("analyze_button")):
            if initial_prompt:
                with st.spinner(t("processing")):
                    # 創建評估器並分析提示
                    evaluator = PromptEvaluator(
                        llm_type=st.session_state.llm_type,
                        region=st.session_state.aws_region
                    )
                    analysis = evaluator.analyze_prompt(initial_prompt, st.session_state.language)

                    # 保存提示類型到會話狀態
                    st.session_state.prompt_type = identify_prompt_type(initial_prompt)
                    st.session_state.analysis = analysis
                    st.session_state.initial_prompt = initial_prompt
                    st.session_state.current_stage = "questions"
                    st.rerun()  # 重新運行以顯示問題
            else:
                st.warning(t("please_input"))
    
    # 如果處於結果階段，顯示原始和優化後的提示類型
    elif st.session_state.current_stage == "result":
        st.header(t("result_header"))
        
        result = st.session_state.optimization_result
        
        # 顯示原始提示及其類型
        original_type = st.session_state.prompt_type
        original_type_display = translations[st.session_state.language]["prompt_types"][original_type]
        
        st.subheader(t("original_prompt"))
        st.caption(f"**{t('prompt_type')}**: {original_type_display}")
        st.text_area(t("original_prompt"), st.session_state.initial_prompt, height=150)
        
        # 顯示優化後的提示及其類型
        enhanced_type = identify_prompt_type(result["enhanced_prompt"])
        enhanced_type_display = translations[st.session_state.language]["prompt_types"][enhanced_type]
        
        st.subheader(t("enhanced_prompt"))
        st.caption(f"**{t('prompt_type')}**: {enhanced_type_display}")
        st.text_area(t("copy_text"), result["enhanced_prompt"], height=200)
        
        st.subheader(t("improvement_description"))
        for improvement in result["improvements"]:
            st.markdown(f"- {improvement}")
        
        # 提供進一步優化選項
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("optimize_again")):
                st.session_state.initial_prompt = result["enhanced_prompt"]
                st.session_state.prompt_type = enhanced_type
                st.session_state.current_stage = "questions"
                st.rerun()
        
        with col2:
            if st.button(t("restart")):
                for key in list(st.session_state.keys()):
                    if key not in ["language", "llm_type", "aws_region", "preset", "custom_params", "mode"]:
                        if key in st.session_state:
                            del st.session_state[key]
                st.session_state.current_stage = "initial"
                st.rerun()

    # 如果處於問題階段
    elif st.session_state.current_stage == "questions":
        st.header(t("improvement_header"))
        
        analysis = st.session_state.analysis
        evaluator = PromptEvaluator(
            llm_type=st.session_state.llm_type,
            region=st.session_state.aws_region
        )
        questions = evaluator.generate_questions(analysis, st.session_state.language)
        
        user_responses = {}
        
        for i, question in enumerate(questions):
            if question["type"] == "reasoning":
                user_responses[question["type"]] = st.checkbox(question["question"])
            else:
                user_responses[question["type"]] = st.text_input(f"{question['question']}", key=f"q_{i}")
        
        if st.button(t("generate_button")):
            # 步驟3：優化提示
            with st.spinner(t("processing")):
                optimization_result = evaluator.optimize_prompt(
                    st.session_state.initial_prompt, 
                    user_responses, 
                    analysis, 
                    st.session_state.language
                )
                st.session_state.optimization_result = optimization_result
                st.session_state.current_stage = "result"
                st.rerun()  # 重新運行以顯示結果
    
    # 如果處於結果階段
    elif st.session_state.current_stage == "result":
        st.header(t("result_header"))
        
        result = st.session_state.optimization_result
        
        st.subheader(t("original_prompt"))
        st.text_area(t("original_prompt"), st.session_state.initial_prompt, height=150)
        
        st.subheader(t("enhanced_prompt"))
        st.text_area(t("copy_text"), result["enhanced_prompt"], height=200)
        
        st.subheader(t("improvement_description"))
        for improvement in result["improvements"]:
            st.markdown(f"- {improvement}")
        
        # 提供進一步優化選項
        col1, col2 = st.columns(2)
        with col1:
            if st.button(t("optimize_again")):
                st.session_state.initial_prompt = result["enhanced_prompt"]
                st.session_state.current_stage = "questions"
                st.rerun()
        
        with col2:
            if st.button(t("restart")):
                for key in list(st.session_state.keys()):
                    if key not in ["language", "llm_type", "aws_region", "preset", "custom_params", "mode"]:
                        if key in st.session_state:
                            del st.session_state[key]
                st.session_state.current_stage = "initial"
                st.rerun()



# 提示類型識別函數
def identify_prompt_type(prompt_text):
    """識別提示的類型"""
    prompt_types = {
        "zh_TW": {
            "zero_shot": "零樣本提示",
            "one_shot": "單樣本提示",
            "few_shot": "少樣本提示",
            "cot": "思維鏈提示",
            "zero_shot_cot": "零樣本思維鏈提示", 
            "step_back": "回退思考提示",
            "react": "推理與行動提示",
            "role": "角色扮演提示",
            "other": "其他類型提示"
        },
        "en": {
            "zero_shot": "Zero-Shot Prompt",
            "one_shot": "One-Shot Prompt",
            "few_shot": "Few-Shot Prompt",
            "cot": "Chain of Thought Prompt",
            "zero_shot_cot": "Zero-Shot Chain of Thought Prompt",
            "step_back": "Step-Back Prompt",
            "react": "ReAct (Reason+Act) Prompt",
            "role": "Role-Playing Prompt",
            "other": "Other Prompt Type"
        },
        "ja": {
            "zero_shot": "ゼロショットプロンプト",
            "one_shot": "ワンショットプロンプト",
            "few_shot": "フューショットプロンプト",
            "cot": "思考の連鎖プロンプト",
            "zero_shot_cot": "ゼロショット思考の連鎖プロンプト",
            "step_back": "ステップバックプロンプト",
            "react": "推論と行動プロンプト",
            "role": "ロールプレイプロンプト",
            "other": "その他のプロンプト"
        }
    }
    
    # 檢測提示類型的特徵
    prompt_lower = prompt_text.lower()
    
    # 檢測角色提示 (優先級最高)
    role_patterns = [
        "你是", "扮演", "act as", "you are a", "role", 
        "あなたは", "として行動", "役割"
    ]
    for pattern in role_patterns:
        if pattern in prompt_lower:
            return "role"
    
    # 檢測 ReAct 提示
    react_patterns = [
        "思考", "行動", "觀察", "reason", "act", "observe", 
        "推論", "行動", "観察"
    ]
    react_count = sum(1 for pattern in react_patterns if pattern in prompt_lower)
    if react_count >= 2:  # 至少包含其中兩個關鍵詞
        return "react"
    
    # 檢測零樣本思維鏈提示
    zero_shot_cot_patterns = [
        "一步步思考", "step by step", "step-by-step", "think step by step",
        "ステップバイステップ", "一歩一歩"
    ]
    for pattern in zero_shot_cot_patterns:
        if pattern in prompt_lower:
            return "zero_shot_cot"
    
    # 檢測思維鏈提示 (一般 CoT)
    cot_patterns = [
        "思考過程", "推理步驟", "顯示你的工作", "思維鏈", 
        "show your work", "reasoning process", "chain of thought",
        "推論過程", "思考の過程", "思考の連鎖"
    ]
    for pattern in cot_patterns:
        if pattern in prompt_lower:
            return "cot"
    
    # 檢測回退思考提示
    step_back_patterns = [
        "回退一步", "step back", "後退一步", "更廣泛的角度",
        "broader perspective", "一歩下がって"
    ]
    for pattern in step_back_patterns:
        if pattern in prompt_lower:
            return "step_back"
    
    # 檢測是否有示例 (判斷是零樣本、單樣本還是少樣本)
    # 尋找輸入/輸出對的模式
    example_patterns = [
        "例子:", "範例:", "舉例:", "example:", "examples:", "input:", "output:",
        "輸入:", "輸出:", "入力:", "出力:", "例:"
    ]
    
    has_examples = False
    example_count = 0
    
    for pattern in example_patterns:
        if pattern in prompt_lower:
            has_examples = True
            example_count += prompt_lower.count(pattern)
    
    if has_examples:
        if example_count == 1:
            return "one_shot"
        elif example_count > 1:
            return "few_shot"
    
    # 如果沒有檢測到任何特定類型，則為零樣本提示
    return "zero_shot"

# 添加自定義 CSS
def add_custom_css():
    st.markdown("""
    <style>
    /* 增加選擇框寬度 */
    div[data-baseweb="select"] {
        min-width: 200px !important;
    }
    
    /* 確保下拉選項也足夠寬 */
    div[role="listbox"] {
        min-width: 200px !important;
    }
    
    /* 增加整體內容區寬度 */
    .block-container {
        max-width: 1200px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 主函數
def main():
    add_custom_css()
    
    # 初始化會話狀態
    initialize_session_state()
    
    # 語言選擇
    col1, col2, col3 = st.columns([1, 8, 1])
    with col1:
        st.empty()
    with col3:
        selected_language = st.selectbox(
            "Language",
            ["繁體中文", "English", "日本語"],
            index=["zh_TW", "en", "ja"].index(st.session_state.language),
            key="language_selector"
        )
        
        # 更新語言選擇
        lang_map = {"繁體中文": "zh_TW", "English": "en", "日本語": "ja"}
        if st.session_state.language != lang_map[selected_language]:
            st.session_state.language = lang_map[selected_language]
            st.rerun()
    
    # 顯示側邊欄
    show_sidebar()
    
    # 只顯示優化模式界面
    show_optimize_ui()

if __name__ == "__main__":
    main()