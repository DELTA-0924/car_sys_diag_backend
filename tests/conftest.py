import pytest;
import asyncio
from httpx import AsyncClient,ASGITransport
from src.main import app 
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from src.main import app
from src.db.dbConnect import get_session
from httpx import AsyncClient
from src.config import Config
from tests.Data import dataUser,dataUserLogin
from src.db.dbConnect import async_engine
from src.schemas import UserLoginResponse
from src.main import redis_path
import subprocess
@pytest.fixture(scope = "session",autouse = True)
def set_up_redis():
        a = subprocess.Popen(redis_path)
        yield 
        a.terminate()


@pytest.fixture(autouse=True)
async def setup_db():

    async with async_engine.begin() as conn:
        from src.db.models import Car
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await async_engine.dispose()
@pytest.fixture(scope = "session")
async def client():


    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture()
def UserData():
    yield dataUser[0].copy()

@pytest.fixture()
def UserLoginData():
    yield dataUserLogin[0].copy()

@pytest.fixture()
async def get_signup_user(client:AsyncClient,UserData):    
    response = await client.post("/api/v1/auth/signup",json = UserData,headers = {"Content-Type":"application/json"})
    assert response.status_code == 201    
    yield
@pytest.fixture()
async def get_login_user(client,get_signup_user,UserLoginData):
    response = await client.post("/api/v1/auth/login",json = UserLoginData,headers = {"Content-Type":"application/json"})
    assert response.status_code == 200
    user = UserLoginResponse.model_validate(response.json())
    yield user