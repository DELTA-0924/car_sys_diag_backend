
from httpx import AsyncClient
import pytest
from src.db.dbConnect import init_db
import asyncio
from src.config import Config
from src.schemas import UserLoginResponse
from src.db.dbConnect import async_engine
from sqlmodel import SQLModel
from jsonschema import validate
from tests.json_schemas import schema_refresh_token ,schema_UserModel
from src.schemas import UserModel


URI = "/api/v1/auth"

header_json={"Content-Type":"application/json"}
@pytest.mark.asyncio
class TestAuth:

    @pytest.mark.asyncio
    async def test_create_user_Account_Success(self,client:AsyncClient,UserData):        

        response = await client.post(URI+"/signup",json = UserData,headers =header_json )

        assert response.status_code == 201,"Регистрация завершилась с ошибкой"
    
    @pytest.mark.asyncio
    async def test_create_user_Account_existing_email(self,client:AsyncClient,get_signup_user,UserData):

        response = await client.post(URI+"/signup",json = UserData,headers = header_json)

        assert response.status_code == 403

        assert response.json()["status_code"]=="user_exists"

    
    @pytest.mark.asyncio
    async def test_create_user_Account_short_password(self,client:AsyncClient,UserData):
        UserData["password"] = "salsa"
        response = await client.post(URI+"/signup",json = UserData,headers =header_json )

        assert response.status_code == 422,"Регистрация завершилась успехом"


    
    @pytest.mark.asyncio
    async def  test_create_user_Account_invalid_email(self,client:AsyncClient,UserData):
        UserData["email"] = "salsamail.com"

        response = await client.post(URI+"/signup",json = UserData,headers =header_json )

        assert response.status_code == 422

        print(response.json())        


    @pytest.mark.asyncio
    async def test_login_users_Success(self,client:AsyncClient,UserLoginData,get_signup_user):    
        response = await client.post(f"{URI}/login",json = UserLoginData,headers = header_json)
        assert response.status_code == 200        
        user = UserLoginResponse.model_validate(response.json())

        assert user.access_token !=None,"Нет токена"
        assert user.refresh_token !=None,"Нет тоенка обновления"

    

    @pytest.mark.asyncio
    async def test_login_users_invalid_credentials(self,client:AsyncClient,UserLoginData,get_signup_user):    
        UserLoginData["password"] = "notsalsa12345"
        response = await client.post(f"{URI}/login",json = UserLoginData,headers = header_json)
        assert response.status_code == 400        

        assert response.json()["status_code"] == "invalid_email_or_password"


    @pytest.mark.asyncio
    async def test_get_new_access_token_Success(self,client:AsyncClient,get_login_user:UserLoginResponse):

        response = await client.get(f"{URI}/refresh_token",headers = {"Authorization":"Bearer "+get_login_user.refresh_token})
        assert response.status_code == 200
        validate(instance = response.json(),schema = schema_refresh_token)

    @pytest.mark.asyncio
    async def test_get_new_access_token_NotRefresh(self,client:AsyncClient,get_login_user:UserLoginResponse):

        response = await client.get(f"{URI}/refresh_token",headers= {"Authorization":"Bearer "+get_login_user.access_token})
        assert response.status_code == 403
        assert response.json()["status_code"] == "refresh_token_required" 
        


    @pytest.mark.asyncio
    async def test_get_current_user_Success(self,client:AsyncClient,get_login_user:UserLoginResponse):

        response  = await client.get(f"{URI}/me",headers = {"Authorization":"Bearer "+get_login_user.access_token})

        assert response.status_code == 200
         
        validate(instance = response.json(),schema = schema_UserModel)
    
    @pytest.mark.asyncio
    async def test_get_current_user_UnAuthorized(self,client:AsyncClient,get_login_user:UserLoginResponse):

        response  = await client.get(f"{URI}/me",headers = {"Authorization":" "+get_login_user.access_token})

        assert response.status_code == 403
                

         

    @pytest.mark.asyncio
    async def test_get_current_user_InvalidToken(self,client:AsyncClient,get_login_user:UserLoginResponse):

        response  = await client.get(f"{URI}/me",headers = {"Authorization":"Bearer "+get_login_user.access_token+"23"})

        assert response.json()["status_code"] == "invalid_token"

        assert response.status_code == 401
         
    
        