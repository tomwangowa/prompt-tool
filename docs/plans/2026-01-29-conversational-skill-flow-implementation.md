# Conversational Skill Flow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 實作對話式 Skill 生成流程，在 Advanced 模式中提供無彈窗的流暢體驗

**Architecture:**
- 基於 conversation_mode 路由到不同的 UI（dialog vs conversational）
- 使用 st.expander() 和 st.status() 在主對話區域顯示進度和結果
- Simple 模式完全不受影響，維持現有 dialog

**Tech Stack:**
- Streamlit (expander, status, form)
- 現有的 SkillMetadataExtractor, SkillComplexityAnalyzer, SkillMarkdownGenerator

---

## Phase 1: 基礎架構和模式路由

### Task 1.1: 添加模式路由到 convert_prompt_to_skill

**Files:**
- Modify: `app.py:423-449`

**Step 1: 修改 convert_prompt_to_skill 添加路由邏輯**

在 `app.py` 第 449 行（`show_skill_metadata_dialog` 調用之前）修改：

```python
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
```

**Step 2: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors (函數尚未定義，會在下一步添加)

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add conversation mode routing for skill generation

- Route to conversational flow in advanced mode
- Maintain dialog for simple mode
- Extract metadata once, share between flows

Part of: Conversational Skill Flow (#1.1)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 1.2: 創建 show_conversational_skill_flow 基礎結構

**Files:**
- Modify: `app.py` (在 convert_prompt_to_skill 之後添加新函數)

**Step 1: 添加基礎函數框架**

在 `app.py` 第 423 行之前（convert_prompt_to_skill 定義之前）添加：

```python
def show_conversational_skill_flow(auto_metadata, complexity, optimized_prompt, original_prompt):
    """Show skill generation in conversational flow (advanced mode only)"""

    # 使用 expander 顯示結果
    with st.expander("✅ " + t("metadata_extracted"), expanded=True):
        # 顯示自動提取的資訊
        st.markdown(f"**{t('skill_name')}**: `{auto_metadata.skill_name}`")
        st.markdown(f"**{t('skill_description')}**: {auto_metadata.description}")
        st.markdown(f"**{t('skill_tools')}**: {', '.join(auto_metadata.tools)}")

        # 複雜度警告（如果需要）
        if complexity.dependencies and (complexity.dependencies.needs_mcp or
                                       complexity.dependencies.needs_scripts or
                                       complexity.dependencies.needs_sub_skills):
            st.warning(t("skill_complexity_notice"))

            if complexity.dependencies.needs_mcp:
                st.markdown(f"**{t('mcp_tools_label')}**: {', '.join(complexity.dependencies.mcp_tools)}")
            if complexity.dependencies.needs_scripts:
                st.markdown(f"**{t('scripts_label')}**: {', '.join(complexity.dependencies.script_types)}")
            if complexity.dependencies.needs_sub_skills:
                st.markdown(f"**{t('sub_skills_label')}**: {len(complexity.dependencies.sub_skill_steps)} steps")

        # 操作按鈕（暫時只有直接生成）
        col1, col2 = st.columns(2)
        with col1:
            # 編輯按鈕（稍後實作）
            st.button("✏️ " + t("edit"), key="edit_metadata_btn_conv", disabled=True, use_container_width=True)

        with col2:
            if st.button("🚀 " + t("generate_directly"), key="generate_directly_btn",
                        type="primary", use_container_width=True):
                # 暫時顯示訊息（實際生成邏輯稍後添加）
                st.info("生成功能將在 Task 1.3 實作")
```

**Step 2: 添加翻譯字串**

在 `app.py` 的 translations 字典中添加（約第 100-150 行）：

```python
# 中文
"metadata_extracted": "技能元數據已提取",
"generate_directly": "直接生成",
"edit": "編輯",

# 英文（約第 250-300 行）
"metadata_extracted": "Skill Metadata Extracted",
"generate_directly": "Generate Directly",
"edit": "Edit",

# 日文（約第 400-450 行）
"metadata_extracted": "スキルメタデータが抽出されました",
"generate_directly": "直接生成",
"edit": "編集",
```

**Step 3: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 4: 測試基礎 UI**

Run: `streamlit run app.py`
Actions:
1. 切換到 Advanced 模式
2. 優化一個 prompt
3. 點擊側邊欄的「轉換為 Skill」
4. 確認看到 expander 卡片顯示元數據
5. 確認「編輯」按鈕是灰色（disabled）
6. 點擊「直接生成」確認顯示提示訊息

Expected: UI 正常顯示，無錯誤

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add conversational skill flow basic structure

- Add show_conversational_skill_flow() function
- Display metadata in expander
- Add translation strings
- Placeholder buttons (edit disabled, generate shows info)

Part of: Conversational Skill Flow (#1.2)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 1.3: 實作直接生成路徑

**Files:**
- Modify: `app.py` (添加 _generate_skill_conversational 函數)

**Step 1: 添加生成函數**

在 `show_conversational_skill_flow` 之前添加輔助函數：

```python
def _generate_skill_conversational(metadata, complexity, optimized_prompt, skill_language="en"):
    """Generate skill with conversational progress display"""

    with st.status(t("generating_skill"), expanded=True) as status:
        llm = create_llm()

        st.write("🔍 " + t("parsing_structure"))
        parser = SkillStructureParser(llm)
        structure = parser.parse(optimized_prompt, st.session_state.language)

        st.write("📝 " + t("generating_markdown"))
        generator = SkillMarkdownGenerator()
        skill_content = generator.generate(structure, metadata, complexity, skill_language)

        st.write("💾 " + t("saving_skill"))
        handler = SkillFileHandler(dev_mode=st.session_state.get("dev_mode", False))
        result = handler.save_or_download(skill_content, metadata, complexity)

        status.update(label="✅ " + t("skill_generated_success"), state="complete")

    # 保存到 session state
    st.session_state.skill_gen_result = result
    st.session_state.final_skill_metadata = metadata
    st.session_state.skill_content = skill_content
    st.session_state.skill_complexity = complexity
```

**Step 2: 更新 show_conversational_skill_flow 使用生成函數**

修改「直接生成」按鈕的邏輯：

```python
        with col2:
            if st.button("🚀 " + t("generate_directly"), key="generate_directly_btn",
                        type="primary", use_container_width=True):
                # 使用預設語言代碼
                lang_map = {"zh_TW": "zh_TW", "en": "en", "ja": "ja"}
                skill_lang = lang_map.get(st.session_state.language, "en")

                _generate_skill_conversational(auto_metadata, complexity, optimized_prompt, skill_lang)
                st.rerun()
```

**Step 3: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 4: 測試生成功能**

Run: `streamlit run app.py`
Actions:
1. Advanced 模式
2. 優化 prompt
3. 轉換為 Skill
4. 點擊「直接生成」
5. 觀察 st.status 進度顯示
6. 確認生成完成

Expected:
- 顯示進度（解析、生成、保存）
- 生成完成後 session state 包含結果
- 頁面重新載入

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat: implement direct generation path

- Add _generate_skill_conversational() with st.status progress
- Connect generate button to actual generation logic
- Save results to session state for download display

Part of: Conversational Skill Flow (#1.3)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 2: 結果顯示和下載

### Task 2.1: 顯示生成結果和下載按鈕

**Files:**
- Modify: `app.py:show_conversational_skill_flow`

**Step 1: 添加結果顯示邏輯**

在 `show_conversational_skill_flow` 函數的 expander 之後添加：

```python
def show_conversational_skill_flow(auto_metadata, complexity, optimized_prompt, original_prompt):
    """Show skill generation in conversational flow (advanced mode only)"""

    # [現有的 expander 代碼保持不變]

    # 顯示生成結果（如果存在）
    if st.session_state.get("skill_gen_result"):
        result = st.session_state.skill_gen_result
        metadata = st.session_state.final_skill_metadata
        complexity = st.session_state.get("skill_complexity", complexity)

        st.success("✅ " + t("skill_generated_success"))
        st.markdown("---")

        # 下載按鈕
        if result.get("download_data"):
            skill_name = metadata.skill_name

            # 判斷是 ZIP 還是單一 SKILL.md
            if complexity.dependencies and (complexity.dependencies.needs_mcp or
                                           complexity.dependencies.needs_scripts or
                                           complexity.dependencies.needs_sub_skills):
                filename = f"{skill_name}.zip"
                mime_type = "application/zip"
                label = f"📦 {t('download_skill')} (ZIP)"
            else:
                filename = "SKILL.md"
                mime_type = "text/markdown"
                label = f"📄 {t('download_skill')} (SKILL.md)"

            st.download_button(
                label=label,
                data=result["download_data"],
                file_name=filename,
                mime=mime_type,
                key="skill_download_btn_conv",
                use_container_width=True,
                type="primary"
            )
```

**Step 2: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 3: 測試下載功能**

Run: `streamlit run app.py`
Actions:
1. 生成一個 skill
2. 確認看到成功訊息
3. 確認看到下載按鈕
4. 點擊下載按鈕
5. 驗證檔案下載

Expected:
- 成功訊息顯示
- 下載按鈕可見
- 點擊後下載 ZIP 或 SKILL.md

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add result display and download button

- Show success message after generation
- Display download button with correct file type
- Support both ZIP and SKILL.md downloads

Part of: Conversational Skill Flow (#2.1)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2.2: 添加審查建議

**Files:**
- Modify: `app.py:show_conversational_skill_flow`

**Step 1: 在下載按鈕後添加審查選項**

在下載按鈕代碼之後添加：

```python
        # 審查建議
        st.markdown("---")
        st.markdown(f"### 💡 {t('next_steps')}")

        if st.button("🔍 " + t("audit_skill"), key="audit_skill_btn_conv", use_container_width=True):
            with st.spinner(t("audit_running")):
                from skill_auditor import audit_skill
                audit_report = audit_skill(
                    st.session_state.skill_content,
                    metadata.skill_name
                )
                st.session_state.audit_report = audit_report
                st.rerun()
```

**Step 2: 添加翻譯**

```python
# 中文
"next_steps": "下一步建議",

# 英文
"next_steps": "Next Steps",

# 日文
"next_steps": "次のステップ",
```

**Step 3: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 4: 測試審查按鈕**

Run: `streamlit run app.py`
Actions:
1. 生成 skill
2. 確認看到「下一步建議」區塊
3. 點擊「審查 Skill」
4. 確認審查執行

Expected: 審查功能正常執行

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add audit suggestion after generation

- Add 'Next Steps' section
- Add audit button
- Integrate with existing skill_auditor

Part of: Conversational Skill Flow (#2.2)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 3: 編輯功能

### Task 3.1: 實作編輯表單

**Files:**
- Modify: `app.py` (添加 _show_metadata_edit_form_conversational)

**Step 1: 添加編輯表單函數**

在 `_generate_skill_conversational` 之前添加：

```python
def _show_metadata_edit_form_conversational(auto_metadata, complexity, optimized_prompt):
    """Show inline metadata edit form in conversational flow"""

    with st.form("edit_metadata_form_conv"):
        st.markdown(f"### {t('edit_skill_metadata')}")

        # 表單欄位
        skill_name = st.text_input(
            t("skill_name"),
            value=auto_metadata.skill_name,
            help=t("skill_name_help")
        )

        description = st.text_area(
            t("skill_description"),
            value=auto_metadata.description,
            height=100
        )

        selected_tools = st.multiselect(
            t("skill_tools"),
            options=PREDEFINED_TOOLS,
            default=auto_metadata.tools
        )

        skill_language = st.selectbox(
            t("skill_language"),
            options=["English", "繁體中文", "日本語"],
            index=0,
            help=t("skill_language_help")
        )

        # 表單按鈕
        col1, col2 = st.columns(2)
        with col1:
            cancel = st.form_submit_button(t("cancel"), use_container_width=True)
        with col2:
            submit = st.form_submit_button(t("confirm_and_generate"),
                                          type="primary",
                                          use_container_width=True)

        if cancel:
            st.session_state.show_metadata_form_conv = False
            st.rerun()

        if submit:
            # 創建更新後的 metadata
            from skill_generator import SkillMetadata
            final_metadata = SkillMetadata(
                skill_name=skill_name,
                description=description,
                tools=selected_tools,
                use_cases=auto_metadata.use_cases
            )

            # 語言映射
            lang_map = {"English": "en", "繁體中文": "zh_TW", "日本語": "ja"}
            skill_lang = lang_map[skill_language]

            # 生成 skill
            st.session_state.show_metadata_form_conv = False
            _generate_skill_conversational(final_metadata, complexity, optimized_prompt, skill_lang)
            st.rerun()
```

**Step 2: 添加翻譯**

```python
# 中文
"edit_skill_metadata": "編輯技能資訊",
"confirm_and_generate": "確認並生成",

# 英文
"edit_skill_metadata": "Edit Skill Metadata",
"confirm_and_generate": "Confirm and Generate",

# 日文
"edit_skill_metadata": "スキルメタデータを編集",
"confirm_and_generate": "確認して生成",
```

**Step 3: 更新 show_conversational_skill_flow**

修改編輯按鈕邏輯：

```python
        with col1:
            if st.button("✏️ " + t("edit"), key="edit_metadata_btn_conv", use_container_width=True):
                st.session_state.show_metadata_form_conv = True
                st.rerun()
```

並在 expander 之後添加：

```python
    # 顯示編輯表單（如果需要）
    if st.session_state.get("show_metadata_form_conv", False):
        _show_metadata_edit_form_conversational(auto_metadata, complexity, optimized_prompt)
```

**Step 4: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 5: 測試編輯流程**

Run: `streamlit run app.py`
Actions:
1. 轉換為 Skill
2. 點擊「編輯」
3. 確認表單顯示
4. 修改資訊
5. 點擊「確認並生成」
6. 驗證使用修改後的資訊生成

Expected: 編輯流程正常工作

**Step 6: Commit**

```bash
git add app.py
git commit -m "feat: implement metadata edit form

- Add _show_metadata_edit_form_conversational()
- Enable edit button in conversational flow
- Support form submission and cancellation
- Use edited metadata for generation

Part of: Conversational Skill Flow (#3.1)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 4: 審查結果顯示

### Task 4.1: 顯示審查結果

**Files:**
- Modify: `app.py:show_conversational_skill_flow`

**Step 1: 添加審查結果顯示**

在審查按鈕代碼之後添加：

```python
        # 顯示審查結果（如果存在）
        if st.session_state.get("audit_report"):
            audit_report = st.session_state.audit_report

            with st.expander("📊 " + t("audit_results"), expanded=True):
                # 分數和狀態
                if audit_report.passed:
                    st.success(f"✅ {t('audit_passed')} - {t('audit_score')}: {audit_report.score}/100")
                else:
                    st.error(f"❌ {t('audit_failed')} - {t('audit_score')}: {audit_report.score}/100")

                st.markdown(f"**{audit_report.summary}**")

                # 問題列表
                if audit_report.issues:
                    st.markdown(f"### {t('found_issues')}: {len(audit_report.issues)}")

                    for issue in audit_report.issues:
                        severity_icons = {
                            "critical": "🔴",
                            "high": "🟠",
                            "medium": "🟡",
                            "low": "🔵"
                        }
                        icon = severity_icons.get(issue.severity, "⚪")
                        severity_text = t(f"severity_{issue.severity}")

                        st.markdown(f"{icon} **[{severity_text}] {issue.category}**: {issue.message}")
                        if issue.suggestion:
                            st.info(f"💡 {issue.suggestion}")
                        st.markdown("---")
                else:
                    st.success(t("audit_no_issues"))
```

**Step 2: 添加翻譯**

```python
# 中文
"audit_results": "審查結果",
"found_issues": "發現問題",

# 英文
"audit_results": "Audit Results",
"found_issues": "Found Issues",

# 日文
"audit_results": "監査結果",
"found_issues": "発見された問題",
```

**Step 3: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 4: 測試審查結果顯示**

Run: `streamlit run app.py`
Actions:
1. 生成 skill
2. 點擊審查
3. 確認結果顯示在 expander 中
4. 檢查問題列表格式

Expected: 審查結果清晰顯示

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat: display audit results in conversational flow

- Show audit results in expander
- Display score and issues
- Use severity icons and translations
- Maintain conversational context

Part of: Conversational Skill Flow (#4.1)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4.2: 添加修正選項

**Files:**
- Modify: `app.py:show_conversational_skill_flow`

**Step 1: 在審查結果後添加修正按鈕**

在審查結果 expander 之後添加：

```python
                # 修正選項（如果有問題）
                if audit_report.issues:
                    st.markdown("---")
                    st.markdown(f"### 💡 {t('improvement_suggestions')}")

                    # 根據是否通過顯示不同訊息
                    if not audit_report.passed:
                        st.warning("⚠️ " + t("skill_needs_improvement"))
                    else:
                        st.info("✨ " + t("skill_can_be_optimized"))

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🤖 " + t("ai_fix"),
                                   key="ai_fix_btn_conv",
                                   use_container_width=True,
                                   type="primary"):
                            st.session_state.fix_mode_conv = "ai"
                            st.rerun()

                    with col2:
                        if st.button("✏️ " + t("manual_edit"),
                                   key="manual_edit_btn_conv",
                                   use_container_width=True):
                            st.session_state.fix_mode_conv = "manual"
                            st.rerun()
```

**Step 2: 添加翻譯**

```python
# 中文
"improvement_suggestions": "改善建議",
"skill_needs_improvement": "Skill 尚未達標，建議修正後再使用",
"skill_can_be_optimized": "Skill 已可用，但可以進一步優化",

# 英文
"improvement_suggestions": "Improvement Suggestions",
"skill_needs_improvement": "Skill needs improvement before use",
"skill_can_be_optimized": "Skill is usable but can be optimized",

# 日文
"improvement_suggestions": "改善提案",
"skill_needs_improvement": "Skillは使用前に改善が必要です",
"skill_can_be_optimized": "Skillは使用可能ですが、最適化できます",
```

**Step 3: 添加修正處理邏輯（暫時顯示訊息）**

在修正按鈕之後添加：

```python
                # AI 修正流程（暫時）
                if st.session_state.get("fix_mode_conv") == "ai":
                    with st.spinner(t("fixing_skill")):
                        st.info("AI 修正功能將在後續完善")
                        st.session_state.fix_mode_conv = None

                # 手動編輯流程（暫時）
                if st.session_state.get("fix_mode_conv") == "manual":
                    st.info("手動編輯功能將在後續完善")
                    st.session_state.fix_mode_conv = None
```

**Step 4: 驗證語法**

Run: `python -m py_compile app.py`
Expected: No errors

**Step 5: 測試修正按鈕**

Run: `streamlit run app.py`
Actions:
1. 生成有問題的 skill
2. 審查
3. 確認看到修正建議
4. 點擊 AI 修正/手動編輯
5. 確認顯示提示訊息

Expected: 按鈕正常顯示，點擊後顯示提示

**Step 6: Commit**

```bash
git add app.py
git commit -m "feat: add fix options for audit issues

- Show improvement suggestions after audit
- Add AI fix and manual edit buttons
- Display different messages for failed vs passed
- Placeholder for fix workflows

Part of: Conversational Skill Flow (#4.2)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 5: 優化觸發整合

### Task 5.1: 在優化完成後添加轉換按鈕

**Files:**
- Modify: `app.py` (找到顯示優化結果的位置)

**Step 1: 找到優化結果顯示位置**

Run: `grep -n "optimization_result" app.py | head -20`
Expected: 找到顯示優化結果的代碼位置

**Step 2: 在優化結果後添加建議區塊**

在顯示優化 prompt 的代碼之後添加：

```python
        # 在優化結果顯示之後
        st.markdown("---")
        st.markdown(f"### 💡 {t('next_steps')}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 " + t("save_to_database"),
                        key="save_optimized_prompt",
                        use_container_width=True):
                # 現有的儲存邏輯
                pass

        with col2:
            if st.button("🔄 " + t("convert_to_skill"),
                        key="convert_optimized_to_skill",
                        use_container_width=True,
                        type="primary"):
                # 觸發轉換
                convert_prompt_to_skill(
                    optimized_prompt=st.session_state.optimization_result,
                    original_prompt=st.session_state.initial_prompt
                )
```

**Step 3: 添加翻譯**

```python
# 中文
"convert_to_skill": "轉換為 Skill",
"save_to_database": "儲存到資料庫",

# 英文
"convert_to_skill": "Convert to Skill",
"save_to_database": "Save to Database",

# 日文
"convert_to_skill": "Skillに変換",
"save_to_database": "データベースに保存",
```

**Step 4: 測試完整流程**

Run: `streamlit run app.py`
Actions:
1. Advanced 模式
2. 優化一個 prompt
3. 確認看到「下一步建議」
4. 點擊「轉換為 Skill」
5. 驗證觸發對話式流程

Expected: 完整流程順暢

**Step 5: Commit**

```bash
git add app.py
git commit -m "feat: add convert to skill button after optimization

- Add 'Next Steps' section after optimization
- Add convert to skill button
- Integrate with conversational flow
- Complete the trigger flow

Part of: Conversational Skill Flow (#5.1)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## Phase 6: 清理和測試

### Task 6.1: 清理 session state

**Files:**
- Modify: `app.py`

**Step 1: 添加清理邏輯**

在 `show_conversational_skill_flow` 開始處添加：

```python
def show_conversational_skill_flow(auto_metadata, complexity, optimized_prompt, original_prompt):
    """Show skill generation in conversational flow (advanced mode only)"""

    # 清理按鈕（在結果顯示後）
    if st.session_state.get("skill_gen_result"):
        if st.button("🔄 " + t("start_new_skill"), key="reset_skill_flow_conv"):
            # 清理所有相關 state
            for key in ["skill_gen_result", "final_skill_metadata", "skill_content",
                       "skill_complexity", "audit_report", "show_metadata_form_conv",
                       "fix_mode_conv"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
```

**Step 2: 添加翻譯**

```python
# 中文
"start_new_skill": "開始新的 Skill",

# 英文
"start_new_skill": "Start New Skill",

# 日文
"start_new_skill": "新しいSkillを開始",
```

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add session state cleanup

- Add reset button for new skill generation
- Clean all conversational flow states
- Improve state management

Part of: Conversational Skill Flow (#6.1)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6.2: 完整功能測試

**Step 1: 測試 Simple 模式（向後兼容）**

Run: `streamlit run app.py`
Test Cases:
- [ ] Simple 模式下側邊欄「轉換為 Skill」打開 dialog
- [ ] Dialog 所有功能正常（編輯、生成、審查）
- [ ] 無回歸問題

**Step 2: 測試 Advanced 模式（新功能）**

Test Cases:
- [ ] 優化後顯示「轉換為 Skill」按鈕
- [ ] 點擊後顯示對話式流程
- [ ] 元數據卡片正確顯示
- [ ] 「直接生成」正常工作
- [ ] 「編輯」→ 修改 → 生成流程正常
- [ ] 生成進度顯示（st.status）
- [ ] 下載按鈕正常工作
- [ ] 審查按鈕正常工作
- [ ] 審查結果正確顯示
- [ ] 修正選項正確顯示
- [ ] 重置按鈕清理狀態

**Step 3: 文檔更新**

```bash
# 更新 CLAUDE.md
```

在 CLAUDE.md 的 "Key Features" 部分添加：

```markdown
- **對話式 Skill 生成** (Advanced mode): 在主對話區域完成整個流程，無彈窗打斷
  - 一鍵生成或可選編輯
  - 實時進度顯示
  - 整合審查和修正
  - Simple mode 維持傳統 dialog
```

**Step 4: 最終 Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with conversational skill flow

- Document new conversational flow feature
- Clarify mode differences
- Update feature list

Part of: Conversational Skill Flow (#6.2)

Co-Authored-By: Claude Sonnet 4.5 (1M context) <noreply@anthropic.com>"
```

---

## 驗收標準

### 功能完整性
- [x] Advanced 模式使用對話式流程
- [x] Simple 模式維持 dialog（無回歸）
- [x] 優化後顯示轉換按鈕
- [x] 元數據顯示和編輯
- [x] 生成進度顯示
- [x] 下載功能正常
- [x] 審查整合正常
- [x] 修正選項顯示

### 代碼質量
- [ ] 所有函數有適當註釋
- [ ] 無重複代碼
- [ ] 語法驗證通過
- [ ] 翻譯完整（中英日）

### 用戶體驗
- [ ] 對話流程流暢
- [ ] 無不必要的 rerun
- [ ] 按鈕標籤清晰
- [ ] 錯誤訊息友好

---

## 估計時間

- **Phase 1**: 30 分鐘（路由 + 基礎結構 + 直接生成）
- **Phase 2**: 20 分鐘（結果顯示 + 審查建議）
- **Phase 3**: 15 分鐘（編輯功能）
- **Phase 4**: 25 分鐘（審查結果 + 修正選項）
- **Phase 5**: 15 分鐘（優化觸發）
- **Phase 6**: 15 分鐘（清理 + 測試）

**總計**: 約 2 小時
