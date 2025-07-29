from  src.schemas import PredictionResponse, SensorModel
from sqlmodel import select
from src.errors import CarNotFound, SensorNotFound
from src.db.models import Car, Sensor
from src.config import Config
from src.ml_model_loader import model,model2
from sqlalchemy import desc
import pandas as pd

class SensorService():

    async def insertSensors(self,sensor_data:SensorModel,session):


        sensors_dict =sensor_data.model_dump()        

        sensor_dict_int = {key:float(value)for key,value in sensors_dict.items()}


        inserted_sensors= Sensor(**sensor_dict_int)

        stmt = select(Car).where(Car.uid == inserted_sensors.car_uid)

        result = await session.exec(stmt)

        car = result.one_or_none();
        if car is None:
            raise CarNotFound()

        session.add(inserted_sensors ) 
        await session.commit()

        return inserted_sensors

    async def getSensorBycarId(self,carId,session):
        stmt = select(Sensor).where(Sensor.car_uid == carId)
        result = await session.exec(stmt)
        sensor = result.one_or_none()
        if not result:
            raise SensorNotFound()
        
        return sensor


    async def updateSensors(self,update_data:dict,cardId,session):

        sensor = getSensorBycarId(carId,session)

        for k,v in update_data.items():
            setattr(sensor,k,v,)

        session.commit()

        return sensor

    async def getPrediction(self,carId,session):
        stmt=select(Sensor.coolant_temp,
                    Sensor.rpm,Sensor.fuel_consumption,
                    Sensor.generator_voltage,Sensor.maf,
                    Sensor.iat,Sensor.tps,Sensor.speed,
                    Sensor.timing_advance,
                    Sensor.short_term_fuel_trim
        ).where(Sensor.car_uid == int(carId)).order_by(desc(Sensor.uid)).limit(1)
        result =  await session.exec(stmt)
        df = pd.DataFrame([dict(row._mapping) for row in result])
                           
        print("DataFrame",df.head(),sep="\n")

        
        if Config.Mode =="develop":
            prediction1 = model.predict(df)
            prediction2 = model2.predict(df)
            issueBroken = prediction1[0]
            km_to_failure = int(prediction2[0])
            print(issueBroken)
            print(km_to_failure)

            response_dict={"issue_broken":issueBroken,"km_to_failure":str(km_to_failure)}

            return  response_dict
        response_dict={"issue_broken":"test stage","km_to_failure":"test Stage"}
        return response_dict
        
    
    def estimate_speed(self,rpm):
        """
        Приблизительно оценивает скорость по оборотам, если реальная скорость = 0.
        """
        if rpm <= 900:
            return 0  # холостой ход, машина точно стоит
        else:
            return rpm / 100 * 2.5  # эмпирический коэффициент
    
    def fill_speed(self,row):
        if row['speed'] == 0 and row['rpm'] > 900:
            return self.estimate_speed(row['rpm'])
        return row['speed']

        df['speed'] = df.apply(fill_speed, axis=1)
