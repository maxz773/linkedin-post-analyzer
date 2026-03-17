from pydantic import BaseModel, Field, HttpUrl

# Define the structrue of the LLM response
class EvaluationResult(BaseModel):
    score: int = Field(description="Produce a score strictly between 0 and 10")
    reason: str = Field(description="Provide a comprehensive reason for the scoring")

# Define the (URL) request schema for FastAPI
class UserRequest(BaseModel):
    post_url: HttpUrl = Field(description="The URL of the LinkedIn post")
    reference_icp: str = Field(
        default="Director, Chief, or Lead decision maker in Sustainability, AI, Software, or Technology.",
        description="The Ideal Customer Profile description to match commenters against"
    )

# Define the response schema for FastAPI
class UserResponse(BaseModel):
    post_score: int = Field(ge=0, le=10)
    comment_score: int = Field(ge=0, le=10)
    ICP_score: int = Field(ge=0, le=10)
    advice: str
