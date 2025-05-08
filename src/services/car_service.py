from datetime import datetime
from typing import List
import uuid

from fastapi import UploadFile
from src.db.models import Car
from src.schemas import CarModel, CreateCarModel
from sqlmodel import select
import shutil
import os
from src.errors import CarNotFound
from sqlalchemy.dialects.postgresql import insert

UPLOAD_FOLDER = "static"

class CarService:
	async def create_car(self,car_data:CreateCarModel,session):
		car_data_dict=car_data.model_dump();
		new_car=Car(**car_data_dict);
		new_car.car_year = datetime.strptime(new_car.car_year, "%Y")
		session.add(new_car)
		await session.commit()

		return new_car

	async def synchronize_data(self, data: List[CreateCarModel], session):
		for item in data:
			item_dict = item.model_dump()
			item_dict["car_year"] = int(item.car_year)

			stmt = insert(Car).values(**item_dict)

			
			stmt = stmt.on_conflict_do_update(
				index_elements=["uid"],
				set_=item_dict  
			)

			await session.execute(stmt)

		await session.commit()
		
	async def set_car_image(self,image:UploadFile,car_uid:str,session):
		statement= select(Car).where(Car.uid == car_uid);
		result  = await session.exec(statement)
		car = result.one_or_none()
		if car is None:
			raise CarNotFound();

		file_ext = os.path.splitext(image.filename)[1]
		unique_name = f"{uuid.uuid4()}{file_ext}"
		file_path = os.path.join(UPLOAD_FOLDER, unique_name)
		print(file_path)
		with open(file_path, "wb") as buffer:
			shutil.copyfileobj(image.file, buffer)

		car.car_image_path = file_path;
		session.add(car)
		await session.commit()

	async def get_all_cars(self,user_uid:str,session):
		statement = select(Car).where(Car.user_uid == int(user_uid))

		result = await session.exec(statement)

		cars = result.all();
		
		return cars if cars is not None else None

