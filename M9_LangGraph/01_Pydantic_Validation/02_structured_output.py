import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model


class MeetingSummary(BaseModel):
    title: str = Field(description="A short meeting title")
    decisions: list[str] = Field(description="Decisions made in the meeting")
    action_items: list[str] = Field(description="Tasks assigned to participants")
    sentiment: Literal["positive", "neutral", "negative"]


if __name__ == "__main__":
    model = get_chat_model().with_structured_output(MeetingSummary)
    result = model.invoke(
        "The team agreed to ship the search update Friday. Priya owns the rollout checklist. "
        "The discussion was constructive. Summarize the meeting."
    )
    print(result.model_dump_json(indent=2))
