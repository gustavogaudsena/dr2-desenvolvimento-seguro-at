from pydantic import BaseModel


class OAuthClient(BaseModel):
    client_id: str
    secret_hash: str
    allowed_scopes: set[str]


class ClientTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scope: str
