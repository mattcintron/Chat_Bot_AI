""" API to run note converter tools

    Endpoints
    --------

    USAGE
    -----

    Run local: 
    > uvicorn main:app --reload

    You should then be able to navigate to localhost:8000/docs to see auto-generated Swagger
"""
from fastapi import FastAPI, APIRouter, Request, Depends, Header, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import requests
import shutil
from ChatBot import *


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return "Welcome to the FastAPI ML API Production Demo"


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Upload a pdf or vtt file to the analysis tool for a data summary read out 
    """

    #save the uploaded file to the root
    with open('json_files/intents.json', "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    retrain_model()

    return {"filename": file.filename,
            "Upload":"COMPLETE",
            "Full Model Retraining":"COMPLETE"}


@app.get("/chat_bot/")
async def chat_bot(text:str):

    chat_response = respond(text)

    return {"Chat Bot Says ": chat_response}





