# create a FastAPI application
import time
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mlteacher import config
from mlteacher.mlops import train
import os
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
import json
import base64

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

@app.get("/jobs")
def train_model():
    queue_client = QueueClient.from_connection_string(config.TrainConfig.fileshare_connection_string, "modeltrainingqueue", message_encode_policy=TextBase64EncodePolicy())
    queue_client.send_message(
        json.dumps({
            "model": "digits"
        })
    )
    return "Added model training job"

@app.post("/models")
def train_model():
    n_min = 5
    
    time.sleep(n_min * 60)
    return "model training done"

# @app.get("/models")
def test_can_upload_file():
    from azure.storage.fileshare import ShareFileClient

    _, model_serving_path = train.train_and_evaluate()

    # upload all files from a saved model to fileshare

    for root, _, filename in os.walk(model_serving_path):
        if filename:
            local_filepath = os.path.join(root, filename)
            # same as local_filepath but added for readability and to remove ambiguity
            fs_filepath = os.path.join(root, filename)
            file_client = ShareFileClient.from_connection_string(conn_str=config.TrainConfig.fileshare_connection_string, share_name=config.TrainConfig.fileshare_name, file_path=fs_filepath)
            with open(local_filepath, "rb") as source_file:
                file_client.upload_file(source_file)


if __name__ == "__main__":
    # run uvicorn on port environment variable PORT or 8000
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
    # test_can_upload_file()
