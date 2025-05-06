from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from src.db.models import User
from src.db.redis import add_jti_to_blocklist,token_blocklist,get_token_blocklist
from src.utils import decode_token
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.dbConnect import get_session
from src.services.user_service import UserService;
from typing import List
from .errors import  (
    AccessTokenRequired,
    RefreshTokenRequired,
    InvalidToken,
    RevokedToken,
    InsufficientPermission,
    )
user_service=UserService()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        credis = await super().__call__(request)

        token = credis.credentials

        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        if get_token_blocklist(token_data['jti']):
            raise RevokedToken()


        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token: str):

        token_data = decode_token(token)

        return True if token_data is not None else False

    def verify_token_data(self,token_data):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict)->None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self,token_data:dict)->None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()

async def  get_current_user(
    token_details:dict = Depends(AccessTokenBearer()),
    session:AsyncSession = Depends(get_session)
    ):
    email = token_details['user']['email']
    user = await user_service.get_user(email,session)

    return user if user is not None else None;


class RoleChecker():
    def __init__(self,allowed_roles:List[str])->None:
        self.allowed_roles=allowed_roles

    def __call__(self,current_user :User = Depends(get_current_user))->any:
        if current_user.role in self.allowed_roles:
            return True

        raise InsufficientPermission()
