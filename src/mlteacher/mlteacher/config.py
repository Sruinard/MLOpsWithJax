import os
from dotenv import load_dotenv

load_dotenv()


class AzureMLConfig:
    subscription_id = os.environ.get(
        "SUBSCRIPTION_ID", "0abb6ec5-9030-4b3f-af04-09183c688576")
    resource_group_name = os.environ.get(
        "RESOURCE_GROUP", "csu-nl-intelligence")
    workspace_name = os.environ.get("AZUREML_WORKSPACE_NAME", "mlpatterns")


class TrainConfig:
    learning_rate = 0.003
    batch_size = 128
    hidden_size = 512
    num_train_steps = 4000
    decode_frequency = 500
    max_len_query_digit = 3
    workdir = "."
    model_name = os.environ.get("MODEL_NAME", "brain")


class DeploymentConfig:
    online_endpoint_name: str


class PipelineConfig:
    deployment_config: DeploymentConfig
    train_config: TrainConfig
    azure_ml_config: AzureMLConfig
