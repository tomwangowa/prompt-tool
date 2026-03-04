#!/usr/bin/env python3
"""
Conversational Skill Conversion UI Components
Handles skill generation, editing, and auditing within the conversation flow.
"""

import streamlit as st
import logging
from typing import Callable, Any

from skill_generator import (
    SkillAnalyzer,
    SkillAnalysis,
    SkillGenerator,
    SkillFileHandler,
    PREDEFINED_TOOLS
)
from skill_auditor import audit_skill, AuditIssue

logger = logging.getLogger(__name__)

# All 12 possible SKILL.md sections
ALL_SECTIONS = [
    "overview", "when_to_use", "process", "setup", "usage",
    "guidelines", "style_guide", "examples", "constraints",
    "error_handling", "security", "output_format"
]

# Human-readable labels for each section
SECTION_LABELS = {
    "overview": "Overview",
    "when_to_use": "When to Use",
    "process": "Process / Workflow",
    "setup": "Setup / Prerequisites",
    "usage": "Usage",
    "guidelines": "Guidelines",
    "style_guide": "Style Guide",
    "examples": "Examples",
    "constraints": "Constraints",
    "error_handling": "Error Handling",
    "security": "Security",
    "output_format": "Output Format",
}

# Language option constants (unified management)
SUPPORTED_SKILL_LANGUAGES = {
    "English": "en",
    "繁體中文": "zh_TW",
    "日本語": "ja"
}

# Skill flow session state keys (unified cleanup management)
SKILL_FLOW_STATE_KEYS = [
    "trigger_skill_conversion",
    "skill_optimized_prompt",
    "skill_original_prompt",
    "cached_analysis",           # SkillAnalysis dict
    "skill_analysis_done",       # Phase 1 complete
    "skill_analysis_confirmed",  # Phase 2 confirmed
    "skill_content",             # Generated SKILL.md content
    "audit_report",
    "skill_flow_active",
    # Deprecated (keep for cleanup of old sessions)
    "skill_metadata_extracted",
    "cached_metadata",
    "cached_complexity",
    "skill_gen_result",
    "final_skill_metadata",
    "skill_complexity",
    "show_metadata_form_conv",
    "fix_mode_conv",
]


def render_skill_conversion_flow(t_func: Callable[[str], str], create_llm_func: Callable[[], Any]):
    """
    Advanced mode: skill conversion in conversation flow.

    Three-phase pipeline:
      Phase 1 - Analysis: SkillAnalyzer produces a SkillAnalysis from the optimized prompt.
      Phase 2 - Confirmation: User reviews/edits the analysis before generation.
      Phase 3 - Generation: SkillGenerator produces the final SKILL.md content.

    Args:
        t_func: Translation function.
        create_llm_func: Factory function to create an LLM instance.
    """
    logger.info("=== SKILL CONVERSION FLOW STARTED ===")
    t = t_func

    # --- Phase 1: Analysis (if not done) ---
    if not st.session_state.get("skill_analysis_done"):
        prompt = st.session_state.get("skill_optimized_prompt", "")
        if not prompt:
            st.warning(_safe_t(t, "no_optimized_prompt", "No optimized prompt available."))
            return

        with st.spinner(_safe_t(t, "extracting_metadata", "Analyzing prompt...")):
            try:
                llm = create_llm_func()
                analyzer = SkillAnalyzer(llm)
                analysis = analyzer.analyze(prompt, st.session_state.get("language", "en"))
                st.session_state.cached_analysis = analysis.to_dict()
                st.session_state.skill_analysis_done = True
                logger.info(f"Analysis complete: type={analysis.skill_type}, name={analysis.metadata.get('name', '?')}")
                st.rerun()
            except Exception as e:
                logger.error(f"Analysis failed: {e}", exc_info=True)
                st.error(f"{_safe_t(t, 'skill_generation_failed', 'Skill generation failed')}: {str(e)}")
                # Allow retry
                st.session_state.trigger_skill_conversion = False
                return
        return

    # --- Phase 2: Show analysis for confirmation ---
    analysis_data = st.session_state.get("cached_analysis", {})
    analysis = SkillAnalysis.from_dict(analysis_data)

    if not st.session_state.get("skill_analysis_confirmed"):
        _render_analysis_confirmation(analysis, t)
        return

    # --- Phase 3: Generate (if not done) ---
    if not st.session_state.get("skill_content"):
        prompt = st.session_state.get("skill_optimized_prompt", "")
        confirmed = SkillAnalysis.from_dict(st.session_state.get("cached_analysis", {}))

        with st.spinner(_safe_t(t, "generating_skill", "Generating SKILL.md...")):
            try:
                llm = create_llm_func()
                generator = SkillGenerator(llm)
                content = generator.generate(confirmed, prompt, st.session_state.get("language", "en"))
                st.session_state.skill_content = content
                logger.info(f"SKILL.md generated: {len(content.splitlines())} lines")
                st.rerun()
            except Exception as e:
                logger.error(f"Generation failed: {e}", exc_info=True)
                st.error(f"{_safe_t(t, 'skill_generation_failed', 'Skill generation failed')}: {str(e)}")
                return
        return

    # --- Show result ---
    _render_skill_generation_result(t)


def _safe_t(t_func: Callable[[str], str], key: str, fallback: str) -> str:
    """
    Safely call the translation function with a fallback.

    If the translation function returns the key itself (meaning no translation
    was found) or raises, the fallback string is returned instead.

    Args:
        t_func: Translation function.
        key: Translation key.
        fallback: Fallback string if key is not translated.

    Returns:
        Translated string or fallback.
    """
    try:
        result = t_func(key)
        # If t returns the key unchanged, it means no translation exists
        if result == key:
            return fallback
        return result
    except Exception:
        return fallback


def _render_analysis_confirmation(analysis: SkillAnalysis, t_func: Callable[[str], str]):
    """
    Phase 2 UI: Display AI analysis results for user to confirm or edit.

    Shows editable fields for skill name, type, tools, description, and
    section checkboxes with AI reasoning. User can confirm to proceed to
    generation or cancel the flow.

    Args:
        analysis: The SkillAnalysis produced by Phase 1.
        t_func: Translation function.
    """
    t = t_func

    st.markdown(f"### {_safe_t(t, 'analysis_results', 'Analysis Results')}")
    st.info(_safe_t(t, "review_analysis_hint", "Review the AI analysis below. You can edit any field before generating."))

    # --- Editable fields ---

    # Skill name
    current_name = analysis.metadata.get("name", "")
    skill_name = st.text_input(
        _safe_t(t, "skill_name", "Skill Name"),
        value=current_name,
        key="analysis_skill_name"
    )

    # Skill type
    skill_types = ["workflow", "tool-wrapper", "knowledge", "creative"]
    current_type_idx = skill_types.index(analysis.skill_type) if analysis.skill_type in skill_types else 2
    skill_type = st.selectbox(
        _safe_t(t, "skill_type", "Skill Type"),
        options=skill_types,
        index=current_type_idx,
        key="analysis_skill_type"
    )

    # Tools
    current_tools = analysis.metadata.get("tools", [])
    # Ensure default values are in the options list
    valid_defaults = [tool for tool in current_tools if tool in PREDEFINED_TOOLS]
    selected_tools = st.multiselect(
        _safe_t(t, "skill_tools", "Tools"),
        options=PREDEFINED_TOOLS,
        default=valid_defaults,
        key="analysis_skill_tools"
    )

    # Description
    current_desc = analysis.metadata.get("description", "")
    description = st.text_area(
        _safe_t(t, "skill_description", "Description"),
        value=current_desc,
        height=100,
        key="analysis_skill_description"
    )

    # --- Section checkboxes ---
    st.markdown(f"#### {_safe_t(t, 'recommended_sections', 'Recommended Sections')}")
    st.caption(_safe_t(t, "section_checkbox_hint", "Check the sections to include in the generated SKILL.md."))

    recommended = set(analysis.recommended_sections)
    reasoning = analysis.section_reasoning or {}

    selected_sections = []
    for section in ALL_SECTIONS:
        label = SECTION_LABELS.get(section, section.replace("_", " ").title())
        help_text = reasoning.get(section, "")
        is_checked = section in recommended
        if st.checkbox(
            label,
            value=is_checked,
            key=f"section_cb_{section}",
            help=help_text if help_text else None
        ):
            selected_sections.append(section)

    # --- Complexity info ---
    complexity = analysis.complexity or {}
    if complexity.get("needs_mcp") or complexity.get("needs_scripts"):
        st.warning(_safe_t(t, "skill_complexity_notice", "This skill has external dependencies (MCP tools, scripts)."))
        deps = complexity.get("dependencies", [])
        if deps:
            st.markdown(f"**Dependencies**: {', '.join(deps)}")

    # --- Action buttons ---
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        cancel = st.button(
            _safe_t(t, "cancel", "Cancel"),
            key="analysis_cancel_btn",
            use_container_width=True
        )

    with col2:
        generate = st.button(
            _safe_t(t, "generate_skill_btn", "Generate Skill"),
            key="analysis_generate_btn",
            type="primary",
            use_container_width=True
        )

    if cancel:
        # Cleanup state and exit the flow
        for key in SKILL_FLOW_STATE_KEYS:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    if generate:
        # Validate required fields
        if not skill_name or not skill_name.strip():
            st.error(_safe_t(t, "skill_name_required", "Skill name is required."))
            return
        if not description or not description.strip():
            st.error(_safe_t(t, "skill_description_required", "Description is required."))
            return
        if not selected_sections:
            st.error(_safe_t(t, "sections_required", "At least one section must be selected."))
            return

        # Update cached_analysis with user edits
        updated = st.session_state.get("cached_analysis", {})
        updated["metadata"]["name"] = skill_name.strip()
        updated["metadata"]["description"] = description.strip()
        updated["metadata"]["tools"] = selected_tools
        updated["skill_type"] = skill_type
        updated["recommended_sections"] = selected_sections
        st.session_state.cached_analysis = updated

        st.session_state.skill_analysis_confirmed = True
        st.rerun()


def _render_skill_generation_result(t_func: Callable[[str], str]):
    """
    Render skill generation result and follow-up actions.

    Displays the generated SKILL.md content with download button,
    installation instructions, audit capability, and cleanup option.

    Args:
        t_func: Translation function.
    """
    t = t_func

    content = st.session_state.get("skill_content", "")
    analysis_data = st.session_state.get("cached_analysis", {})
    skill_name = analysis_data.get("metadata", {}).get("name", "unnamed-skill")

    st.success(_safe_t(t, "skill_generated_success", "Skill generated successfully!"))
    st.markdown("---")

    # Installation instructions
    with st.expander(_safe_t(t, "installation_instructions", "Installation Instructions"), expanded=True):
        st.markdown(f"1. Install: `mkdir -p ~/.claude/skills/{skill_name} && mv SKILL.md ~/.claude/skills/{skill_name}/`")
        st.markdown(f"2. Use: `/{skill_name}`")

        # Show dependency notice if applicable
        complexity = analysis_data.get("complexity", {})
        if complexity.get("needs_mcp") or complexity.get("needs_scripts"):
            st.info(_safe_t(t, "skill_has_dependencies", "This skill requires additional resources (MCP/scripts). See SKILL.md for details."))

    # Download button
    st.download_button(
        label=f"{_safe_t(t, 'download_skill', 'Download Skill')} (SKILL.md)",
        data=content,
        file_name="SKILL.md",
        mime="text/markdown",
        key="skill_download_btn_conv",
        use_container_width=True,
        type="primary"
    )

    # Preview
    with st.expander(_safe_t(t, "preview_skill", "Preview SKILL.md"), expanded=False):
        st.code(content, language="markdown")

    # Audit section
    st.markdown("---")
    st.markdown(f"### {_safe_t(t, 'next_steps', 'Next Steps')}")

    if not st.session_state.get("audit_report"):
        if st.button(
            _safe_t(t, "audit_skill", "Audit Skill"),
            key="audit_skill_btn_conv",
            use_container_width=True
        ):
            with st.spinner(_safe_t(t, "audit_running", "Running audit...")):
                audit_report = audit_skill(content, skill_name)
                st.session_state.audit_report = audit_report
                st.rerun()

    # Show audit results if available
    if st.session_state.get("audit_report"):
        _render_audit_results(t)

    # Cleanup / start new
    st.markdown("---")
    if st.button(
        _safe_t(t, "start_new_skill", "Start New Skill"),
        key="reset_skill_flow_conv",
        use_container_width=True
    ):
        for key in SKILL_FLOW_STATE_KEYS:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


def _render_audit_results(t_func: Callable[[str], str]):
    """
    Render audit results and manual fix options.

    Args:
        t_func: Translation function.
    """
    t = t_func
    audit_report = st.session_state.audit_report
    analysis_data = st.session_state.get("cached_analysis", {})
    skill_name = analysis_data.get("metadata", {}).get("name", "unnamed-skill")

    with st.expander(_safe_t(t, "audit_results", "Audit Results"), expanded=True):
        # Score and status
        if audit_report.passed:
            st.success(f"{_safe_t(t, 'audit_passed', 'Audit Passed')} - {_safe_t(t, 'audit_score', 'Score')}: {audit_report.score}/100")
        else:
            st.error(f"{_safe_t(t, 'audit_failed', 'Audit Failed')} - {_safe_t(t, 'audit_score', 'Score')}: {audit_report.score}/100")

        st.markdown(f"**{audit_report.summary}**")

        # Issue list
        if audit_report.issues:
            st.markdown(f"### {_safe_t(t, 'found_issues', 'Issues Found')}: {len(audit_report.issues)}")

            for issue in audit_report.issues:
                severity_icons = {
                    "critical": "RED",
                    "high": "ORANGE",
                    "medium": "YELLOW",
                    "low": "BLUE"
                }
                icon = severity_icons.get(issue.severity, "")
                severity_text = _safe_t(t, f"severity_{issue.severity}", issue.severity.upper())

                st.markdown(f"**[{severity_text}] {issue.category}**: {issue.message}")
                if issue.suggestion:
                    st.info(f"Suggestion: {issue.suggestion}")
                st.markdown("---")
        else:
            st.success(_safe_t(t, "audit_no_issues", "No issues found."))

    # Fix options (if there are issues)
    if audit_report.issues:
        st.markdown("---")
        st.markdown(f"### {_safe_t(t, 'improvement_suggestions', 'Improvement Suggestions')}")

        if not audit_report.passed:
            st.warning(_safe_t(t, "skill_needs_improvement", "This skill needs improvement before use."))
        else:
            st.info(_safe_t(t, "skill_can_be_optimized", "This skill passed but can be further optimized."))

        # Manual edit option
        if st.button(
            _safe_t(t, "manual_edit", "Manual Edit"),
            key="manual_edit_btn_conv",
            use_container_width=True,
            type="primary"
        ):
            st.session_state.fix_mode_conv = "manual"
            st.rerun()

    # Manual edit flow
    if audit_report and audit_report.issues and st.session_state.get("fix_mode_conv") == "manual":
        st.markdown("---")
        st.markdown(f"### {_safe_t(t, 'edit_skill_content', 'Edit Skill Content')}")

        current_content = st.session_state.get("fixed_skill_content") or st.session_state.get("skill_content", "")

        edited_content = st.text_area(
            _safe_t(t, "edit_skill_content", "Edit Skill Content"),
            value=current_content,
            height=400,
            key="manual_edit_textarea_conv",
            label_visibility="collapsed"
        )

        col_save, col_reaudit, col_cancel = st.columns(3)

        with col_save:
            if st.button(
                _safe_t(t, "save_changes", "Save Changes"),
                key="save_manual_edit_btn_conv",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.fixed_skill_content = edited_content
                st.session_state.skill_content = edited_content
                st.success(_safe_t(t, "fix_success", "Changes saved."))
                st.session_state.fix_mode_conv = None

        with col_reaudit:
            if st.button(
                _safe_t(t, "re_audit", "Re-audit"),
                key="re_audit_manual_btn_conv",
                use_container_width=True
            ):
                with st.spinner(_safe_t(t, "audit_running", "Running audit...")):
                    new_audit_report = audit_skill(edited_content, skill_name)
                    st.session_state.audit_report = new_audit_report
                    st.session_state.fix_mode_conv = None
                    st.rerun()

        with col_cancel:
            if st.button(
                _safe_t(t, "cancel", "Cancel"),
                key="cancel_manual_edit_btn_conv",
                use_container_width=True
            ):
                st.session_state.fix_mode_conv = None
                st.rerun()
