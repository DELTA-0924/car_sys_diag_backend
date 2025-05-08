from typing import List
from fastapi import APIRouter,Depends, UploadFile,status,File,Form
from src.dependencies import AccessTokenBearer
from src.schemas import CarModel,CreateCarModel,CreateCarModelSync
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.dbConnect import get_session
from src.services.car_service import CarService
from src.errors import (
    CarNotFound
    )


car_router = APIRouter()
car_service = CarService()
acces_token_bearer = AccessTokenBearer()



@car_router .post("/",response_model=CarModel,status_code = status.HTTP_201_CREATED)
async def create_car(car_data:CreateCarModel,session:AsyncSession = Depends(get_session)):

   new_car = await car_service.create_car(car_data,session)
   
   return new_car

@car_router .get("/",response_model = List[CarModel])
async def get_cars(session:AsyncSession = Depends(get_session),
                   token_details = Depends(acces_token_bearer)):
    user_uid = token_details.get("user")["user_uid"]
    cars = await car_service.get_all_cars(user_uid,session)
    if cars is not None:
        return cars
    else :
        raise CarNotFound()

@car_router.post("/sync",status_code = status.HTTP_201_CREATED)
async def synchronize_data_car(data:List[CreateCarModelSync],
                               user_details = acces_token_bearer,
                               session: AsyncSession = Depends(get_session)
                               ):
    await car_service.synchronize_data(data,session)

    return status.HTTP_201_CREATED


@car_router.post("/upload-image")
async def upload_image(car_uid:str = Form(...),image:UploadFile = File(...),session:AsyncSession = Depends(get_session)):
    

    await car_service.set_car_image(image,car_uid,session);

    return status.HTTP_200_OK