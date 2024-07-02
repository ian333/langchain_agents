# chat_models.py
from pydantic import BaseModel, Field
import uuid
from typing import Optional, List, Dict

# Definición del modelo ChatRequest
class ChatRequest(BaseModel):
    courseid: Optional[str] = Field(None, example="0ac18238-dae1-465e-87a1-455588e1242b")
    memberid: Optional[str] = Field(None, example="8b013804-faa6-426e-bfcc-43227f58e3c8")
    prompt: Optional[str] = Field(None, example="explicame de que sirven las integrales y diferenciales , con algo super entendible .")
    threadid: Optional[str] = Field(None, example="bc29cced-2f65-441a-8985-c4e70eb3f61c")
    followup: Optional[List[Dict[str, str]]] = Field(None, example=[{"Answer": "¡Hola! Estoy bien, gracias. ¿Y tú? ¿En qué puedo ayudarte hoy?", "Prompt": "Hola, ¿cómo estás?"}])
    email: Optional[str] = Field(None, example="sebastian@skills.tech")
    organizationid: Optional[str] = Field(None, example="6c0bfedb-258a-4c77-9bad-b0e87c0d9c98")
    web: Optional[bool] = Field(False, example=False)



#     {
#   "courseid": "0ac18238-dae1-465e-87a1-455588e1242b",
#   "threadid": "bc29cced-2f65-441a-8985-c4e70eb3f61c",
#   "memberid": "8b013804-faa6-426e-bfcc-43227f58e3c8",
#   "followup": [
#     {
#       "Prompt": "Understanding the project's main objective",
#       "Answer": "**Understanding the Project's Main Objective**\n\nThe Define Phase of Lean Six Sigma focuses on defining the project's main objective, ensuring that it aligns with the strategic goals of the organization. This involves:\n\n* **Establishing SMART Goals:** Setting specific, measurable, achievable, relevant, and time-bound goals.\n* **Identifying Problems:** Identifying specific problems or areas for improvement within the process.\n* **Understanding Team Roles and Functions:** Clarifying the roles and responsibilities of team members involved in the project.\n* **Using SIPOC:** Creating a SIPOC (Suppliers, Inputs, Process, Outputs, Customers) diagram to outline the project's scope and boundaries.\n\nBy defining the project's main objective clearly, the team can focus their efforts on the most critical areas and ensure that the project aligns with the organization's overall objectives."
#     }
#   ],
#   "prompt": "3. How will the project contribute to the organization's mission or strategic objectives?",
#   "email": "sebastian@skills.tech",
#   "organizationid": "6c0bfedb-258a-4c77-9bad-b0e87c0d9c98"
# }

    
class QueryRequest(BaseModel):
    courseid: str
    query_text: str
