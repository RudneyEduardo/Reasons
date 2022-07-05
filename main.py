import os
from xmlrpc.client import boolean
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URI"])
db = client.ReasonsDb


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ReasonModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    reason: str = Field(...)
    visited: str = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "reason": "Eu te Amo Demais",
                "visited": "false",
            }
        }




@app.post("/", response_description="Add new student", response_model=ReasonModel)
async def create_reason(reason: ReasonModel = Body(...)):
    reason = jsonable_encoder(reason)
    new_reason = await db["reasons"].insert_one(reason)
    created_reason = await db["reasons"].find_one({"_id": new_reason.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_reason)


@app.get(
    "/", response_class=HTMLResponse
)
async def home_page():
    return """
    <html>
        <head>
            <title>Fast Api Example Test</title>
        </head>
        <body>
            <h1>Look Im Working</h1>
        </body>
    </html>
    """
    
@app.get(
    "/all", response_description="List all reasons that were not visited", response_model=List[ReasonModel]
)
async def list_reasons():
    reasons = await db["reasons"].find().to_list(200)
    reasonNotVisited = []
    for i in range(len(reasons)):
        if reasons[i]["visited"] == "false":
            reasonNotVisited.append(reasons[i])

    return reasonNotVisited






