
from datetime import date, datetime
import uuid
from sqlmodel import Column, Field, Relationship, SQLModel, table
from typing import Optional
import sqlalchemy.dialects.postgresql as pg
from typing import List



class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role:str = Field(sa_column=Column(pg.VARCHAR,nullable=False,server_default="user"))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))   
    def __repr__(self):
        return f"<User {self.username}>"



class Car(SQLModel,table=True):
    __tablename__ = "cars"
    uid:uuid.UUID = Field(
        sa_column = Column(pg.UUID,nullable = False,primary_key = True,default = uuid.uuid4)
    )
    car_model:str
    car_mark:str
    car_year:int
    issueBroken:str = Field(nullable=True)
    user_uid:Optional[uuid.UUID] = Field(default = None,foreign_key = "users.uid")
    car_image_path:str| None = None