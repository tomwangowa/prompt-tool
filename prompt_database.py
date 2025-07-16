#!/usr/bin/env python3
"""
提示詞資料庫管理模組
用於保存和載入優化後的提示詞
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import os

class PromptDatabase:
    """提示詞資料庫管理類"""
    
    def __init__(self, db_path: str = "prompts.db"):
        """初始化資料庫連接"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化資料庫表結構"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                original_prompt TEXT NOT NULL,
                optimized_prompt TEXT NOT NULL,
                analysis_scores TEXT,
                tags TEXT,
                language TEXT DEFAULT 'zh_TW',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_prompt(self, name: str, original_prompt: str, optimized_prompt: str, 
                   analysis_scores: Dict = None, tags: List[str] = None, 
                   language: str = "zh_TW") -> str:
        """保存提示詞"""
        prompt_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prompts 
            (id, name, original_prompt, optimized_prompt, analysis_scores, tags, language, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            prompt_id,
            name,
            original_prompt,
            optimized_prompt,
            json.dumps(analysis_scores) if analysis_scores else None,
            json.dumps(tags) if tags else None,
            language,
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        return prompt_id
    
    def load_prompts(self, limit: int = 50) -> List[Dict]:
        """載入所有保存的提示詞"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, original_prompt, optimized_prompt, analysis_scores, tags, language, created_at
            FROM prompts
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        prompts = []
        for row in rows:
            prompt = {
                'id': row[0],
                'name': row[1],
                'original_prompt': row[2],
                'optimized_prompt': row[3],
                'analysis_scores': json.loads(row[4]) if row[4] else {},
                'tags': json.loads(row[5]) if row[5] else [],
                'language': row[6],
                'created_at': row[7]
            }
            prompts.append(prompt)
        
        return prompts
    
    def load_prompt_by_id(self, prompt_id: str) -> Optional[Dict]:
        """根據ID載入特定提示詞"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, original_prompt, optimized_prompt, analysis_scores, tags, language, created_at
            FROM prompts
            WHERE id = ?
        """, (prompt_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row[0],
            'name': row[1],
            'original_prompt': row[2],
            'optimized_prompt': row[3],
            'analysis_scores': json.loads(row[4]) if row[4] else {},
            'tags': json.loads(row[5]) if row[5] else [],
            'language': row[6],
            'created_at': row[7]
        }
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """刪除提示詞"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def search_prompts(self, query: str, language: str = None) -> List[Dict]:
        """搜索提示詞"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = """
            SELECT id, name, original_prompt, optimized_prompt, analysis_scores, tags, language, created_at
            FROM prompts
            WHERE (name LIKE ? OR original_prompt LIKE ? OR optimized_prompt LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if language:
            sql += " AND language = ?"
            params.append(language)
        
        sql += " ORDER BY updated_at DESC"
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        prompts = []
        for row in rows:
            prompt = {
                'id': row[0],
                'name': row[1],
                'original_prompt': row[2],
                'optimized_prompt': row[3],
                'analysis_scores': json.loads(row[4]) if row[4] else {},
                'tags': json.loads(row[5]) if row[5] else [],
                'language': row[6],
                'created_at': row[7]
            }
            prompts.append(prompt)
        
        return prompts
    
    def get_all_tags(self) -> List[str]:
        """獲取所有標籤"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT tags FROM prompts WHERE tags IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()
        
        all_tags = set()
        for row in rows:
            if row[0]:
                tags = json.loads(row[0])
                all_tags.update(tags)
        
        return sorted(list(all_tags))
    
    def get_prompt_count(self) -> int:
        """獲取提示詞總數"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM prompts")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count