# create a FastAPI application
import os
import pathlib

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config

from alphabrain.mlops import train
from alphabrain.alphabrain.mlops.trainer.azure_ml_repo import AzureMLRepo

app = FastAPI()

origins = [
    "*",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def homepage():
    return {"message": "Hello World"}


if __name__ == "__main__":
    # run uvicorn on port environment variable PORT or 8000
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
