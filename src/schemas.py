from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid


class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: Optional[uuid.UUID]
    product_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=5)
    review_text: str = Field(max_lenght=48)


class Product(BaseModel):
    uid: uuid.UUID
    title: str = Field(max_length=10, min_length=3)
    description: str = Field(max_length=50, min_length=8)
    size: str
    images: int = Field(ge=0)
    price: int = Field(ge=0)
    has: bool = Optional[bool] | False
    published_date: date
    created_at: datetime
    update_at: datetime
    user_uid: Optional[uuid.UUID]
    reviews: List[ReviewModel]


class CreateProduct(BaseModel):
    title: str = Field(max_length=10, min_length=3)
    description: str = Field(max_length=50, min_length=8)
    size: str
    images: int = Field(ge=0)
    price: int = Field(ge=0)
    has: bool = Optional[bool] | False
    published_date: str


class UpdateProduct(BaseModel):
    title: str = Field(max_length=10, min_length=3)
    description: str = Field(max_length=50, min_length=8)
    size: str
    images: int = Field(ge=0)
    price: int = Field(ge=0)
    has: bool = Optional[bool] | True


class USerCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_lenght=8)
    email: str = Field(max_lenght=40)
    password: str = Field(min_lenght=6)


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    update_at: datetime    


class UserProductsModel(UserModel):
    products: List[Product]


class USerLogginModel(BaseModel):
    email: str = Field(max_lenght=40)
    password: str = Field(min_lenght=6)


class CarModel(BaseModel):
    uid:uuid.UUID
    user_uid:uuid.UUID
    car_model:str = Field(max_length=20)
    car_mark:str = Field(max_length=20)    
    car_year:int
    issueBroken : Optional[str] = None
    car_image_path:Optional[str] = None
   


class CreateCarModel(BaseModel):
    user_uid:uuid.UUID
    car_model:str = Field(max_length=20)
    car_mark:str = Field(max_length=20)    
    car_year:str = Field(max_length=10)

   

class UpdateCarModel(BaseModel):
    model:str = Field(max_length=20)
    mark:str = Field(max_length=20)    
    year:str = Field(max_length=10)


