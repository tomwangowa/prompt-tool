import streamlit as st
import os
import time
from datetime import datetime
from llm_invoker import LLMFactory, ParameterPresets
from prompt_eval import PromptEvaluator
from prompt_database import PromptDatabase
from prompt_storage_local import LocalStoragePromptDB
from config_loader import get_default_config_loader
from conversation_types import create_new_session, ConversationSession, Message, MessageRole, MessageType
from conversation_ui import render_conversation_ui, render_new_conversation_button, get_conversation_ui_translations
from skill_generator import (
    SkillMetadataExtractor,
    SkillComplexityAnalyzer,
    SkillStructureParser,
    SkillMarkdownGenerator,
    SkillFileHandler,
    SkillMetadata,
    SkillComplexity,
    PREDEFINED_TOOLS
)

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
        "save_prompt": "💾 保存提示",
        "load_prompt": "📁 載入提示",
        "load_original": "📄 載入原始",
        "load_optimized": "✨ 載入優化",
        "prompt_library": "提示詞庫",
        "save_name": "提示名稱",
        "save_tags": "標籤 (用逗號分隔)",
        "save_success": "提示已保存！",
        "save_error": "保存失敗",
        "load_success": "提示已載入！",
        "no_saved_prompts": "暫無保存的提示",
        "delete_prompt": "🗑️ 刪除",
        "confirm_delete": "確認刪除此提示？",
        "search_prompts": "搜尋提示詞",
        "prompt_name": "提示名稱",
        "created_at": "創建時間",
        "copy_prompt": "📋 複製提示",
        "export_prompts": "📤 匯出",
        "import_prompts": "📥 匯入",
        "export_success": "匯出成功！",
        "import_success": "匯入成功！已匯入 {imported} 筆，跳過 {skipped} 筆，錯誤 {errors} 筆",
        "import_error": "匯入失敗：{error}",
        "import_file_label": "選擇 JSON 檔案",
        "overwrite_existing": "覆蓋已存在的提示詞",
        "local_storage_notice": "⚠️ 資料儲存在瀏覽器中，請定期匯出以永久保存",
        "specific_model": "具體模型",
        "gemini_api_key_note": "需要設置 GEMINI_API_KEY 環境變數",
        "gemini_api_key_input": "Gemini API Key",
        "gemini_api_key_placeholder": "輸入您的 Gemini API Key (可選,會覆寫環境變數)",
        "gemini_api_key_help": "在此輸入的 API Key 會覆寫 .env 中的設定",
        "gemini_api_key_configured": "✅ API Key 已設定",
        "gemini_api_key_edit": "✏️ 編輯 API Key",
        "gemini_api_key_confirm": "✅ 確認",
        "gemini_api_key_cancel": "❌ 取消",
        "gemini_api_key_get_link": "🔑 [取得 Gemini API Key](https://aistudio.google.com/app/apikey)",
        "vertex_project_note": "需要設置 GOOGLE_CLOUD_PROJECT 環境變數和 Google Cloud 認證",
        # UI 模式切換
        "ui_mode_settings": "介面模式",
        "ui_mode_label": "選擇 UI 模式",
        "conversation_mode": "對話模式（實驗性）",
        "classic_mode": "傳統模式",
        "language_switch_warning": "⚠️ 提醒：切換語言將重新載入介面，請先保存當前的優化結果（如有需要）。",
        # Skill conversion
        "convert_to_skill": "轉換為 Skill",
        "convert_to_skill_button": "🤖 轉換為 Skill",
        "convert_to_skill_short": "🤖 Skill",
        "skill_metadata_dialog_title": "Skill 元數據編輯",
        "skill_metadata_hint": "請檢查並編輯 Skill 的元數據。AI 已自動提取以下資訊：",
        "skill_name": "Skill 名稱",
        "skill_name_help": "使用 kebab-case 格式（例如：data-analysis-helper）",
        "skill_description": "Skill 描述",
        "skill_tools": "使用的工具",
        "skill_language": "Skill 語言",
        "skill_language_help": "選擇生成的 SKILL.md 檔案語言",
        "skill_complexity_notice": "⚠️ 此 Skill 需要額外的資源：",
        "suggested_resources": "建議的資源",
        "generate_skill": "生成 Skill",
        "cancel": "取消",
        "generating_skill": "正在生成 Skill...",
        "extracting_metadata": "正在提取元數據...",
        "analyzing_complexity": "正在分析複雜度...",
        "parsing_structure": "正在解析結構...",
        "generating_markdown": "正在生成 Markdown...",
        "saving_skill": "正在保存 Skill...",
        "skill_generated_success": "✅ Skill 生成成功！",
        "skill_generation_failed": "❌ Skill 生成失敗",
        "how_to_use_skill": "如何使用這個 Skill：",
        "skill_usage_step1": "1. 將 Skill 檔案複製到 Claude Code 的 skills 目錄",
        "skill_usage_step2": "2. 在 Claude Code 中使用 /[skill-name] 來呼叫此 Skill",
        "skill_needs_resources_notice": "⚠️ 此 Skill 需要額外的資源（MCP、腳本或子技能）。",
        "add_resources_manually": "請查看 README.md 以了解如何添加這些資源。",
        "download_skill": "下載 Skill",
        "skill_saved_to": "Skill 已保存到：",
        "mcp_tools_label": "MCP 工具",
        "scripts_label": "腳本",
        "sub_skills_label": "子任務",
        "close": "關閉",
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
        "save_prompt": "💾 Save Prompt",
        "load_prompt": "📁 Load Prompt",
        "load_original": "📄 Load Original",
        "load_optimized": "✨ Load Optimized",
        "prompt_library": "Prompt Library",
        "save_name": "Prompt Name",
        "save_tags": "Tags (comma separated)",
        "save_success": "Prompt saved successfully!",
        "save_error": "Save failed",
        "load_success": "Prompt loaded successfully!",
        "no_saved_prompts": "No saved prompts",
        "delete_prompt": "🗑️ Delete",
        "confirm_delete": "Confirm delete this prompt?",
        "search_prompts": "Search prompts",
        "prompt_name": "Prompt Name",
        "created_at": "Created At",
        "copy_prompt": "📋 Copy Prompt",
        "export_prompts": "📤 Export",
        "import_prompts": "📥 Import",
        "export_success": "Export successful!",
        "import_success": "Import successful! Imported {imported}, skipped {skipped}, errors {errors}",
        "import_error": "Import failed: {error}",
        "import_file_label": "Select JSON file",
        "overwrite_existing": "Overwrite existing prompts",
        "local_storage_notice": "⚠️ Data is stored in browser. Export regularly for permanent backup",
        "specific_model": "Specific Model",
        "gemini_api_key_note": "Requires GEMINI_API_KEY environment variable",
        "gemini_api_key_input": "Gemini API Key",
        "gemini_api_key_placeholder": "Enter your Gemini API Key (optional, overrides environment variable)",
        "gemini_api_key_help": "API Key entered here will override the .env setting",
        "gemini_api_key_configured": "✅ API Key Configured",
        "gemini_api_key_edit": "✏️ Edit API Key",
        "gemini_api_key_confirm": "✅ Confirm",
        "gemini_api_key_cancel": "❌ Cancel",
        "gemini_api_key_get_link": "🔑 [Get Gemini API Key](https://aistudio.google.com/app/apikey)",
        "vertex_project_note": "Requires GOOGLE_CLOUD_PROJECT environment variable and Google Cloud authentication",
        # UI 模式切換
        "ui_mode_settings": "Interface Mode",
        "ui_mode_label": "Select UI Mode",
        "conversation_mode": "Conversation (Experimental)",
        "classic_mode": "Classic",
        "language_switch_warning": "⚠️ Reminder: Switching languages will reload the interface. Please save your optimized results first if needed.",
        # Skill conversion
        "convert_to_skill": "Convert to Skill",
        "convert_to_skill_button": "🤖 Convert to Skill",
        "convert_to_skill_short": "🤖 Skill",
        "skill_metadata_dialog_title": "Edit Skill Metadata",
        "skill_metadata_hint": "Please review and edit the Skill metadata. AI has automatically extracted the following information:",
        "skill_name": "Skill Name",
        "skill_name_help": "Use kebab-case format (e.g., data-analysis-helper)",
        "skill_description": "Skill Description",
        "skill_tools": "Tools Used",
        "skill_language": "Skill Language",
        "skill_language_help": "Choose the language for the generated SKILL.md file",
        "skill_complexity_notice": "⚠️ This Skill requires additional resources:",
        "suggested_resources": "Suggested Resources",
        "generate_skill": "Generate Skill",
        "cancel": "Cancel",
        "generating_skill": "Generating Skill...",
        "extracting_metadata": "Extracting metadata...",
        "analyzing_complexity": "Analyzing complexity...",
        "parsing_structure": "Parsing structure...",
        "generating_markdown": "Generating Markdown...",
        "saving_skill": "Saving Skill...",
        "skill_generated_success": "✅ Skill generated successfully!",
        "skill_generation_failed": "❌ Skill generation failed",
        "how_to_use_skill": "How to use this Skill:",
        "skill_usage_step1": "1. Copy the Skill file to Claude Code's skills directory",
        "skill_usage_step2": "2. Use /[skill-name] in Claude Code to invoke this Skill",
        "skill_needs_resources_notice": "⚠️ This Skill requires additional resources (MCP, scripts, or sub-skills).",
        "add_resources_manually": "Please see README.md for instructions on adding these resources.",
        "download_skill": "Download Skill",
        "skill_saved_to": "Skill saved to:",
        "mcp_tools_label": "MCP Tools",
        "scripts_label": "Scripts",
        "sub_skills_label": "Sub-skills",
        "close": "Close",
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
        "save_prompt": "💾 プロンプトを保存",
        "load_prompt": "📁 プロンプトを読み込み",
        "load_original": "📄 オリジナルを読み込み",
        "load_optimized": "✨ 最適化版を読み込み",
        "prompt_library": "プロンプトライブラリ",
        "save_name": "プロンプト名",
        "save_tags": "タグ (カンマ区切り)",
        "save_success": "プロンプトが保存されました！",
        "save_error": "保存に失敗しました",
        "load_success": "プロンプトが読み込まれました！",
        "no_saved_prompts": "保存されたプロンプトがありません",
        "delete_prompt": "🗑️ 削除",
        "confirm_delete": "このプロンプトを削除しますか？",
        "search_prompts": "プロンプトを検索",
        "prompt_name": "プロンプト名",
        "created_at": "作成日時",
        "copy_prompt": "📋 プロンプトをコピー",
        "export_prompts": "📤 エクスポート",
        "import_prompts": "📥 インポート",
        "export_success": "エクスポート成功！",
        "import_success": "インポート成功！{imported}件インポート、{skipped}件スキップ、{errors}件エラー",
        "import_error": "インポート失敗：{error}",
        "import_file_label": "JSONファイルを選択",
        "overwrite_existing": "既存のプロンプトを上書き",
        "local_storage_notice": "⚠️ データはブラウザに保存されます。定期的にエクスポートしてください",
        "specific_model": "特定のモデル",
        "gemini_api_key_note": "GEMINI_API_KEY環境変数が必要です",
        "gemini_api_key_input": "Gemini API Key",
        "gemini_api_key_placeholder": "Gemini API Keyを入力してください（オプション、環境変数を上書き）",
        "gemini_api_key_help": "ここに入力されたAPI Keyは.envの設定を上書きします",
        "gemini_api_key_configured": "✅ API Key設定済み",
        "gemini_api_key_edit": "✏️ API Keyを編集",
        "gemini_api_key_confirm": "✅ 確認",
        "gemini_api_key_cancel": "❌ キャンセル",
        "gemini_api_key_get_link": "🔑 [Gemini API Keyを取得](https://aistudio.google.com/app/apikey)",
        "vertex_project_note": "GOOGLE_CLOUD_PROJECT環境変数とGoogle Cloud認証が必要です",
        # UI 模式切換
        "ui_mode_settings": "インターフェースモード",
        "ui_mode_label": "UIモードを選択",
        "conversation_mode": "会話モード（実験的）",
        "classic_mode": "クラシックモード",
        "language_switch_warning": "⚠️ リマインダー：言語を切り替えるとインターフェースが再読み込みされます。必要に応じて、最適化された結果を先に保存してください。",
        # Skill conversion
        "convert_to_skill": "Skillに変換",
        "convert_to_skill_button": "🤖 Skillに変換",
        "convert_to_skill_short": "🤖 Skill",
        "skill_metadata_dialog_title": "Skillメタデータ編集",
        "skill_metadata_hint": "Skillのメタデータを確認して編集してください。AIが自動的に以下の情報を抽出しました：",
        "skill_name": "Skill名",
        "skill_name_help": "kebab-case形式を使用（例：data-analysis-helper）",
        "skill_description": "Skill説明",
        "skill_tools": "使用するツール",
        "skill_language": "Skill言語",
        "skill_language_help": "生成されるSKILL.mdファイルの言語を選択",
        "skill_complexity_notice": "⚠️ このSkillには追加のリソースが必要です：",
        "suggested_resources": "推奨リソース",
        "generate_skill": "Skillを生成",
        "cancel": "キャンセル",
        "generating_skill": "Skillを生成中...",
        "extracting_metadata": "メタデータを抽出中...",
        "analyzing_complexity": "複雑度を分析中...",
        "parsing_structure": "構造を解析中...",
        "generating_markdown": "Markdownを生成中...",
        "saving_skill": "Skillを保存中...",
        "skill_generated_success": "✅ Skillが正常に生成されました！",
        "skill_generation_failed": "❌ Skillの生成に失敗しました",
        "how_to_use_skill": "このSkillの使用方法：",
        "skill_usage_step1": "1. SkillファイルをClaude Codeのskillsディレクトリにコピーする",
        "skill_usage_step2": "2. Claude Codeで/[skill-name]を使用してこのSkillを呼び出す",
        "skill_needs_resources_notice": "⚠️ このSkillには追加のリソース（MCP、スクリプト、またはサブスキル）が必要です。",
        "add_resources_manually": "これらのリソースの追加方法については、README.mdを参照してください。",
        "download_skill": "Skillをダウンロード",
        "skill_saved_to": "Skillの保存先：",
        "mcp_tools_label": "MCPツール",
        "scripts_label": "スクリプト",
        "sub_skills_label": "サブスキル",
        "close": "閉じる",
    }
}

# 動態合併對話式 UI 的翻譯
ui_translations = get_conversation_ui_translations()
for lang in translations:
    if lang in ui_translations:
        translations[lang].update(ui_translations[lang])

# 獲取翻譯
def t(key):
    return translations[st.session_state.language].get(key, key)


# Skill conversion functions
def convert_prompt_to_skill(optimized_prompt: str, original_prompt: str = None):
    """Convert optimized prompt to Claude Code Skill"""

    # Step 1: Extract metadata and analyze complexity (共用邏輯)
    with st.spinner(t("extracting_metadata")):
        llm = create_llm()
        metadata_extractor = SkillMetadataExtractor(llm)
        complexity_analyzer = SkillComplexityAnalyzer(llm)

        try:
            auto_metadata = metadata_extractor.extract(optimized_prompt, st.session_state.language)
            complexity = complexity_analyzer.analyze(optimized_prompt, st.session_state.language)
        except Exception as e:
            st.error(f"{t('skill_generation_failed')}: {str(e)}")
            return

    # Step 2: Route based on conversation mode
    if st.session_state.conversation_mode == "advanced":
        # 新的對話式流程
        show_conversational_skill_flow(auto_metadata, complexity, optimized_prompt, original_prompt)
    else:
        # 傳統 modal dialog（保持不變）
        show_skill_metadata_dialog(auto_metadata, complexity, optimized_prompt, original_prompt)


@st.dialog(title="Edit Skill Metadata", width="large")
def show_skill_metadata_dialog(auto_metadata, complexity, optimized_prompt, original_prompt):
    st.markdown(t("skill_metadata_hint"))

    # Skill name input
    skill_name = st.text_input(
        t("skill_name"),
        value=auto_metadata.skill_name,
        help=t("skill_name_help")
    )

    # Description textarea
    description = st.text_area(
        t("skill_description"),
        value=auto_metadata.description,
        height=100
    )

    # Tools multiselect with PREDEFINED_TOOLS
    selected_tools = st.multiselect(
        t("skill_tools"),
        options=PREDEFINED_TOOLS,
        default=auto_metadata.tools
    )

    # Show complexity info if complex dependencies
    if complexity.dependencies:
        deps = complexity.dependencies
        if deps.needs_mcp or deps.needs_scripts or deps.needs_sub_skills:
            st.warning(t("skill_complexity_notice"))

            if deps.needs_mcp:
                st.markdown(f"**{t('mcp_tools_label')}**: {', '.join(deps.mcp_tools)}")
            if deps.needs_scripts:
                st.markdown(f"**{t('scripts_label')}**: {', '.join(deps.script_types)}")
            if deps.needs_sub_skills:
                st.markdown(f"**{t('sub_skills_label')}**: {len(deps.sub_skill_steps)} steps")

            if deps.suggested_resources:
                st.markdown(f"**{t('suggested_resources')}**:")
                for resource in deps.suggested_resources:
                    st.markdown(f"- {resource}")

    # Language selector (English/繁體中文/日本語)
    skill_language = st.selectbox(
        t("skill_language"),
        options=["English", "繁體中文", "日本語"],
        index=0,
        help=t("skill_language_help")
    )

    # Map display names to language codes
    lang_map = {"English": "en", "繁體中文": "zh_TW", "日本語": "ja"}
    skill_lang_code = lang_map[skill_language]

    # Generate / Cancel buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("generate_skill"), key="skill_dialog_generate", type="primary", use_container_width=True):
            # Create final metadata
            final_metadata = SkillMetadata(
                skill_name=skill_name,
                description=description,
                tools=selected_tools,
                use_cases=auto_metadata.use_cases
            )

            # Save metadata to session state for audit button
            st.session_state.final_skill_metadata = final_metadata

            # Generate skill files - DON'T rerun, show result immediately in dialog
            result = generate_skill_files(optimized_prompt, final_metadata, complexity, skill_lang_code)

            # Save to session state for persistence across reruns
            st.session_state.skill_gen_result = result

    # Use session state result if available (persists across reruns)
    if "skill_gen_result" in st.session_state:
        result = st.session_state.skill_gen_result
        final_metadata = st.session_state.get("final_skill_metadata")

    # Show success immediately
    if "skill_gen_result" in st.session_state and result.get("success", False) and final_metadata:
        st.success(f"✅ {t('skill_generated_success')}")

        # Dev mode: show save path
        if result.get("file_path"):
            st.info(f"{t('skill_saved_to')} `{result['file_path']}`")
            st.markdown(f"**{t('how_to_use_skill')}**: `/{final_metadata.skill_name}`")

        # Production mode: show download button
        elif result.get("download_data"):
            skill_name = final_metadata.skill_name

            # Determine if ZIP or SKILL.md
            if complexity.dependencies and (complexity.dependencies.needs_mcp or
                                       complexity.dependencies.needs_scripts or
                                       complexity.dependencies.needs_sub_skills):
                filename = f"{skill_name}.zip"
                mime_type = "application/zip"
                label = f"📦 {t('download_skill')} (ZIP)"
                st.markdown(f"**{label}**")
                with st.expander("📖 安裝說明", expanded=True):
                    st.markdown(f"1. 解壓並移動: `unzip {filename} && mv {skill_name} ~/.claude/skills/`\n2. 使用: `/{skill_name}`")
            else:
                filename = "SKILL.md"
                mime_type = "text/markdown"
                label = f"📄 {t('download_skill')} (SKILL.md)"
                st.markdown(f"**{label}**")
                with st.expander("📖 安裝說明", expanded=True):
                    st.markdown(f"1. 安裝: `mkdir -p ~/.claude/skills/{skill_name} && mv SKILL.md ~/.claude/skills/{skill_name}/`\n2. 使用: `/{skill_name}`")

            st.download_button(
                label=label,
                data=result["download_data"],
                file_name=filename,
                mime=mime_type,
                key="skill_download_button",
                use_container_width=True,
                type="primary"
            )

        # Add close button after download
        if st.button("✅ 完成", key="skill_close_button", use_container_width=True):
            if "skill_gen_result" in st.session_state:
                del st.session_state.skill_gen_result
            if "final_skill_metadata" in st.session_state:
                del st.session_state.final_skill_metadata
            st.rerun()

        # Stop rendering to prevent showing original buttons again
        st.stop()

    elif "skill_gen_result" in st.session_state:
        # Show error if generation failed
        st.error(f"{t('skill_generation_failed')}: {result.get('message', 'Unknown error')}")
        st.stop()

    with col2:
        if st.button(t("cancel"), key="skill_dialog_cancel", use_container_width=True):
            # Clear result and close dialog
            if "skill_gen_result" in st.session_state:
                del st.session_state.skill_gen_result
            if "final_skill_metadata" in st.session_state:
                del st.session_state.final_skill_metadata
            st.rerun()


def generate_skill_files(optimized_prompt, final_metadata, complexity, skill_language):
    """Generate skill files with progress indicators - Returns result dict"""

    with st.spinner(t("generating_skill")):
        llm = create_llm()

        # Parse structure
        st.caption(f"🔍 {t('parsing_structure')}")
        parser = SkillStructureParser(llm)
        structure = parser.parse(optimized_prompt, st.session_state.language)

        # Generate markdown
        st.caption(f"📝 {t('generating_markdown')}")
        generator = SkillMarkdownGenerator()
        skill_content = generator.generate(structure, final_metadata, complexity, skill_language)

        # Save/download
        st.caption(f"💾 {t('saving_skill')}")
        handler = SkillFileHandler(dev_mode=st.session_state.dev_mode)
        result = handler.save_or_download(skill_content, final_metadata, complexity)

    # Return result for display outside button context
    returned_result = {
        "success": result["success"],
        "file_path": result.get("file_path"),
        "download_data": result.get("download_data"),
        "message": result.get("message"),
        "final_metadata": final_metadata,
        "complexity": complexity
    }

    # Debug logging
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[SKILL_GEN] Returning result: success={returned_result['success']}, "
                f"file_path={returned_result['file_path']}, "
                f"download_data_size={len(returned_result['download_data']) if returned_result['download_data'] else 0}, "
                f"dev_mode={st.session_state.dev_mode}")

    return returned_result


# 重置對話會話（統一的重置邏輯）
def reset_conversation_session():
    """重置對話會話狀態"""
    st.session_state.current_session = create_new_session()
    st.session_state.trigger_optimization = False
    st.session_state.pending_responses = {}
    st.session_state.active_save_msg_id = None
    st.session_state.is_processing = False

# 初始化會話狀態
def initialize_session_state():
    # 載入配置
    config = get_default_config_loader()

    # 讀取 dev_mode 設定 (Streamlit Secrets 優先，然後 config.yaml)
    if 'dev_mode' not in st.session_state:
        try:
            if "dev_mode" in st.secrets:
                st.session_state.dev_mode = st.secrets["dev_mode"]
            else:
                st.session_state.dev_mode = config.get('app.dev_mode', True)
        except Exception:
            # No secrets.toml file exists (local development)
            st.session_state.dev_mode = config.get('app.dev_mode', True)

    # Provider 名稱對應表
    provider_display_map = {
        "gemini": "Gemini (API Key)",
        "gemini-vertex": "Gemini (Vertex AI)",
        "claude": "Claude (AWS Bedrock)"
    }

    if 'language' not in st.session_state:
        st.session_state.language = config.get_default_language()

    # LLM 模型選擇 - 從配置檔案讀取預設值
    if 'llm_provider' not in st.session_state:
        default_provider = config.get_default_provider()
        st.session_state.llm_provider = provider_display_map.get(default_provider, "Gemini (API Key)")

    if 'llm_type' not in st.session_state:
        st.session_state.llm_type = config.get_default_provider()

    if 'llm_model' not in st.session_state:
        provider = config.get_default_provider()
        llm_config = config.get_llm_config(provider) or {}  # 防禦 None
        st.session_state.llm_model = llm_config.get('model', 'gemini-3-flash-preview')

    if 'aws_region' not in st.session_state:
        claude_config = config.get_llm_config('claude') or {}  # 防禦 None
        st.session_state.aws_region = claude_config.get('region', 'us-west-2')

    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = ""  # 用戶確認後的 API Key
    if 'gemini_api_key_temp' not in st.session_state:
        st.session_state.gemini_api_key_temp = ""  # 臨時輸入的 API Key (未確認)
    if 'show_gemini_api_key_input' not in st.session_state:
        # 如果還沒有設定 API Key,預設顯示輸入框
        st.session_state.show_gemini_api_key_input = (st.session_state.gemini_api_key == "")

    # 固定使用最適合 Prompt 分析的參數
    # 不需要 session_state 存儲,直接在函數中使用固定值

    # 初始化資料庫 - 根據 dev_mode 選擇儲存方式
    if 'prompt_db' not in st.session_state:
        if st.session_state.dev_mode:
            # 開發模式：使用 SQLite 資料庫
            db_path = config.get('app.database.path', 'prompts.db')
            st.session_state.prompt_db = PromptDatabase(db_path)
        else:
            # 上線模式：使用瀏覽器 LocalStorage
            st.session_state.prompt_db = LocalStoragePromptDB()

    # 初始化對話模式相關狀態
    if 'conversation_mode' not in st.session_state:
        st.session_state.conversation_mode = False  # 預設使用傳統模式（對話模式為實驗性功能）

    if 'current_session' not in st.session_state:
        st.session_state.current_session = create_new_session()

    # 向後相容：保留現有的 current_stage（用於 classic 模式）
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = "initial"

    # 初始化對話式 UI 觸發器
    if 'trigger_optimization' not in st.session_state:
        st.session_state.trigger_optimization = False
    if 'pending_responses' not in st.session_state:
        st.session_state.pending_responses = {}
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    if 'active_save_msg_id' not in st.session_state:
        st.session_state.active_save_msg_id = None



# 創建 LLM 實例
def create_llm():
    llm_type = st.session_state.llm_type
    
    if llm_type == "claude":
        return LLMFactory.create_llm(
            llm_type,
            region=st.session_state.aws_region
        )
    elif llm_type == "gemini":
        # 如果用戶輸入了 API Key,使用它;否則使用環境變數
        kwargs = {"model": st.session_state.llm_model}
        if st.session_state.gemini_api_key:
            kwargs["api_key"] = st.session_state.gemini_api_key
        return LLMFactory.create_llm(llm_type, **kwargs)
    elif llm_type == "gemini-vertex":
        return LLMFactory.create_llm(
            llm_type,
            model=st.session_state.llm_model
        )
    else:
        # 默認返回 Gemini
        kwargs = {"model": st.session_state.llm_model}
        if st.session_state.gemini_api_key:
            kwargs["api_key"] = st.session_state.gemini_api_key
        return LLMFactory.create_llm("gemini", **kwargs)


# 獲取固定的最佳分析參數
def get_current_params():
    """
    返回固定的最佳 Prompt 分析參數
    Temperature=0.2 確保分析結果穩定一致
    """
    return {
        "temperature": 0.2,  # 低溫度確保穩定、可重複的分析
        "top_p": 0.9,        # 適中的選擇範圍
        "top_k": 40,         # 標準設置
        "max_tokens": 4096   # 足夠的輸出空間
    }

# 顯示側邊欄
def show_sidebar():
    # UI 模式切換（所有用戶可用）
    st.sidebar.markdown("### ⚙️ " + t("ui_mode_settings"))
    mode = st.sidebar.radio(
        t("ui_mode_label"),
        options=[t("classic_mode"), t("conversation_mode")],
        index=1 if st.session_state.conversation_mode else 0,
        horizontal=True
    )
    new_mode = (mode == t("conversation_mode"))
    if new_mode != st.session_state.conversation_mode:
        st.session_state.conversation_mode = new_mode
        st.rerun()

    st.sidebar.markdown("---")

    # 對話模式：顯示新對話按鈕（小按鈕）
    if st.session_state.conversation_mode:
        if st.sidebar.button("🔄 " + t("new_conversation"), key="sidebar_new_conversation"):
            reset_conversation_session()
            st.rerun()

    st.sidebar.markdown("---")

    # 開發模式：顯示完整 LLM 設定
    if st.session_state.dev_mode:
        st.sidebar.header(t("aws_settings"))

        # LLM 模型選擇
        available_models = LLMFactory.get_available_models()

        # 提供者選擇
        selected_provider = st.sidebar.selectbox(
            t("select_llm"),
            list(available_models.keys()),
            index=list(available_models.keys()).index(st.session_state.llm_provider) if st.session_state.llm_provider in available_models else 0
        )

        # 更新 session state
        if selected_provider != st.session_state.llm_provider:
            st.session_state.llm_provider = selected_provider
            st.session_state.llm_type = available_models[selected_provider]["type"]
            st.session_state.llm_model = available_models[selected_provider]["models"][0]  # 默認第一個模型

        # 模型選擇
        selected_model = st.sidebar.selectbox(
            t("specific_model"),
            available_models[selected_provider]["models"],
            index=available_models[selected_provider]["models"].index(st.session_state.llm_model) if st.session_state.llm_model in available_models[selected_provider]["models"] else 0
        )
        st.session_state.llm_model = selected_model

        # 顯示認證需求提示和配置
        if st.session_state.llm_type == "gemini":
            st.sidebar.info(t("gemini_api_key_note"))

            # 根據狀態顯示輸入框或編輯按鈕
            if st.session_state.show_gemini_api_key_input:
                # 顯示輸入框
                gemini_api_key_input = st.sidebar.text_input(
                    t("gemini_api_key_input"),
                    value=st.session_state.gemini_api_key_temp if st.session_state.gemini_api_key_temp else st.session_state.gemini_api_key,
                    type="password",
                    placeholder=t("gemini_api_key_placeholder"),
                    help=t("gemini_api_key_help"),
                    key="gemini_api_key_input_field"
                )

                # 將輸入存儲到臨時變數
                st.session_state.gemini_api_key_temp = gemini_api_key_input

                # 添加確認和取消按鈕
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button(t("gemini_api_key_confirm"), key="confirm_api_key", use_container_width=True):
                        # 確認後保存到正式變數
                        st.session_state.gemini_api_key = st.session_state.gemini_api_key_temp
                        st.session_state.show_gemini_api_key_input = False
                        st.session_state.gemini_api_key_temp = ""  # 清空臨時變數
                        st.rerun()
                with col2:
                    if st.button(t("gemini_api_key_cancel"), key="cancel_api_key", use_container_width=True):
                        # 取消編輯,清空臨時變數
                        st.session_state.gemini_api_key_temp = ""
                        # 如果有已保存的 API Key,隱藏輸入框
                        if st.session_state.gemini_api_key:
                            st.session_state.show_gemini_api_key_input = False
                        st.rerun()
            else:
                # 顯示已配置提示和編輯按鈕
                st.sidebar.success(t("gemini_api_key_configured"))
                if st.sidebar.button(t("gemini_api_key_edit"), key="edit_api_key"):
                    st.session_state.show_gemini_api_key_input = True
                    st.rerun()

            # 顯示取得 API Key 的連結（統一處理，避免重複）
            st.sidebar.markdown(t("gemini_api_key_get_link"))

        elif st.session_state.llm_type == "gemini-vertex":
            st.sidebar.info(t("vertex_project_note"))

        # 如果是 Claude (AWS Bedrock)，顯示區域選擇
        if st.session_state.llm_type == "claude":
            aws_regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
            selected_region = st.sidebar.selectbox(
                t("select_region"),
                aws_regions,
                index=aws_regions.index(st.session_state.aws_region) if st.session_state.aws_region in aws_regions else 1
            )
            st.session_state.aws_region = selected_region

        # 固定使用最適合 Prompt 分析的參數 (不顯示參數調整選項)
        # Temperature=0.2 確保分析結果穩定一致
        # 用戶無需調整這些參數,系統會自動使用最佳設置

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

    # 提示詞庫管理（所有模式都顯示）
    st.sidebar.header(t("prompt_library"))

    # 上線模式：顯示 LocalStorage 提示
    if not st.session_state.dev_mode:
        st.sidebar.warning(t("local_storage_notice"))

    show_prompt_library_sidebar()


# 顯示提示詞庫側邊欄
def show_prompt_library_sidebar():
    """顯示提示詞庫管理界面"""
    db = st.session_state.prompt_db

    # 匯出/匯入按鈕
    col_exp, col_imp = st.sidebar.columns(2)
    with col_exp:
        # 匯出按鈕 - 直接生成最新資料（移除快取以避免資料不同步）
        export_data = db.export_prompts()
        st.download_button(
            label=t("export_prompts"),
            data=export_data,
            file_name="prompts_backup.json",
            mime="application/json",
            use_container_width=True
        )

    with col_imp:
        # 匯入按鈕 - 使用 popover 顯示上傳界面
        with st.popover(t("import_prompts"), use_container_width=True):
            uploaded_file = st.file_uploader(
                t("import_file_label"),
                type=['json'],
                key="import_file"
            )
            overwrite = st.checkbox(t("overwrite_existing"), value=False)

            if uploaded_file is not None:
                if st.button("✅ " + t("import_prompts"), key="do_import"):
                    try:
                        # Handle UTF-8 encoding with error handling
                        raw_data = uploaded_file.read()
                        try:
                            json_data = raw_data.decode('utf-8')
                        except UnicodeDecodeError:
                            # Fallback to utf-8 with error replacement
                            json_data = raw_data.decode('utf-8', errors='replace')
                            st.warning("⚠️ Some characters may have been replaced due to encoding issues")
                    except Exception as e:
                        st.error(t("import_error").format(error=f"File read error: {str(e)}"))
                        json_data = None

                    if json_data:
                        result = db.import_prompts(json_data, overwrite=overwrite)

                        if result.get("success"):
                            st.success(t("import_success").format(
                                imported=result["imported"],
                                skipped=result["skipped"],
                                errors=result["errors"]
                            ))
                            st.rerun()
                        else:
                            st.error(t("import_error").format(error=result.get("error", "Unknown")))

    # 搜索框
    search_query = st.sidebar.text_input(t("search_prompts"), key="search_prompts")

    # 載入提示詞
    if search_query:
        prompts = db.search_prompts(search_query, st.session_state.language)
    else:
        prompts = db.load_prompts(limit=20)
    
    if prompts:
        # 顯示提示詞列表
        for prompt in prompts:
            with st.sidebar.expander(f"📝 {prompt['name'][:30]}..."):
                st.write(f"**{t('created_at')}:** {prompt['created_at'][:10]}")
                if prompt['tags']:
                    st.write(f"**Tags:** {', '.join(prompt['tags'])}")
                
                # 預覽區域
                preview_tab1, preview_tab2 = st.tabs(["📄 原始", "✨ 優化"])
                with preview_tab1:
                    st.text_area("原始提示", prompt['original_prompt'][:100] + "...", height=80, disabled=True, key=f"orig_{prompt['id']}")
                with preview_tab2:
                    st.text_area("優化提示", prompt['optimized_prompt'][:100] + "...", height=80, disabled=True, key=f"opt_{prompt['id']}")
                
                # 載入按鈕組
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(t("load_original"), key=f"load_orig_{prompt['id']}", use_container_width=True):
                        # 載入原始提示（支援兩種模式）
                        if st.session_state.conversation_mode:
                            st.session_state.current_session = create_new_session(prompt['original_prompt'])
                        else:
                            st.session_state.initial_prompt = prompt['original_prompt']
                            st.session_state.current_stage = "initial"
                        st.success(f"✅ {t('load_success')} (原始)")
                        st.rerun()

                with col2:
                    if st.button(t("load_optimized"), key=f"load_opt_{prompt['id']}", use_container_width=True):
                        # 載入優化提示（支援兩種模式）
                        if st.session_state.conversation_mode:
                            st.session_state.current_session = create_new_session(prompt['optimized_prompt'])
                        else:
                            st.session_state.initial_prompt = prompt['optimized_prompt']
                            st.session_state.current_stage = "initial"
                        st.success(f"✅ {t('load_success')} (優化)")
                        st.rerun()

                with col3:
                    if st.button(t("convert_to_skill_short"), key=f"skill_{prompt['id']}",
                                 help=t("convert_to_skill"), use_container_width=True):
                        convert_prompt_to_skill(
                            optimized_prompt=prompt['optimized_prompt'],
                            original_prompt=prompt['original_prompt']
                        )
                
                # 刪除按鈕
                if st.button(t("delete_prompt"), key=f"del_{prompt['id']}", use_container_width=True):
                    if db.delete_prompt(prompt['id']):
                        st.success("已刪除")
                        st.rerun()
    else:
        st.sidebar.info(t("no_saved_prompts"))


# 保存提示對話框
def show_save_prompt_dialog(original_prompt, optimized_prompt, analysis_scores=None):
    """顯示保存提示的對話框"""
    with st.expander(t("save_prompt"), expanded=False):
        # 使用 form 來避免 session state 問題
        with st.form("save_prompt_form"):
            save_name = st.text_input(t("save_name"))
            save_tags = st.text_input(t("save_tags"))
            
            if st.form_submit_button(t("save_prompt")):
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

                        st.success(t("save_success"))
                        st.rerun()  # 重新運行以清空表單
                        
                    except Exception as e:
                        st.error(f"{t('save_error')}: {str(e)}")
                else:
                    st.warning("請輸入提示名稱")


# 顯示提示優化界面
def show_optimize_ui():
    st.header(t("app_title"))
    
    # 如果處於起始階段或重新開始
    if not hasattr(st.session_state, 'current_stage') or st.session_state.current_stage == "initial":
        st.header(t("initial_prompt_header"))
        # 使用 session state 中的 initial_prompt 作為預設值
        default_value = st.session_state.get('initial_prompt', '')
        initial_prompt = st.text_area(t("initial_prompt_label"), value=default_value, height=200)
        
        # 顯示識別的提示類型
        if initial_prompt:
            prompt_type = identify_prompt_type(initial_prompt)
            type_display = translations[st.session_state.language]["prompt_types"][prompt_type]
            st.info(f"**{t('prompt_type')}**: {type_display}")

        if st.button(t("analyze_button")):
            if initial_prompt:
                with st.spinner(t("processing")):
                    # 創建評估器並分析提示
                    llm_instance = create_llm()
                    evaluator = PromptEvaluator(llm_instance=llm_instance)
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
        
        # 顯示優化後的提示標題和複製按鈕
        col_title, col_copy = st.columns([3, 1])
        with col_title:
            st.subheader(t("enhanced_prompt"))
        with col_copy:
            if st.button(t("copy_prompt"), key="copy_optimized_prompt"):
                st.toast("✅ 請選擇下方文字框內容進行複製", icon="📋")
        
        st.caption(f"**{t('prompt_type')}**: {enhanced_type_display}")
        st.text_area(t("copy_text"), result["enhanced_prompt"], height=200)
        
        st.subheader(t("improvement_description"))
        for improvement in result["improvements"]:
            st.markdown(f"- {improvement}")
        
        # 保存提示功能
        show_save_prompt_dialog(
            st.session_state.initial_prompt,
            result["enhanced_prompt"],
            st.session_state.get('analysis', {})
        )

        # 提供進一步優化選項和 Skill 轉換
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button(t("save_prompt")):
                st.info("請使用上方的保存功能")

        with col2:
            if st.button(t("convert_to_skill_button")):
                convert_prompt_to_skill(
                    optimized_prompt=result["enhanced_prompt"],
                    original_prompt=st.session_state.initial_prompt
                )

        with col3:
            if st.button(t("optimize_again")):
                st.session_state.initial_prompt = result["enhanced_prompt"]
                st.session_state.prompt_type = enhanced_type
                st.session_state.current_stage = "questions"
                st.rerun()

        with col4:
            if st.button(t("restart")):
                for key in list(st.session_state.keys()):
                    if key not in ["language", "llm_type", "aws_region", "preset", "custom_params", "mode", "prompt_db"]:
                        if key in st.session_state:
                            del st.session_state[key]
                st.session_state.current_stage = "initial"
                st.rerun()

    # 如果處於問題階段
    elif st.session_state.current_stage == "questions":
        st.header(t("improvement_header"))
        
        analysis = st.session_state.analysis
        llm_instance = create_llm()
        evaluator = PromptEvaluator(llm_instance=llm_instance)
        questions = evaluator.generate_questions(analysis, st.session_state.language)
        
        user_responses = {}
        
        for i, question in enumerate(questions):
            if question["type"] == "reasoning":
                user_responses[question["type"]] = st.checkbox(question["question"])
            elif question.get("input_type") == "selectbox":
                # 使用下拉式選單
                options = question.get("options", [])
                labels = [opt["label"] for opt in options]
                keys = [opt["key"] for opt in options]
                default_key = question.get("default", "")
                default_index = keys.index(default_key) if default_key in keys else 0

                selected_label = st.selectbox(
                    question["question"],
                    labels,
                    index=default_index,
                    key=f"q_{i}"
                )
                # 找到對應的 key
                selected_index = labels.index(selected_label)
                user_responses[question["type"]] = keys[selected_index]
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
        new_language = lang_map[selected_language]

        if st.session_state.language != new_language:
            # 檢查是否有未保存的優化結果
            has_unsaved_work = (
                st.session_state.conversation_mode and
                st.session_state.current_session.last_optimization is not None
            )

            # 簡單警告（不阻擋切換）
            if has_unsaved_work:
                st.toast(t("language_switch_warning"), icon="⚠️")

            # 直接切換語言
            st.session_state.language = new_language
            st.rerun()
    
    # 顯示側邊欄
    show_sidebar()

    # 根據模式顯示不同的 UI
    if st.session_state.conversation_mode:
        # 對話式 UI
        render_conversation_ui(t, create_llm)
    else:
        # 傳統階段式 UI
        show_optimize_ui()

if __name__ == "__main__":
    main()