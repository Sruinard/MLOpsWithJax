

from mlteacher.submit_training import AzureMLRepo
from mlteacher.mlops import train
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import load_component
from mldesigner import command_component, Input, Output


@command_component(
    name="train_model",
    version="1",
    display_name="Train Jax Model",
    description="Train a jax model to be able to add digits",
    environment=None,
)
def train_and_eval_model_job(model_output_path: Output(type="uri_folder")):
    train.train_and_evaluate(model_output_path)


@command_component(
    name="register trained ml model",
    version="1",
    display_name="register JAX model",
    description="Register JAX ML model to be served with TFServing and managed online endpoints",
    environment=None,
)
def register_ml_model_job(model_output_path: Input(type='uri_folder')):
    repo = AzureMLRepo()
    repo.register_model(local_path=model_output_path)


@command_component(
    name="serve_with_managed_endpoints_and_tfserving",
    version="1",
    display_name="Serve JAX model with managed endpoints and tfserving",
    description="Serve a encoder decoder model with tfserving",
    environment=None,
)
def serve_ml_model_job():
    pass
