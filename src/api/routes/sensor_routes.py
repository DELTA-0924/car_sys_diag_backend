from src.schemas import PredictionResponse, SensorModel,ResponseContact
from fastapi import APIRouter,Depends,status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.dbConnect import get_session
from src.services.sensor_service import SensorService

sensor_router = APIRouter()

sensor_service = SensorService()

@sensor_router.post("/send-sensors",response_model = PredictionResponse,status_code = status.HTTP_200_OK)
async def send_sensors(sensor_data:SensorModel,session:AsyncSession = Depends(get_session)):

    await sensor_service.insertSensors(sensor_data,session)


    prediction_dict= await sensor_service.getPrediction(sensor_data.car_uid,session)


    response = PredictionResponse(status_code = str(status.HTTP_200_OK),detail = "predicted successfully",
                                  issue_broken = prediction_dict['issue_broken'],
                                  km_to_failure = prediction_dict['km_to_failure'])
    
    
    return response
    

