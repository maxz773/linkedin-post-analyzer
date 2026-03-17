from pydantic import BaseModel, Field, HttpUrl

# Define the structrue of the LLM response
class EvaluationResult(BaseModel):
    score: int = Field(description="Produce a score strictly between 0 and 10")
    reason: str = Field(description="Provide a comprehensive reason for the scoring")

# Define the request schema for FastAPI
class UserRequest(BaseModel):
    post_url: HttpUrl = Field(description="The URL of the LinkedIn post")
    li_at_cookie: str = Field(description="User's LinkedIn li_at cookie for bypassing login")


# Define the response schema for FastAPI
class UserResponse(BaseModel):
    post_score: int = Field(ge=0, le=10)
    comment_score: int = Field(ge=0, le=10)
    ICP_score: int = Field(ge=0, le=10)
    advice: str
