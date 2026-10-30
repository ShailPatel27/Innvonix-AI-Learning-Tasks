from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    department: str = Field(default="", max_length=100)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class GroupCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=300)


class GroupMemberRequest(BaseModel):
    user_id: int = Field(gt=0)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=64)


class ChatMessage(BaseModel):
    role: str
    content: str
    sources: list[dict] = Field(default_factory=list)
