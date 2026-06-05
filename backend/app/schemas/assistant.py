from pydantic import BaseModel


class AssistantMessage(BaseModel):
    user_id: str
    message: str


class AssistantResponse(BaseModel):
    reply: str
    action: str | None = None
    data: dict | None = None
