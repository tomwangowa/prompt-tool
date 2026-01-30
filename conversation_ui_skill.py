#!/usr/bin/env python3
"""
對話式 Skill 轉換 UI 組件
處理在對話流程中的 skill 生成、編輯和審查
"""

import streamlit as st
import logging
from typing import Callable, Any

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
from skill_auditor import audit_skill, AuditIssue

logger = logging.getLogger(__name__)

# 語言選項常數（統一管理）
SUPPORTED_SKILL_LANGUAGES = {
    "English": "en",
    "繁體中文": "zh_TW",
    "日本語": "ja"
}

# Skill 流程相關的 session state 鍵（統一清理管理）
SKILL_FLOW_STATE_KEYS = [
    "trigger_skill_conversion",
    "skill_metadata_extracted",
    "skill_optimized_prompt",
    "skill_original_prompt",
    "cached_metadata",
    "cached_complexity",
    "skill_gen_result",
    "final_skill_metadata",
    "skill_content",
    "skill_complexity",
    "audit_report",
    "show_metadata_form_conv",
    "fix_mode_conv"
]


def render_skill_conversion_flow(t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    渲染對話式 skill 轉換流程（Advanced 模式專用）

    Args:
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """

    logger.info("=== SKILL CONVERSION FLOW STARTED ===")

    # Step 1: 元數據提取（如果尚未提取）
    if not st.session_state.get('skill_metadata_extracted'):
        optimized_prompt = st.session_state.skill_optimized_prompt
        original_prompt = st.session_state.get('skill_original_prompt', '')

        with st.spinner(t_func("extracting_metadata")):
            try:
                llm = create_llm_func()
                metadata_extractor = SkillMetadataExtractor(llm)
                complexity_analyzer = SkillComplexityAnalyzer(llm)

                auto_metadata = metadata_extractor.extract(optimized_prompt, st.session_state.language)
                complexity = complexity_analyzer.analyze(optimized_prompt, st.session_state.language)

                # 緩存結果
                st.session_state.cached_metadata = auto_metadata
                st.session_state.cached_complexity = complexity
                st.session_state.skill_metadata_extracted = True

                logger.info(f"Metadata extracted: {auto_metadata.skill_name}")
                st.rerun()

            except Exception as e:
                logger.error(f"Metadata extraction failed: {e}", exc_info=True)
                st.error(f"{t_func('skill_generation_failed')}: {str(e)}")

                # 清理狀態並允許重試
                st.session_state.trigger_skill_conversion = False
                return

    # Step 2: 顯示元數據卡片
    auto_metadata = st.session_state.cached_metadata
    complexity = st.session_state.cached_complexity
    optimized_prompt = st.session_state.skill_optimized_prompt
    original_prompt = st.session_state.get('skill_original_prompt', '')

    with st.expander("✅ " + t_func("metadata_extracted"), expanded=not st.session_state.get('skill_gen_result')):
        # 顯示提取的資訊
        st.markdown(f"**{t_func('skill_name')}**: `{auto_metadata.skill_name}`")
        st.markdown(f"**{t_func('skill_description')}**: {auto_metadata.description}")
        st.markdown(f"**{t_func('skill_tools')}**: {', '.join(auto_metadata.tools) or t_func('none')}")

        # 複雜度警告（如果需要）
        if complexity.dependencies and (complexity.dependencies.needs_mcp or
                                       complexity.dependencies.needs_scripts or
                                       complexity.dependencies.needs_sub_skills):
            st.warning(t_func("skill_complexity_notice"))

            if complexity.dependencies.needs_mcp:
                st.markdown(f"**{t_func('mcp_tools_label')}**: {', '.join(complexity.dependencies.mcp_tools)}")
            if complexity.dependencies.needs_scripts:
                st.markdown(f"**{t_func('scripts_label')}**: {', '.join(complexity.dependencies.script_types)}")
            if complexity.dependencies.needs_sub_skills:
                st.markdown(f"**{t_func('sub_skills_label')}**: {len(complexity.dependencies.sub_skill_steps)} steps")

    # Step 3: 操作按鈕（如果尚未生成）
    if not st.session_state.get('skill_gen_result'):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✏️ " + t_func("edit"), key="edit_metadata_btn_conv", use_container_width=True):
                st.session_state.show_metadata_form_conv = True
                st.rerun()

        with col2:
            if st.button("🚀 " + t_func("generate_directly"), key="generate_directly_btn",
                        type="primary", use_container_width=True):
                # 使用統一的語言映射
                skill_lang = st.session_state.get("language", "en")

                _generate_skill_conversational(auto_metadata, complexity, optimized_prompt, skill_lang, t_func, create_llm_func)
                st.rerun()

    # Step 4: 編輯表單（如果需要）
    if st.session_state.get("show_metadata_form_conv", False):
        _render_metadata_edit_form(auto_metadata, complexity, optimized_prompt, t_func, create_llm_func)

    # Step 5: 顯示生成結果（如果存在）
    if st.session_state.get("skill_gen_result"):
        _render_skill_generation_result(auto_metadata, complexity, t_func, create_llm_func)


def _generate_skill_conversational(metadata, complexity, optimized_prompt, skill_language,
                                   t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    生成 skill 並顯示進度（對話式版本）

    Args:
        metadata: Skill 元數據
        complexity: 複雜度分析結果
        optimized_prompt: 優化後的 prompt
        skill_language: Skill 語言代碼
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """

    logger.info(f"=== GENERATING SKILL: {metadata.skill_name} ===")
    logger.info(f"Metadata - name: {metadata.skill_name}, desc: {metadata.description[:50]}..., tools: {metadata.tools}")
    logger.info(f"Complexity - needs_mcp: {complexity.dependencies.needs_mcp if complexity.dependencies else False}")

    # 驗證 metadata 有效性
    if not metadata.skill_name or len(metadata.skill_name.strip()) < 3:
        st.error(f"❌ Invalid skill name: '{metadata.skill_name}'. Name must be at least 3 characters.")
        logger.error(f"Invalid skill name: {metadata.skill_name}")
        return

    if not metadata.description or len(metadata.description.strip()) < 10:
        st.error(f"❌ Invalid skill description: too short. Description must be at least 10 characters.")
        logger.error(f"Invalid description length: {len(metadata.description) if metadata.description else 0}")
        return

    with st.status(t_func("generating_skill"), expanded=True) as status:
        llm = create_llm_func()

        st.write("🔍 " + t_func("parsing_structure"))
        parser = SkillStructureParser(llm)
        structure = parser.parse(optimized_prompt, st.session_state.language)

        st.write("📝 " + t_func("generating_markdown"))
        generator = SkillMarkdownGenerator()
        skill_content = generator.generate(structure, metadata, complexity, skill_language)

        st.write("💾 " + t_func("saving_skill"))
        handler = SkillFileHandler(dev_mode=st.session_state.get("dev_mode", False))
        result = handler.save_or_download(skill_content, metadata, complexity)

        status.update(label=t_func("skill_generated_success"), state="complete")

    # 保存到 session state
    st.session_state.skill_gen_result = result
    st.session_state.final_skill_metadata = metadata
    st.session_state.skill_content = skill_content
    st.session_state.skill_complexity = complexity

    logger.info(f"Skill generated successfully: {metadata.skill_name}")


def _render_metadata_edit_form(auto_metadata, complexity, optimized_prompt,
                               t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    渲染元數據編輯表單

    Args:
        auto_metadata: 自動提取的元數據
        complexity: 複雜度分析結果
        optimized_prompt: 優化後的 prompt
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """

    with st.form("edit_metadata_form_conv"):
        st.markdown("### " + t_func("edit_skill_metadata"))

        skill_name = st.text_input(t_func("skill_name"), value=auto_metadata.skill_name)
        description = st.text_area(t_func("skill_description"), value=auto_metadata.description, height=100)
        selected_tools = st.multiselect(
            t_func("skill_tools"),
            options=PREDEFINED_TOOLS,
            default=auto_metadata.tools
        )

        # 語言選擇（使用統一常數）
        current_lang = st.session_state.get("language", "en")

        # 安全查找當前語言標籤（避免 IndexError）
        found_labels = [k for k, v in SUPPORTED_SKILL_LANGUAGES.items() if v == current_lang]
        current_lang_label = found_labels[0] if found_labels else "English"

        skill_language_label = st.selectbox(
            t_func("skill_language"),
            options=list(SUPPORTED_SKILL_LANGUAGES.keys()),
            index=list(SUPPORTED_SKILL_LANGUAGES.keys()).index(current_lang_label)
        )
        skill_language = SUPPORTED_SKILL_LANGUAGES[skill_language_label]

        col1, col2 = st.columns(2)

        with col1:
            cancel = st.form_submit_button(t_func("cancel"), use_container_width=True)

        with col2:
            submit = st.form_submit_button(t_func("confirm"), type="primary", use_container_width=True)

        if cancel:
            st.session_state.show_metadata_form_conv = False
            st.rerun()

        if submit:
            # 驗證必填欄位
            validation_errors = []

            if not skill_name or not skill_name.strip():
                validation_errors.append(t_func("skill_name") + " " + t_func("required"))

            if not description or not description.strip():
                validation_errors.append(t_func("skill_description") + " " + t_func("required"))

            # Note: Tools are optional - some skills don't require specific tools

            # 顯示驗證錯誤並停止
            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                st.stop()

            # 創建更新後的元數據
            final_metadata = SkillMetadata(
                skill_name=skill_name.strip(),
                description=description.strip(),
                tools=selected_tools,
                use_cases=auto_metadata.use_cases
            )

            # 生成 skill
            _generate_skill_conversational(final_metadata, complexity, optimized_prompt,
                                          skill_language, t_func, create_llm_func)
            st.session_state.show_metadata_form_conv = False
            st.rerun()


def _render_skill_generation_result(metadata, complexity, t_func: Callable[[str], str],
                                    create_llm_func: Callable[[], Any]):
    """
    渲染 skill 生成結果和後續操作

    Args:
        metadata: Skill 元數據
        complexity: 複雜度分析結果
        t_func: 翻譯函數
        create_llm_func: 創建 LLM 實例的函數
    """

    result = st.session_state.skill_gen_result

    st.success(t_func("skill_generated_success"))
    st.markdown("---")

    # 下載按鈕（簡化：永遠只下載 SKILL.md）
    if result.get("download_data"):
        skill_name = metadata.skill_name

        # 安裝說明
        with st.expander("📖 安裝說明", expanded=True):
            st.markdown(f"1. 安裝: `mkdir -p ~/.claude/skills/{skill_name} && mv SKILL.md ~/.claude/skills/{skill_name}/`")
            st.markdown(f"2. 使用: `/{skill_name}`")

            # 如果有依賴，顯示額外提示
            if complexity.dependencies and (complexity.dependencies.needs_mcp or
                                           complexity.dependencies.needs_scripts or
                                           complexity.dependencies.needs_sub_skills):
                st.info("ℹ️ 此 Skill 需要額外資源（MCP/腳本），請查看 SKILL.md 中的說明。")

        st.download_button(
            label=f"📄 {t_func('download_skill')} (SKILL.md)",
            data=result["download_data"],
            file_name="SKILL.md",
            mime="text/markdown",
            key="skill_download_btn_conv",
            use_container_width=True,
            type="primary"
        )

    # 審查建議
    st.markdown("---")
    st.markdown(f"### 💡 {t_func('next_steps')}")

    if not st.session_state.get("audit_report"):
        if st.button(t_func("audit_skill"), key="audit_skill_btn_conv", use_container_width=True):
            with st.spinner(t_func("audit_running")):
                audit_report = audit_skill(
                    st.session_state.skill_content,
                    metadata.skill_name
                )
                st.session_state.audit_report = audit_report
                st.rerun()

    # 顯示審查結果（如果存在）
    if st.session_state.get("audit_report"):
        _render_audit_results(t_func)

    # 清理按鈕
    st.markdown("---")
    if st.button("🔄 " + t_func("start_new_skill"), key="reset_skill_flow_conv", use_container_width=True):
        # 清理所有相關 state（使用統一的常數列表）
        for key in SKILL_FLOW_STATE_KEYS:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()


def _render_audit_results(t_func: Callable[[str], str]):
    """
    渲染審查結果和修正選項

    Args:
        t_func: 翻譯函數
    """

    audit_report = st.session_state.audit_report

    with st.expander("📊 " + t_func("audit_results"), expanded=True):
        # 分數和狀態
        if audit_report.passed:
            st.success(f"{t_func('audit_passed')} - {t_func('audit_score')}: {audit_report.score}/100")
        else:
            st.error(f"{t_func('audit_failed')} - {t_func('audit_score')}: {audit_report.score}/100")

        st.markdown(f"**{audit_report.summary}**")

        # 問題列表
        if audit_report.issues:
            st.markdown(f"### {t_func('found_issues')}: {len(audit_report.issues)}")

            for issue in audit_report.issues:
                severity_icons = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵"
                }
                icon = severity_icons.get(issue.severity, "⚪")
                severity_text = t_func(f"severity_{issue.severity}")

                st.markdown(f"{icon} **[{severity_text}] {issue.category}**: {issue.message}")
                if issue.suggestion:
                    st.info(f"💡 {issue.suggestion}")
                st.markdown("---")
        else:
            st.success(t_func("audit_no_issues"))

    # 修正選項（如果有問題）
    if audit_report.issues:
        st.markdown("---")
        st.markdown(f"### 💡 {t_func('improvement_suggestions')}")

        # 根據是否通過顯示不同訊息
        if not audit_report.passed:
            st.warning(t_func("skill_needs_improvement"))
        else:
            st.info(t_func("skill_can_be_optimized"))

        # Only show manual edit option (AI fix not yet implemented in conversational mode)
        if st.button(t_func("manual_edit"),
                   key="manual_edit_btn_conv",
                   use_container_width=True,
                   type="primary"):
            st.session_state.fix_mode_conv = "manual"
            st.rerun()

    # 手動編輯流程
    if audit_report and audit_report.issues and st.session_state.get("fix_mode_conv") == "manual":
        st.markdown("---")
        st.markdown(f"### ✏️ {t_func('edit_skill_content')}")

        # 獲取當前的 skill content
        current_content = st.session_state.get("fixed_skill_content") or st.session_state.get("skill_content", "")

        edited_content = st.text_area(
            t_func("edit_skill_content"),
            value=current_content,
            height=400,
            key="manual_edit_textarea_conv",
            label_visibility="collapsed"
        )

        col_save, col_reaudit, col_cancel = st.columns(3)

        with col_save:
            if st.button(t_func("save_changes"), key="save_manual_edit_btn_conv", use_container_width=True, type="primary"):
                # 更新 skill content
                st.session_state.fixed_skill_content = edited_content
                st.session_state.skill_content = edited_content
                st.success(t_func("fix_success"))
                st.session_state.fix_mode_conv = None

        with col_reaudit:
            if st.button(t_func("re_audit"), key="re_audit_manual_btn_conv", use_container_width=True):
                # 使用編輯後的內容重新審查
                with st.spinner(t_func("audit_running")):
                    new_audit_report = audit_skill(
                        edited_content,
                        st.session_state.final_skill_metadata.skill_name
                    )
                    st.session_state.audit_report = new_audit_report
                    st.session_state.fix_mode_conv = None
                    st.rerun()

        with col_cancel:
            if st.button(t_func("cancel"), key="cancel_manual_edit_btn_conv", use_container_width=True):
                st.session_state.fix_mode_conv = None
                st.rerun()
