
from typing import List
from fastapi import APIRouter,Depends, UploadFile,status,File,Form,Response
from fastapi.responses import JSONResponse
from src.dependencies import AccessTokenBearer
from src.schemas import CarCreateResponse, CarModel,CreateCarModel,CreateCarModelSync,ResponseContact
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.dbConnect import get_session
from src.services.car_service import CarService
from src.config import Config
from src.errors import (
    CarNotFound
    )
STATIC_URL_PREFIX = Config.STATIC_URL_PREFIX

car_router = APIRouter()
car_service = CarService()
acces_token_bearer = AccessTokenBearer()



@car_router.post("/",status_code = status.HTTP_201_CREATED)
async def create_car(car_data:CreateCarModelSync,session:AsyncSession = Depends(get_session)):
   
    if car_data.user_uid == 9999:
       car_data.user_uid = None
    ids =  await car_service.create_car(car_data,session)  

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=ids
    )

@car_router .get("/",response_model = List[CarModel])
async def get_cars(session:AsyncSession = Depends(get_session),
                   token_details = Depends(acces_token_bearer)):
    user_uid = token_details.get("user")["user_uid"]
    cars = await car_service.get_all_cars(user_uid,session)
    

    if cars is not None:
        for car in cars:
            car.car_image_path = STATIC_URL_PREFIX+car.car_image_path.replace("\\","/")
        return cars
    else :
        raise CarNotFound()

@car_router.post("/sync",response_model = CarCreateResponse)
async def synchronize_data_car(data:List[CreateCarModelSync],
                               user_details =Depends(acces_token_bearer),
                               session: AsyncSession = Depends(get_session)
                               ):
    ids_result = await car_service.synchronize_data(data,session)

    response = CarCreateResponse(status_code = str(status.HTTP_200_OK),detail = "Sync was succesfully",ids = ids_result)

    return  response


@car_router.post("/upload-image",response_model = ResponseContact,status_code = status.HTTP_201_CREATED)
async def upload_image(images:List[UploadFile] = File(...),session:AsyncSession = Depends(get_session),user_details = Depends(acces_token_bearer)):


    await car_service.set_car_image_bulk(images,session)

    response = ResponseContact(status_code = str(status.HTTP_200_OK),detail = "upload-image was succesfully")

    return response