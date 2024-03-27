# chat_models.py
from pydantic import BaseModel, Field
import uuid
from typing import Optional, List, Dict

# Definición del modelo ChatRequest
class ChatRequest(BaseModel):
    courseid: Optional[str] = Field(None, example="80603fc0-1f06-4489-a33a-6494ea9062e3")
    memberid: Optional[str] = Field(None, example="8b013804-faa6-426e-bfcc-43227f58e3c8")
    prompt: Optional[str] = Field(None, example="explicame de que sirven las integrales y diferenciales , con algo super entendible .")
    threadid: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), example="4a37be7f-ce2c-4f19-aaaa-15f6d334a908")
    followup: Optional[List[Dict[str, str]]] = Field(None, example=[{"Answer": "¡Hola! Estoy bien, gracias. ¿Y tú? ¿En qué puedo ayudarte hoy?", "Prompt": "Hola, ¿cómo estás?"}])
    email: Optional[str] = Field(None, example="sebastian@skills.tech")
    organizationid: Optional[str] = Field(None, example="80603fc0-1f06-4489-a33a-6494ea9142e3")
    
