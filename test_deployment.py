
# # import required libraries
# from azure.ai.ml import MLClient
# from azure.identity import DefaultAzureCredential
# from azure.ai.ml.entities import Model
# from azure.ai.ml.entities import Environment, BuildContext, ManagedOnlineDeployment
# from azure.ai.ml import command
# import os


# class AzureMLConfig:
#     subscription_id = os.environ.get(
#         "SUBSCRIPTION_ID", "0abb6ec5-9030-4b3f-af04-09183c688576")
#     resource_group_name = os.environ.get(
#         "RESOURCE_GROUP", "csu-nl-machine-learning-with-jax")
#     workspace_name = os.environ.get(
#         "AZUREML_WORKSPACE_NAME", "mb-pf-ob3dbeybifbia")


# class TrainConfig:
#     learning_rate = 0.003
#     batch_size = 128
#     hidden_size = 512
#     num_train_steps = 5000
#     decode_frequency = 500
#     max_len_query_digit = 3
#     workdir = "."
#     model_name = os.environ.get("MODEL_NAME", "brain")


# class InfraConfig:
#     train_env: str = os.environ.get("TRAIN_ENV", "jaxtraining")
#     compute_cluster: str = os.environ.get("COMPUTE_CLUSTER", "cpu-cluster")


# class DeploymentConfig:
#     online_endpoint_name: str = os.environ.get(
#         "AZUREML_ONLINE_ENDPOINT", "moeob3dbeybifbia")
#     serving_environment_name: str = os.environ.get(
#         "SERVING_ENVIRONMENT_NAME", "jaxserving")
#     endpoint_api_key: str = os.environ.get(
#         "ENDPOINT_API_KEY")
#     # "ENDPOINT_API_KEY", "jYVasujnJESABBAIJcKKvKr1o7UdrGnT")


# class PipelineConfig:
#     infra_config: InfraConfig = InfraConfig()
#     train_config: TrainConfig = TrainConfig()
#     deployment_config: DeploymentConfig = DeploymentConfig()
#     azure_ml_config: AzureMLConfig = AzureMLConfig()


# class GraphAPIConfig:
#     microbrain_endpoint: str = os.environ.get(
#         "ALPHABRAIN_ENDPOINT", "http://localhost:8000")


# class AzureMLRepo:

#     def __init__(self, azure_ml_config: AzureMLConfig = AzureMLConfig()):
#         self.ml_client: MLClient = MLClient(DefaultAzureCredential(), azure_ml_config.subscription_id,
#                                             azure_ml_config.resource_group_name, azure_ml_config.workspace_name)

#     def online_endpoint_deployment(self, model_artifact_name, model_artifact_version, tf_model_name):
#         serving_env = self.ml_client.environments.get(
#             name=PipelineConfig.deployment_config.serving_environment_name, version='1')

#         # model_artifact_version = next(
#         #     self.ml_client.models.list(name=model_artifact_name)).version
#         model = self.ml_client.models.get(
#             name=model_artifact_name, version=model_artifact_version)

#         deployment_name = f'brain-deployment-1{model_artifact_version}'
#         blue_deployment = ManagedOnlineDeployment(
#             name=deployment_name,
#             endpoint_name=PipelineConfig.deployment_config.online_endpoint_name,
#             model=model,
#             environment=serving_env,
#             environment_variables={
#                 "MODEL_BASE_PATH": f"/var/azureml-app/azureml-models/{model_artifact_name}/{model_artifact_version}",
#                 "MODEL_NAME": tf_model_name,
#             },
#             instance_type="Standard_DS2_v2",
#             instance_count=1,

#         )

#         # create a blue deployment
#         endpoint = self.ml_client.online_endpoints.get(
#             name=PipelineConfig.deployment_config.online_endpoint_name)
#         endpoint.traffic = {deployment_name: 100}
#         self.ml_client.begin_create_or_update(blue_deployment).result()
#         self.ml_client.begin_create_or_update(endpoint)


# repo = AzureMLRepo()
# # print(repo.ml_client.online_endpoints.get_keys(
# #     name=PipelineConfig.deployment_config.online_endpoint_name).access_token)
# repo.online_endpoint_deployment(model_artifact_name="alphabrainfrompipeline",
#                                 model_artifact_version="20221117182540", tf_model_name='brain')
