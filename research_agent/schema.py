"""
Schema contract for every app research record.
Every extraction from the LLM must validate against AppRecord.
If it doesn't validate, agent.py retries the extraction (see RETRY logic there).
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import datetime


class Evidence(BaseModel):
    url: str
    snippet: str = Field(..., description="Short quote/paraphrase from the page supporting the claim")


class ApiSurface(BaseModel):
    type: Literal["REST", "GraphQL", "REST+GraphQL", "SDK-only", "none found"]
    breadth: Literal["broad", "moderate", "narrow", "unknown"]
    mcp_exists: bool = False
    mcp_note: Optional[str] = None  # e.g. "official MCP server at help.otter.ai/mcp"


class AppRecord(BaseModel):
    app: str
    category: str
    one_liner: str = Field(..., max_length=200)

    auth_methods: list[Literal["OAuth2", "API key", "Basic", "Token", "None", "Other"]]
    auth_note: Optional[str] = None  # freeform detail, e.g. "OAuth2 + per-request signing"

    self_serve: Literal["self-serve", "gated", "partial"]
    gate_reason: Optional[str] = None  # required if self_serve != "self-serve"

    api_surface: ApiSurface

    verdict: Literal["buildable", "blocked", "partial"]
    blocker: Optional[str] = None  # required if verdict != "buildable"

    evidence: list[Evidence] = Field(..., min_length=1)

    confidence: Literal["high", "medium", "low"]

    # metadata, not from LLM — filled in by agent.py
    pass_number: int = 1
    fetched_at: Optional[str] = None
    model_used: Optional[str] = None
    domain_matched: Optional[bool] = None  # False = source may be a different/unofficial product

    @field_validator("gate_reason")
    @classmethod
    def gate_reason_required_if_gated(cls, v, info):
        self_serve = info.data.get("self_serve")
        if self_serve in ("gated", "partial") and not v:
            raise ValueError("gate_reason required when self_serve is 'gated' or 'partial'")
        return v

    @field_validator("blocker")
    @classmethod
    def blocker_required_if_not_buildable(cls, v, info):
        verdict = info.data.get("verdict")
        if verdict in ("blocked", "partial") and not v:
            raise ValueError("blocker required when verdict is not 'buildable'")
        return v


class VerificationEntry(BaseModel):
    """One row in the human sample-check log."""
    app: str
    field_checked: str  # e.g. "auth_methods", "self_serve", "verdict"
    agent_answer: str
    human_answer: str
    correct: bool
    pass_number: int  # which pass (1 or 2) this check was run against
    reviewer_note: Optional[str] = None
    checked_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


if __name__ == "__main__":
    # smoke test with a realistic example
    example = AppRecord(
        app="Stripe",
        category="Finance and Fintech",
        one_liner="Payments infrastructure API for online businesses",
        auth_methods=["API key"],
        auth_note="Secret key in Authorization header, restricted keys available",
        self_serve="self-serve",
        api_surface=ApiSurface(type="REST", breadth="broad", mcp_exists=True, mcp_note="Official Stripe MCP server"),
        verdict="buildable",
        evidence=[Evidence(url="https://stripe.com/docs/api", snippet="Stripe API uses API keys for authentication")],
        confidence="high",
    )
    print(example.model_dump_json(indent=2))
    print("\nSchema validated OK.")