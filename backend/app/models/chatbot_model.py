from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    response: str

class HistoryResponse(BaseModel):
    user_id: str
    message_count: int
    history: list

class SummaryResponse(BaseModel):
    user_id: str
    summary: str
    message_count: int
    total_conversations: Optional[int] = None
    generated_at: Optional[str] = None
    auto_generated: Optional[bool] = None

class TranscriptResponse(BaseModel):
    transcript: str
    text: str
    confidence: float
    latency_ms: int
    api_latency_ms: Optional[int] = None
    audio_duration_s: Optional[float] = None
    model_used: Optional[str] = None
    error: Optional[str] = None