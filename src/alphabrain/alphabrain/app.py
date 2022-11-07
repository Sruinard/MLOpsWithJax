# create a FastAPI application
import os

from dataclasses import dataclass
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from alphabrain.mlops import pipeline, serving
from alphabrain.mlops.trainer.azure_ml_repo import AzureMLRepo

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


@dataclass
class InferenceRequest:
    body: str


@app.get("/")
def homepage():
    return {"message": "Hello World"}


@app.post("/pipelines/")
def submit_pipeline_run():
    repo = AzureMLRepo()
    repo.ml_client.jobs.create_or_update(
        job=pipeline.brain_in_production(), experiment_name="mlops-with-jax")


@app.post("/models/{model_name}/predict")
def invoke_ml_endpoint(inference_request: InferenceRequest, model_name: str):
    inference_pipeline = serving.InferencePipelineFactory(
    ).get_inference_pipeline(model_name)
    prediction = inference_pipeline.predict(inference_request.body)
    return {
        "inputs": inference_request.body,
        "outputs": prediction,
        "combined": f"{inference_request.body}={prediction}"
    }


if __name__ == "__main__":
    # run uvicorn on port environment variable PORT or 8000
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
