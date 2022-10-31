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


@app.get("/azureml/environments")
def get_environments():
    docker_build_context = pathlib.Path().parent.resolve()
    repo = AzureMLRepo()
    env_versions = repo.register_environment(docker_build_context)
    return env_versions


@app.get("/azureml/compute")
def get_compute():
    repo = AzureMLRepo()
    repo.create_compute()


@app.get("/azureml/training")
def get_training():
    repo = AzureMLRepo()
    src_code_root_folder = pathlib.Path().parent.resolve()
    training_info = repo.submit_training_job(
        path_to_src_code=src_code_root_folder)
    return training_info


@app.get("/azureml/models/{job_name}")
def add_model(job_name: str):
    repo = AzureMLRepo()
    repo.register_model_from_job_name(job_name)


if __name__ == "__main__":
    # run uvicorn on port environment variable PORT or 8000
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
