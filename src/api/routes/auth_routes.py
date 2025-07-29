import http
from http.client import ACCEPTED
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import USerCreateModel, UserModel, USerLogginModel,UserLoginResponse,UserResponse,EmailModel,ResponseContact
from src.services.user_service import UserService
from src.db.dbConnect import get_session
from src.utils import create_acces_token, verify_password,create_url_safe_token,decode_url_safe_token
from datetime import timedelta,datetime
from fastapi.responses import JSONResponse
from src.dependencies import AccessTokenBearer, RefreshTokenBearer,get_current_user,RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists,UserNotFound,InvalidCredentials,InvalidToken
from src.mail import mail,create_message
from src.config import Config


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin','user'])

REFRESH_TOKEN_EXPIRY = 180


@auth_router.post('/send_email')
async def  send_email(emails:EmailModel):
    emails = emails.addresses

    html = "<h1>Welcome to the app</h1>"

    message = create_message(
        recipients=emails,
        subject = "Welcome",
        body=html
    )

    #await mail.send_message(message)

    result = ResponseContact(status_code=str(status.HTTP_200_OK),detail ='send eamil successfuly')

    return result
@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED
)
async def create_user_Account(
    user_data: USerCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    user_exist = await user_service.user_exist(email, session)

    if user_exist:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)

    token = create_url_safe_token({"email":email})


    link=f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"


    html_message = f"""
    <h1>Verify your email</h1>
    <p>Pleace click this <a href = {link}>link</a> to verify your email</p>
    """

    message = create_message(
        recipients=[email],
        subject = "Verify your email",
        body=html_message
    )

    await mail.send_message(message)

    result = ResponseContact(status_code=str(status.HTTP_200_OK),detail ='User created successfully, please email to verify your account')

    return {"message":result,"user":new_user}


@auth_router.post("/login",response_model = UserLoginResponse,status_code = status.HTTP_200_OK)
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

            response = UserLoginResponse(message = "Login successfull",
                                        access_token =  acces_token,
                                        refresh_token = refresh_token,
                                        user = UserResponse(email = user.email,
                                                            username = user.username,
                                                            uid = user.uid))


            return response
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

@auth_router.get('/me',response_model=UserModel,status_code=200)
async def get_user(
    user = Depends(get_current_user),
    _:bool = Depends(role_checker)
    ): 

    if user is not None:
        return user
    else:
        raise UserNotFound()


@auth_router.get('/verify/{token}')
async def verify_user(token:str,session:AsyncSession =Depends(get_session)):

    token_data =decode_url_safe_token(token)

    user_email = token_data.get('email')

    if user_email:
        user = await user_service.get_user(user_email,session)

        if not user:
            raise UserNotFound()

        await user_service.update_user(user,{"is_verified":True},session)

        result = ResponseContact(status_code=str(status.HTTP_200_OK),detail ="Account verified successfully ")

        return result
    
    result = ResponseContact(status_code = str(status.http.HTTP_500_INTERNAL_SERVER_ERROR),detail = "Error occured during verification")

    return result
    
    