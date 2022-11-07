import os
from pathlib import Path

from alphabrain.mlops.trainer.azure_ml_repo import AzureMLRepo
from alphabrain.mlops.trainer import train
from alphabrain.config import PipelineConfig
from azure.ai.ml import dsl
from azure.ai.ml.entities import Environment, AmlCompute, BuildContext
from mldesigner import command_component, Input, Output

environment = Environment(
    # build=BuildContext(path="../"),
    # name="jax-training-environment"
    name="jax-training-environment",
    build=BuildContext(path=Path(__file__).resolve().parents[0])
)


@command_component(
    name="train_model",
    version="1",
    display_name="Train Jax Model",
    description="Train a jax model to be able to add digits",
    environment=environment
)
def train_and_eval_model_job(serving_model_dir: Output(type="uri_folder", mode="upload"), logs_dir: Output(type="uri_folder", mode="upload")):
    _ = train.train_and_evaluate(
        serving_model_dir=serving_model_dir, logs_dir=logs_dir)


@command_component(
    name="register_trained_ml_model",
    version="1",
    display_name="register JAX model",
    description="Register JAX ML model to be served with TFServing and managed online endpoints",
    environment=environment
)
def register_ml_model_job(serving_model_dir: Input(type='uri_folder', mode='direct'), model_artifact_name: Input(type='string'), model_artifact_version: Output(type='uri_folder')):
    repo = AzureMLRepo()
    path_to_model_on_storage_account = f"{serving_model_dir}brain"
    model_artifact_name, registered_model_artifact_version = repo.register_model(path_to_model_on_storage_account=path_to_model_on_storage_account,
                                                                                 model_artifact_name=model_artifact_name)
    # registered_model_artifact_version = "123456"
    with open(os.path.join(model_artifact_version, "model_artifact_version.txt"), "wt") as text_file:
        text_file.write(registered_model_artifact_version)


@command_component(
    name="serve_with_managed_endpoints_and_tfserving",
    version="1",
    display_name="Serve JAX model with managed endpoints and tfserving",
    description="Serve a encoder decoder model with tfserving",
    environment=environment
)
def serve_ml_model_job(model_artifact_name: Input(type="string"), model_artifact_version: Input(type="uri_folder"), tf_model_name: Input(type='string')):
    with open(os.path.join(model_artifact_version, "model_artifact_version.txt"), "r") as text_file:
        model_artifact_version = text_file.readline()

    repo = AzureMLRepo()
    repo.online_endpoint_deployment(
        model_artifact_name=model_artifact_name, model_artifact_version=model_artifact_version, tf_model_name=tf_model_name)


# default_compute=cpu_compute_target,)
@dsl.pipeline(compute=PipelineConfig.infra_config.compute_cluster)
def brain_in_production():
    """Train jax model and serve with tfserving."""
    model_artifact_name = "alphabrainfrompipeline"
    train_and_eval_out = train_and_eval_model_job()

    model_registration_out = register_ml_model_job(
        serving_model_dir=train_and_eval_out.outputs.serving_model_dir, model_artifact_name=model_artifact_name)

    _ = serve_ml_model_job(
        model_artifact_name=model_artifact_name, model_artifact_version=model_registration_out.outputs.model_artifact_version, tf_model_name='brain')
