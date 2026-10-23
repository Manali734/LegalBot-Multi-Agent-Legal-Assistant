"""Pydantic schemas for LegalBot API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class LegalQuestionRequest(BaseModel):
    """Schema for incoming user legal queries."""
    question: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="The legal inquiry or question to analyze.",
        examples=["Can a landlord withhold a security deposit without providing an itemized list?"]
    )

    @field_validator("question")
    @classmethod
    def validate_question_content(cls, value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) < 5:
            raise ValueError("Question must contain at least 5 non-whitespace characters.")
        return trimmed


class LegalBotResponse(BaseModel):
    """Schema for multi-agent legal guidance response."""
    status: str = Field(default="success", description="Status of the analysis.")
    question: str = Field(..., description="The original question submitted.")
    answer: str = Field(..., description="Synthesized, reviewed legal answer.")
    category: Optional[str] = Field(default=None, description="Identified legal area or domain.")
    sources: List[str] = Field(default_factory=list, description="Legal references or library sources cited.")
    disclaimer: str = Field(..., description="Mandatory legal disclaimer.")


class HealthResponse(BaseModel):
    """Schema for application health check endpoint."""
    status: str = Field(default="healthy")
    app_name: str
    groq_configured: bool
    model: str
    agents: List[str]
