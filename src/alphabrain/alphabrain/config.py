import os
from dotenv import load_dotenv

load_dotenv()


class AzureMLConfig:
    subscription_id = os.environ.get(
        "SUBSCRIPTION_ID")
    resource_group_name = os.environ.get(
        "RESOURCE_GROUP")
    workspace_name = os.environ.get(
        "AZUREML_WORKSPACE_NAME")


class TrainConfig:
    learning_rate = 0.003
    batch_size = 128
    hidden_size = 512
    num_train_steps = 5000
    decode_frequency = 500
    max_len_query_digit = 3
    workdir = "."
    model_name = os.environ.get("MODEL_NAME", "brain")


class InfraConfig:
    train_env: str = os.environ.get("TRAIN_ENV")
    compute_cluster: str = os.environ.get("COMPUTE_CLUSTER", "cpu-cluster")


class DeploymentConfig:
    online_endpoint_name: str = os.environ.get(
        "AZUREML_ONLINE_ENDPOINT")
    serving_environment_name: str = os.environ.get(
        "SERVING_ENVIRONMENT_NAME", "jaxserving")


class PipelineConfig:
    infra_config: InfraConfig = InfraConfig()
    train_config: TrainConfig = TrainConfig()
    deployment_config: DeploymentConfig = DeploymentConfig()
    azure_ml_config: AzureMLConfig = AzureMLConfig()


class GraphAPIConfig:
    microbrain_endpoint: str = os.environ.get(
        "ALPHABRAIN_ENDPOINT", "http://localhost:8000")
