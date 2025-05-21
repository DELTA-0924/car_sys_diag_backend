
from datetime import date, datetime
import uuid
from sqlmodel import Column, Field, Relationship, SQLModel, table
from typing import Optional
from sqlalchemy import ForeignKey,BigInteger
import sqlalchemy.dialects.postgresql as pg
from typing import List



class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: int = Field(
           sa_column=Column(pg.BIGINT, primary_key=True, nullable=False)
    )
    username: str
    email: str
    role:str = Field(sa_column=Column(pg.VARCHAR,nullable=False,server_default="user"))
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))   
    def __repr__(self):
        return f"<User {self.username}>"



class Car(SQLModel,table=True):
    __tablename__ = "cars"
    uid:int = Field(
           sa_column=Column(pg.BIGINT, primary_key=True, nullable=False)
    )
    car_model:str
    car_mark:str
    car_year:int
    issueBroken:str = Field(nullable=True)
    user_uid:Optional[int] = Field(default = None,sa_column = Column(pg.BIGINT,ForeignKey("users.uid",ondelete = "CASCADE"),nullable = True))
    car_image_path:str| None = None    