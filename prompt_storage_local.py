#!/usr/bin/env python3
"""
Browser LocalStorage-based prompt storage for production mode.
Uses streamlit-local-storage to persist data in user's browser.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st

# Key for storing prompts in LocalStorage
STORAGE_KEY = "prompt_tool_prompts"


class LocalStoragePromptDB:
    """
    LocalStorage-based prompt storage.
    Implements same interface as PromptDatabase for compatibility.
    """

    def __init__(self):
        """Initialize LocalStorage connection"""
        self._init_storage()

    def _init_storage(self):
        """Initialize the storage in session state"""
        if 'local_prompts' not in st.session_state:
            st.session_state.local_prompts = []
            self._load_from_local_storage()

    def _load_from_local_storage(self):
        """Load prompts from browser LocalStorage"""
        try:
            from streamlit_local_storage import LocalStorage
            ls = LocalStorage()
            data = ls.getItem(STORAGE_KEY)

            # 只有在 session_state 中還沒有這個 key 時才載入
            # (表示這是第一次初始化，而非用戶已刪除所有 prompts)
            if 'local_prompts' not in st.session_state:
                if data:
                    parsed = json.loads(data)
                    # 驗證 JSON 資料結構是否為 dict
                    if isinstance(parsed, dict):
                        st.session_state.local_prompts = parsed.get("prompts", [])
                    else:
                        # LocalStorage 資料格式錯誤
                        logging.warning(f"LocalStorage data is not a dict: {type(parsed)}")
                        st.session_state.local_prompts = []
                else:
                    st.session_state.local_prompts = []

            # 如果 key 已存在，我們假設 session_state 是最新的，不進行覆蓋

        except Exception as e:
            # LocalStorage 不可用時，確保 session_state 被初始化
            if 'local_prompts' not in st.session_state:
                st.session_state.local_prompts = []

            # 記錄錯誤以便除錯
            logging.warning(f"Failed to load from LocalStorage: {e}")

    def _save_to_local_storage(self):
        """Save prompts to browser LocalStorage"""
        try:
            from streamlit_local_storage import LocalStorage
            ls = LocalStorage()
            data = {
                "version": "1.0",
                "updated_at": datetime.now().isoformat(),
                "prompts": st.session_state.local_prompts
            }
            ls.setItem(STORAGE_KEY, json.dumps(data, ensure_ascii=False))
        except Exception:
            pass  # Silently fail if LocalStorage not available

    def save_prompt(self, name: str, original_prompt: str, optimized_prompt: str,
                    analysis_scores: Dict = None, tags: List[str] = None,
                    language: str = "zh_TW") -> str:
        """Save a prompt to LocalStorage"""
        prompt_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        prompt = {
            'id': prompt_id,
            'name': name,
            'original_prompt': original_prompt,
            'optimized_prompt': optimized_prompt,
            'analysis_scores': analysis_scores or {},
            'tags': tags or [],
            'language': language,
            'created_at': now,
            'updated_at': now
        }

        st.session_state.local_prompts.insert(0, prompt)
        self._save_to_local_storage()

        return prompt_id

    def load_prompts(self, limit: int = 50) -> List[Dict]:
        """Load all saved prompts"""
        self._load_from_local_storage()
        return st.session_state.local_prompts[:limit]

    def load_prompt_by_id(self, prompt_id: str) -> Optional[Dict]:
        """Load a specific prompt by ID"""
        for prompt in st.session_state.local_prompts:
            if prompt.get('id') == prompt_id:
                return prompt
        return None

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by ID"""
        initial_len = len(st.session_state.local_prompts)
        st.session_state.local_prompts = [
            p for p in st.session_state.local_prompts
            if p.get('id') != prompt_id
        ]

        if len(st.session_state.local_prompts) < initial_len:
            self._save_to_local_storage()
            return True
        return False

    def search_prompts(self, query: str, language: str = None) -> List[Dict]:
        """Search prompts by query"""
        query_lower = query.lower()
        results = []

        for prompt in st.session_state.local_prompts:
            # Search in name, original_prompt, optimized_prompt
            if (query_lower in prompt.get('name', '').lower() or
                query_lower in prompt.get('original_prompt', '').lower() or
                    query_lower in prompt.get('optimized_prompt', '').lower()):

                if language is None or prompt.get('language') == language:
                    results.append(prompt)

        return results

    def get_all_tags(self) -> List[str]:
        """Get all unique tags"""
        all_tags = set()
        for prompt in st.session_state.local_prompts:
            tags = prompt.get('tags', [])
            if tags:
                all_tags.update(tags)
        return sorted(list(all_tags))

    def get_prompt_count(self) -> int:
        """Get total prompt count"""
        return len(st.session_state.local_prompts)

    def export_prompts(self) -> str:
        """Export all prompts to JSON string"""
        # 如果 session_state 尚未初始化，嘗試從 LocalStorage 載入
        # (檢查 key 是否存在，而非列表是否為空，避免已刪除資料復活)
        if 'local_prompts' not in st.session_state:
            self._load_from_local_storage()

        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "prompt_count": len(st.session_state.local_prompts),
            "prompts": st.session_state.local_prompts
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)

    def import_prompts(self, json_data: str, overwrite: bool = False) -> Dict:
        """Import prompts from JSON string"""
        try:
            data = json.loads(json_data)
            prompts = data.get("prompts", [])

            imported = 0
            skipped = 0
            errors = 0

            existing_ids = {p.get('id') for p in st.session_state.local_prompts}

            for prompt in prompts:
                try:
                    prompt_id = prompt.get('id')

                    if prompt_id in existing_ids:
                        if overwrite:
                            # Remove existing and add new
                            st.session_state.local_prompts = [
                                p for p in st.session_state.local_prompts
                                if p.get('id') != prompt_id
                            ]
                            prompt['updated_at'] = datetime.now().isoformat()
                            st.session_state.local_prompts.insert(0, prompt)
                            imported += 1
                        else:
                            skipped += 1
                    else:
                        # Add new prompt
                        if not prompt_id:
                            prompt['id'] = str(uuid.uuid4())
                        st.session_state.local_prompts.insert(0, prompt)
                        imported += 1

                except Exception:
                    errors += 1

            self._save_to_local_storage()

            return {
                "success": True,
                "imported": imported,
                "skipped": skipped,
                "errors": errors,
                "total": len(prompts)
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Invalid JSON format: {str(e)}",
                "imported": 0,
                "skipped": 0,
                "errors": 0
            }
