from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from database.supa import supabase_user, supabase_admin
from typing import List

app = FastAPI()

class PathResponse(BaseModel):
    id: str
    name: str
    topics: List[dict]
    articles: List[dict]
    course: dict

