

from alphabrain.alphabrain.mlops.trainer.azure_ml_repo import AzureMLRepo
from alphabrain.mlops import train
from azure.ai.ml.dsl import pipeline
from azure.ai.ml import load_component
from azure.ai.ml.entities import Environment, AmlCompute
from mldesigner import command_component, Input, Output


@command_component(
    name="train_model",
    version="1",
    display_name="Train Jax Model",
    description="Train a jax model to be able to add digits",
    environment=Environment(),
)
def train_and_eval_model_job(serving_model_dir: Output(type="uri_folder"), logs_dir: Output(type="uri_folder")):
    _ = train.train_and_evaluate(
        serving_model_dir=serving_model_dir, logs_dir=logs_dir)


@command_component(
    name="register trained ml model",
    version="1",
    display_name="register JAX model",
    description="Register JAX ML model to be served with TFServing and managed online endpoints",
    environment=None,
)
def register_ml_model_job(serving_model_dir: Input(type='uri_folder'), model_name: Output(type='string')):
    repo = AzureMLRepo()
    repo.register_model(local_path=serving_model_dir, model_name=model_name)


@command_component(
    name="serve_with_managed_endpoints_and_tfserving",
    version="1",
    display_name="Serve JAX model with managed endpoints and tfserving",
    description="Serve a encoder decoder model with tfserving",
    environment=None,
)
def serve_ml_model_job(model_name: Input(type='str')):
    repo = AzureMLRepo()
    repo.online_endpoint_deployment(model_name=model_name)


@pipeline()  # default_compute=cpu_compute_target,)
def brain_in_production():
    model_name = "brain"
    """Train jax model and serve with tfserving."""
    train_and_eval_out = train_and_eval_model_job()

    model_registration_out = register_ml_model_job(
        train_and_eval_out.outputs.serving_model_dir, model_name=model_name)

    _ = serve_ml_model_job(
        model_name=model_registration_out.outputs.model_name)
