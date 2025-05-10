from pydantic import BaseModel, Field

class Login(BaseModel):
    username: str = Field(..., example="John Doe")
    password: str = Field(..., example="password123")
