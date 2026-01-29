# 對話式 Skill 生成流程設計

**日期**: 2026-01-29
**分支**: feature/conversational-skill-flow
**狀態**: 設計已驗證，待實作

## 概覽

將「轉換為 Skill」功能從 modal dialog 改為對話式流程，提升 Advanced 對話模式的用戶體驗。

### 核心目標

1. **保持對話連續性** - 所有交互在主對話區域完成，無彈窗打斷
2. **最小化點擊次數** - 預設一鍵生成，可選編輯
3. **向後兼容** - Simple 模式維持原有 modal dialog
4. **流暢的審查流程** - 審查和修正整合在對話中

## 設計決策

### 決策 1：UI 模式（選項 C）

**混合模式：主對話區 + 可摺疊卡片**

- 結果在主對話區域顯示（保留歷史）
- 使用 `st.expander()` 創建可摺疊卡片
- 編輯表單在同一卡片內展開

### 決策 2：互動次數（選項 A）

**一次互動**

- 預設：使用自動提取的元數據直接生成
- 可選：點擊「編輯」調整參數
- 目標：減少摩擦，提升效率

### 決策 3：模式切換（選項 A）

**基於 conversation_mode**

```python
if st.session_state.conversation_mode == "advanced":
    show_conversational_skill_flow()  # 新的對話式流程
else:
    show_skill_metadata_dialog()      # 傳統 modal dialog
```

### 決策 4：觸發方式（選項 A）

**優化完成後顯示按鈕**

```
助手: ✅ Prompt 優化完成！

      [優化結果...]

      ┌────────────────────────┐
      │ 💡 下一步建議          │
      │ [📋 儲存到資料庫]      │
      │ [🔄 轉換為 Skill]      │  ← NEW
      └────────────────────────┘
```

## 架構設計

### 組件層級

```
convert_prompt_to_skill()
├─ 提取元數據 & 分析複雜度（共用）
├─ 檢查 conversation_mode
│  ├─ "advanced" → show_conversational_skill_flow() [NEW]
│  └─ "simple"   → show_skill_metadata_dialog()     [EXISTING]
```

### 新增函數

#### 1. show_conversational_skill_flow()

```python
def show_conversational_skill_flow(auto_metadata, complexity, optimized_prompt, original_prompt):
    """Show skill generation in conversational flow (advanced mode only)"""

    # 使用 expander 顯示結果
    with st.expander("✅ 技能元數據已提取", expanded=True):
        # 顯示自動提取的資訊
        st.markdown(f"**技能名稱**: `{auto_metadata.skill_name}`")
        st.markdown(f"**描述**: {auto_metadata.description}")
        st.markdown(f"**工具**: {', '.join(auto_metadata.tools)}")

        # 複雜度警告（如果需要）
        if complexity.dependencies:
            st.warning(t("skill_complexity_notice"))

        # 操作按鈕
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✏️ 編輯"):
                st.session_state.show_metadata_form = True
                st.rerun()
        with col2:
            if st.button("🚀 直接生成", type="primary"):
                _generate_skill(auto_metadata, complexity, optimized_prompt)

    # 編輯表單（如果需要）
    if st.session_state.get("show_metadata_form"):
        _show_metadata_edit_form(auto_metadata, complexity, optimized_prompt)
```

#### 2. _show_metadata_edit_form()

```python
def _show_metadata_edit_form(auto_metadata, complexity, optimized_prompt):
    """Show inline metadata edit form"""

    with st.form("edit_metadata_form"):
        st.markdown("### 編輯技能資訊")

        skill_name = st.text_input("技能名稱", value=auto_metadata.skill_name)
        description = st.text_area("描述", value=auto_metadata.description)
        selected_tools = st.multiselect("工具", options=PREDEFINED_TOOLS, default=auto_metadata.tools)
        skill_language = st.selectbox("語言", options=["English", "繁體中文", "日本語"])

        col1, col2 = st.columns(2)
        with col1:
            cancel = st.form_submit_button("取消")
        with col2:
            submit = st.form_submit_button("確認並生成", type="primary")

        if cancel:
            st.session_state.show_metadata_form = False
            st.rerun()

        if submit:
            final_metadata = SkillMetadata(
                skill_name=skill_name,
                description=description,
                tools=selected_tools,
                use_cases=auto_metadata.use_cases
            )
            _generate_skill(final_metadata, complexity, optimized_prompt)
```

#### 3. _generate_skill()

```python
def _generate_skill(metadata, complexity, optimized_prompt):
    """Generate skill with conversational progress display"""

    with st.status("正在生成 Skill...", expanded=True) as status:
        st.write("🔍 正在解析結構...")
        parser = SkillStructureParser(llm)
        structure = parser.parse(optimized_prompt, st.session_state.language)

        st.write("📝 正在生成 Markdown...")
        generator = SkillMarkdownGenerator()
        skill_content = generator.generate(structure, metadata, complexity, skill_language)

        st.write("💾 正在準備下載...")
        handler = SkillFileHandler(dev_mode=False)
        result = handler.save_or_download(skill_content, metadata, complexity)

        status.update(label="✅ Skill 生成成功！", state="complete")

    # 保存到 session state
    st.session_state.skill_gen_result = result
    st.session_state.final_skill_metadata = metadata
    st.session_state.skill_content = skill_content

    st.rerun()  # 顯示結果
```

## UI 流程

### 流程 1: 快速生成（預設路徑）

```
用戶: 優化我的 prompt
助手: ✅ 優化完成！

      [優化結果...]

      💡 下一步建議
      [轉換為 Skill] ← 用戶點擊

助手: 正在分析...

      ┌─ ✅ 技能元數據已提取 ────┐
      │ 名稱: data-analyzer       │
      │ 描述: 資料分析助手...     │
      │ 工具: Read, Bash          │
      │                           │
      │ [✏️ 編輯] [🚀 直接生成]  │ ← 用戶點擊「直接生成」
      └───────────────────────────┘

助手: [st.status 進度顯示]
      🔍 正在解析結構...
      📝 正在生成 Markdown...
      💾 正在準備下載...

助手: ✅ Skill 生成成功！

      [📥 下載 Skill (ZIP)]

      💡 下一步建議
      [🔍 審查品質]
```

### 流程 2: 編輯後生成

```
[從「技能元數據已提取」卡片開始]

      ┌─ ✅ 技能元數據已提取 ────┐
      │ [✏️ 編輯] [🚀 直接生成]  │ ← 用戶點擊「編輯」
      └───────────────────────────┘

      ┌─ 編輯技能資訊 ────────────┐
      │ 技能名稱:                 │
      │ [data-analyzer      ]     │
      │                           │
      │ 描述:                     │
      │ [資料分析助手...    ]     │
      │                           │
      │ 工具: [☑ Read ☑ Bash]    │
      │ 語言: [English ▼]         │
      │                           │
      │ [取消] [確認並生成]       │ ← 用戶點擊
      └───────────────────────────┘

[後續流程同「快速生成」]
```

### 流程 3: 審查和修正

```
[從「Skill 生成成功」開始]

助手: ✅ Skill 生成成功！

      [📥 下載 Skill (ZIP)]

      💡 下一步建議
      [🔍 審查品質] ← 用戶點擊

助手: 正在審查...

      ┌─ 📊 審查結果 ────────────┐
      │ ❌ 審查未通過 - 75/100    │
      │                           │
      │ 發現 2 個問題             │
      │ 🟠 [重要] structure: ...  │
      │    💡 Add '## Overview'   │
      └───────────────────────────┘

      ### 💡 改善建議
      ⚠️ Skill 尚未達標，建議修正

      [🤖 AI 自動修正] [✏️ 手動編輯] ← 用戶點擊

助手: 正在修正 Skill...

助手: ✅ 修正完成！

      [🔍 重新審查] [📥 下載修正版]
```

## 狀態管理

### Session State 變數

```python
# 現有
st.session_state.conversation_mode        # "simple" | "advanced"
st.session_state.skill_gen_result         # 生成結果
st.session_state.final_skill_metadata     # 最終元數據
st.session_state.audit_report             # 審查報告

# 新增
st.session_state.show_metadata_form       # 是否顯示編輯表單
st.session_state.skill_content            # Skill 內容（供審查使用）
st.session_state.fix_mode                 # "ai" | "manual" | None
```

## 兼容性

### Simple 模式（傳統）

- ✅ 完全不受影響
- ✅ 繼續使用 `@st.dialog` modal dialog
- ✅ 所有現有功能保持不變

### Advanced 模式（新）

- ✅ 使用新的對話式流程
- ✅ 所有功能在主對話區域完成
- ✅ 可摺疊卡片保持 UI 整潔

## 實作順序

### Phase 1: 基礎架構
1. 修改 `convert_prompt_to_skill()` 添加模式路由
2. 實作 `show_conversational_skill_flow()` 基本結構
3. 實作元數據顯示和「直接生成」路徑

### Phase 2: 編輯功能
1. 實作 `_show_metadata_edit_form()`
2. 添加取消/確認邏輯
3. 整合表單提交到生成流程

### Phase 3: 生成和結果
1. 實作 `_generate_skill()` 使用 `st.status()`
2. 實作結果顯示（下載按鈕）
3. 添加「下一步建議」區塊

### Phase 4: 審查整合
1. 實作審查結果在對話流程中的顯示
2. 實作 AI 修正和手動編輯按鈕
3. 實作重新審查流程

### Phase 5: 優化觸發
1. 在優化完成後添加「下一步建議」區塊
2. 添加「轉換為 Skill」按鈕
3. 整合到現有優化流程

## 測試計劃

### 功能測試

**Simple 模式（傳統）**:
- [ ] 側邊欄「轉換為 Skill」仍然打開 dialog
- [ ] Dialog 所有功能正常（編輯、生成、審查、修正）
- [ ] 無任何回歸問題

**Advanced 模式（新）**:
- [ ] 優化完成後顯示「轉換為 Skill」按鈕
- [ ] 點擊後顯示元數據卡片
- [ ] 「直接生成」路徑正常工作
- [ ] 「編輯」路徑正常工作
- [ ] 生成進度顯示正確
- [ ] 下載按鈕功能正常
- [ ] 審查功能整合正確
- [ ] AI 修正和手動編輯正常
- [ ] 重新審查功能正常

### UX 測試

- [ ] 對話流程自然流暢
- [ ] 無不必要的 rerun 或閃爍
- [ ] 卡片摺疊/展開平滑
- [ ] 按鈕位置和標籤清晰
- [ ] 錯誤訊息友好

## 風險和緩解

### 風險 1: Session State 衝突

**風險**: 新的 session state 變數可能與現有邏輯衝突

**緩解**:
- 使用明確的命名前綴（如 `conv_skill_*`）
- 在切換模式時清理相關狀態
- 充分測試模式切換

### 風險 2: UI 複雜度增加

**風險**: 對話式流程可能比 dialog 更複雜

**緩解**:
- 使用 expander 保持 UI 整潔
- 提供清晰的視覺層級
- 遵循一致的設計模式

### 風險 3: 向後兼容性

**風險**: 修改可能影響現有 Simple 模式

**緩解**:
- Simple 模式完全不修改現有代碼
- 所有新代碼在獨立函數中
- 充分的回歸測試

## 未來改進

1. **快捷鍵支援**: 允許用戶使用鍵盤快捷鍵觸發
2. **歷史記錄**: 保存最近生成的 skills 供快速存取
3. **批次生成**: 支援一次生成多個相關 skills
4. **預覽模式**: 在生成前預覽 SKILL.md 內容

## 參考資料

- [Streamlit Expander 文檔](https://docs.streamlit.io/library/api-reference/layout/st.expander)
- [Streamlit Status 文檔](https://docs.streamlit.io/library/api-reference/status/st.status)
- [Streamlit Form 文檔](https://docs.streamlit.io/library/api-reference/control-flow/st.form)
- 現有實作: `show_skill_metadata_dialog()` (app.py:596)
