from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid





class USerCreateModel(BaseModel):        
    username: str = Field(max_lenght=8)
    email: str = Field(max_lenght=40)
    password: str = Field(min_lenght=6)


class UserModel(BaseModel):
    uid: int
    username: str
    email: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    update_at: datetime    

class UserResponse(BaseModel):
        email:str
        username:str
        uid:int

class UserLoginResponse(BaseModel):
    message:str
    access_token:str
    refresh_token:str
    user:UserResponse

class USerLogginModel(BaseModel):
    email: str = Field(max_lenght=40)
    password: str = Field(min_lenght=6)


class CarModel(BaseModel):
    uid:int
    user_uid:int
    car_model:str = Field(max_length=20)
    car_mark:str = Field(max_length=20)    
    car_year:int
    issueBroken : Optional[str] = None
    car_image_path:Optional[str] = None
   


class CreateCarModel(BaseModel):
    user_uid:int
    car_model:str = Field(max_length=20)
    car_mark:str = Field(max_length=20)    
    car_year:str = Field(max_length=10)
    car_image_path:Optional[str] = None   
    issueBroken:Optional[str] = None

class CreateCarModelSync(CreateCarModel):
    uid:Optional[int] =None
    temp_uid:int


class UpdateCarModel(BaseModel):
    model:str = Field(max_length=20)
    mark:str = Field(max_length=20)    
    year:str = Field(max_length=10)


class ResponseContact(BaseModel):
    status_code:str
    detail:str
    
class IdMapping(BaseModel):
    temp_id:int
    new_id:int

class CarCreateResponse(ResponseContact):
    ids:list[IdMapping]



class EmailModel(BaseModel):
    addresses:List[str]


class SensorModel(BaseModel):       
       coolant_temp:str
       rpm:str
       fuel_consumption:str
       generator_voltage:str
       maf:str
       iat:str
       tps:str
       speed:str
       timing_advance:str
       short_term_fuel_trim:str
       car_uid:int

class PredictionResponse(BaseModel):
    status_code:str
    detail:str
    issue_broken:str
    km_to_failure:str