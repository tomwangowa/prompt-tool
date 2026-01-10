#!/usr/bin/env python3
"""
對話類型定義模組
定義對話式 UI 所需的資料結構和類型
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid


class MessageRole(Enum):
    """訊息角色定義"""
    USER = "user"           # 用戶輸入
    ASSISTANT = "assistant" # AI 回應
    SYSTEM = "system"       # 系統通知


class MessageType(Enum):
    """訊息類型定義"""
    TEXT = "text"                    # 純文字訊息
    ANALYSIS = "analysis"            # 分析結果
    QUESTIONS = "questions"          # 改進問題組
    OPTIMIZATION = "optimization"    # 優化結果
    SYSTEM_NOTICE = "system_notice"  # 系統通知


@dataclass
class Message:
    """對話訊息結構"""
    id: str                          # 唯一識別碼
    role: MessageRole                # 訊息角色
    type: MessageType                # 訊息類型
    content: str                     # 主要內容
    timestamp: datetime              # 時間戳記
    metadata: Dict[str, Any] = field(default_factory=dict)  # 額外數據

    # 特定類型的額外數據
    analysis_data: Optional[Dict] = None      # 分析結果詳細數據
    questions_data: Optional[List[Dict]] = None  # 問題列表
    optimization_data: Optional[Dict] = None   # 優化結果數據
    parent_message_id: Optional[str] = None    # 父訊息 ID (用於追蹤對話鏈)

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式（用於序列化）"""
        return {
            "id": self.id,
            "role": self.role.value,
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "analysis_data": self.analysis_data,
            "questions_data": self.questions_data,
            "optimization_data": self.optimization_data,
            "parent_message_id": self.parent_message_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """從字典創建訊息（用於反序列化）"""
        try:
            return cls(
                id=data.get("id", str(uuid.uuid4())),  # 防止 id 遺失
                role=MessageRole(data["role"]),  # 必要欄位
                type=MessageType(data["type"]),  # 必要欄位
                content=data.get("content", ""),
                timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
                metadata=data.get("metadata", {}),
                analysis_data=data.get("analysis_data"),
                questions_data=data.get("questions_data"),
                optimization_data=data.get("optimization_data"),
                parent_message_id=data.get("parent_message_id")
            )
        except (KeyError, ValueError) as e:
            # 記錄錯誤並拋出自定義異常
            raise ValueError(f"Invalid message data format: {e}") from e


@dataclass
class ConversationSession:
    """完整的對話會話"""
    session_id: str                  # 會話 ID
    messages: List[Message]          # 訊息列表
    current_prompt: str              # 當前處理的 prompt
    original_prompt: str             # 最初的 prompt
    iteration_count: int = 0         # 迭代次數
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # 狀態追蹤
    last_analysis: Optional[Dict] = None
    last_optimization: Optional[Dict] = None
    pending_questions: Optional[List[Dict]] = None
    question_answers: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: MessageRole, msg_type: MessageType,
                    content: str, **kwargs) -> Message:
        """添加新訊息到會話"""
        msg = Message(
            id=str(uuid.uuid4()),
            role=role,
            type=msg_type,
            content=content,
            timestamp=datetime.now(),
            **kwargs
        )
        self.messages.append(msg)
        self.updated_at = datetime.now()
        return msg

    def get_messages_by_type(self, msg_type: MessageType) -> List[Message]:
        """獲取特定類型的所有訊息"""
        return [msg for msg in self.messages if msg.type == msg_type]

    def get_last_message(self) -> Optional[Message]:
        """獲取最後一條訊息"""
        return self.messages[-1] if self.messages else None

    def clear_messages(self):
        """清空訊息歷史"""
        self.messages = []

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "current_prompt": self.current_prompt,
            "original_prompt": self.original_prompt,
            "iteration_count": self.iteration_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_analysis": self.last_analysis,
            "last_optimization": self.last_optimization,
            "pending_questions": self.pending_questions,
            "question_answers": self.question_answers
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSession":
        """從字典創建會話"""
        try:
            return cls(
                session_id=data.get("session_id", str(uuid.uuid4())),
                messages=[Message.from_dict(m) for m in data.get("messages", [])],
                current_prompt=data.get("current_prompt", ""),
                original_prompt=data.get("original_prompt", ""),
                iteration_count=data.get("iteration_count", 0),
                created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
                updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(),
                last_analysis=data.get("last_analysis"),
                last_optimization=data.get("last_optimization"),
                pending_questions=data.get("pending_questions"),
                question_answers=data.get("question_answers", {})
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid conversation session data format: {e}") from e


class ConversationState(Enum):
    """對話狀態"""
    IDLE = "idle"                      # 空閒，等待用戶輸入
    ANALYZING = "analyzing"            # 正在分析
    AWAITING_QUESTIONS = "awaiting_questions"  # 等待用戶回答改進問題
    OPTIMIZING = "optimizing"          # 正在優化
    COMPLETED = "completed"            # 本輪優化完成
    CONVERSING = "conversing"          # 持續對話中


def create_new_session(initial_prompt: str = "") -> ConversationSession:
    """創建新的對話會話"""
    return ConversationSession(
        session_id=str(uuid.uuid4()),
        messages=[],
        current_prompt=initial_prompt,
        original_prompt=initial_prompt,
        iteration_count=0
    )
