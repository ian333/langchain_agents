# chat_models.py
from pydantic import BaseModel, Field
import uuid
from typing import Optional,List

class ChatRequest(BaseModel):
    text: str = Field(..., example="Hola, ¿cómo estás?")
    courseid: Optional[str] = Field(None, example="ba86e360-577c-4145-baac-974611be0872")
    memberid: Optional[str] = Field(None, example="d6d7b6b9-a530-4fa5-9375-fd6bc54b41f5")
    prompt: Optional[str] = Field(None, example="Explica el concepto de relatividad.")
    threadid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), example=str(uuid.uuid4()))
    followup: Optional[List] = Field(None, example=[{"Answer":"¡Hola! Estoy bien, gracias. ¿Y tú? ¿En qué puedo ayudarte hoy?","Prompt": "Hola, ¿cómo estás?"}])
    email: Optional[str] = Field(None, example="sebastian@skills.tech")
