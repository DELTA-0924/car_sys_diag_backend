import http
from http.client import ACCEPTED
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import USerCreateModel, UserModel, USerLogginModel, UserProductsModel
from src.services.user_service import UserService
from src.db.dbConnect import get_session
from src.utils import create_acces_token, verify_password
from datetime import timedelta,datetime
from fastapi.responses import JSONResponse
from src.dependencies import AccessTokenBearer, RefreshTokenBearer,get_current_user,RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists,UserNotFound,InvalidCredentials,InvalidToken
auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin','user'])

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post(
    "/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED
)
async def create_user_Account(
    user_data: USerCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exist = await user_service.user_exist(email, session)

    if user_exist:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    return new_user


@auth_router.post("/login")
async def login_users(
    login_data: USerLogginModel, session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password

    user = await user_service.get_user(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            acces_token = create_acces_token(
                user_data={"email": user.email, "user_uid": str(user.uid)}
            )

            refresh_token = create_acces_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login succcesful ",
                    "acces_token": acces_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )
    raise InvalidCredentials()


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details:dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp)>datetime.now():
        new_access_token = create_acces_token(user_data=token_details['user'])
        
        return JSONResponse(content={"access_token":new_access_token})

    raise InvalidToken()


@auth_router.get('/logout')
async def revoke_token(token_details:dict = Depends(AccessTokenBearer())):

    jti=token_details['jti']

    add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message":"Logoged Out Succesfully"
            },
        status_code=status.HTTP_200_OK
        )

@auth_router.get('/me',response_model=UserModel)
async def get_current_user(
    user = Depends(get_current_user),
    _:bool = Depends(role_checker)
    ): 

    if user is not None:
        return user
    else:
        raise UserNotFound()

