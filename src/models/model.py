from pydantic import BaseModel
from typing import Dict, Any


class ConversationInputDto(BaseModel):
    input: str

class ConversationOutputDto(BaseModel):
    message: str
    correct_responses: Dict[str, Any]