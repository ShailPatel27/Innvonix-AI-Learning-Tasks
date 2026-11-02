from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


class SupportTicket(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    priority: int = Field(ge=1, le=5)
    email: str
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or "." not in value.rsplit("@", 1)[-1]:
            raise ValueError("Enter a valid email address.")
        return value.lower()

    @model_validator(mode="after")
    def check_urgent_ticket(self):
        if self.priority == 1 and not self.tags:
            raise ValueError("Urgent tickets need at least one tag.")
        return self


if __name__ == "__main__":
    raw_ticket = {
        "title": "Payment failed at checkout",
        "priority": 1,
        "email": "USER@example.com",
        "tags": ["billing"],
    }

    try:
        ticket = SupportTicket.model_validate(raw_ticket)
        print(ticket.model_dump())
    except ValidationError as error:
        print(error)
