# import required libraries
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model
from azure.ai.ml.entities import ManagedOnlineDeployment
from alphabrain.config import PipelineConfig, AzureMLConfig
from datetime import datetime


class AzureMLRepo:

    def __init__(self, azure_ml_config: AzureMLConfig = AzureMLConfig()):
        self.ml_client: MLClient = MLClient(DefaultAzureCredential(), azure_ml_config.subscription_id,
                                            azure_ml_config.resource_group_name, azure_ml_config.workspace_name)

    def register_model(self, path_to_model_on_storage_account, model_artifact_name='alphabrain'):
        model_version = str(datetime.now().strftime("%Y%m%d%H%M%S"))
        # atastores/workspaceblobstore/paths/azureml/8b611fb8-afe0-4464-b6a7-eba88541e8b6/serving_model_dir/brain/
        # azureml://subscriptions/0abb6ec5-9030-4b3f-af04-09183c688576/resourcegroups/csu-nl-intelligence/workspaces/mlpatterns/datastores/workspaceblobstore/paths/azureml/8b611fb8-afe0-4464-b6a7-eba88541e8b6/serving_model_dir/brain/20221101080400/
        model = Model(
            path=path_to_model_on_storage_account,
            name=model_artifact_name,
            version=model_version,
            type="custom_model",
            description="Model created from pipeline run."
        )
        self.ml_client.models.create_or_update(model)
        return model_artifact_name, model_version

    def online_endpoint_deployment(self, model_artifact_name, model_artifact_version, tf_model_name):
        serving_env = self.ml_client.environments.get(
            name=PipelineConfig.deployment_config.serving_environment_name, version='1')

        # model_artifact_version = next(
        #     self.ml_client.models.list(name=model_artifact_name)).version
        model = self.ml_client.models.get(
            name=model_artifact_name, version=model_artifact_version)

        deployment_name = f'brain-deployment-{model_artifact_version}'
        blue_deployment = ManagedOnlineDeployment(
            name=deployment_name,
            endpoint_name=PipelineConfig.deployment_config.online_endpoint_name,
            model=model,
            environment=serving_env,
            environment_variables={
                "MODEL_BASE_PATH": f"/var/azureml-app/azureml-models/{model_artifact_name}/{model_artifact_version}",
                "MODEL_NAME": tf_model_name,
            },
            instance_type="Standard_DS2_v2",
            instance_count=1,

        )

        # create a blue deployment
        endpoint = self.ml_client.online_endpoints.get(
            name=PipelineConfig.deployment_config.online_endpoint_name)
        endpoint.traffic = {deployment_name: 100}
        self.ml_client.begin_create_or_update(blue_deployment).result()
        self.ml_client.begin_create_or_update(endpoint)

    def submit_pipeline_job(self, pipeline_definition):
        pipeline_instance = pipeline_definition()

        pipeline_job = self.ml_client.jobs.create_or_update(
            pipeline_instance, experiment_name="pipeline_samples"
        )
