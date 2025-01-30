# External imports
from sqlmodel import SQLModel

class TokenResponse(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenResponse(SQLModel):
    access_token: str
    token_type: str