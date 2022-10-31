# import required libraries
from azure.ai.ml import MLClient
from azure.ai.ml.entities import AmlCompute
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model
from azure.ai.ml.entities import Environment, BuildContext, ManagedOnlineDeployment
from azure.ai.ml import command
import os
from alphabrain.config import PipelineConfig, AzureMLConfig


class AzureMLRepo:

    def __init__(self, azure_ml_config: AzureMLConfig = AzureMLConfig()):
        self.cpu_compute_target = "cpu-cluster"
        self.ml_client = MLClient(DefaultAzureCredential(), azure_ml_config.subscription_id,
                                  azure_ml_config.resource_group_name, azure_ml_config.workspace_name)

    def create_compute(self):
        try:
            self.ml_client.compute.get(self.cpu_compute_target)
        except Exception:
            print("Creating a new cpu compute target...")
            compute = AmlCompute(
                name=self.cpu_compute_target, size="STANDARD_D2_V2", min_instances=0, max_instances=4
            )
            self.ml_client.compute.begin_create_or_update(compute).result()

    def register_environment(self, root_dir):
        env_name = "mlteacher-jax-env"
        env_docker_context = Environment(
            build=BuildContext(path=root_dir),
            name=env_name,
            description="Environment created from a Docker context.",
        )
        self.ml_client.environments.create_or_update(env_docker_context)
        envs = self.ml_client.environments.list(name=env_name)
        return {
            "environment_versions": [env.version for env in envs],
            "environment_name": env_name
        }

    def submit_training_job(self, path_to_src_code: str):
        # define the command
        env_name = "mlteacher-jax-env"
        envs = self.ml_client.environments.list(name=env_name)
        command_job = command(
            code=path_to_src_code,
            command="python mlteacher/mlops/train.py",
            environment=f"{env_name}:{next(envs).version}",
            compute=self.cpu_compute_target,
        )
        # submit the command
        returned_job = self.ml_client.jobs.create_or_update(command_job)
        # get a URL for the status of the job
        return {
            "endpoint": returned_job.services["Studio"].endpoint,
            "name": returned_job.name
        }

    def online_endpoint_deployment(self, model_name):
        # create a blue deployment
        model = Model(name=PipelineConfig.train_config.model_name, version="1")

        env = Environment(
            name="tfserving-environment",
            image="docker.io/tensorflow/serving:latest",
            inference_config={
                "liveness_route": {"port": 8501, "path": f"/v1/models/{model_name}"},
                "readiness_route": {"port": 8501, "path": f"/v1/models/{model_name}"},
                "scoring_route": {"port": 8501, "path": f"/v1/models/{model_name}:predict"},
            },
        )

        blue_deployment = ManagedOnlineDeployment(
            name="blue",
            endpoint_name=PipelineConfig.deployment_config.online_endpoint_name,
            model=model,
            environment=env,
            environment_variables={
                "MODEL_BASE_PATH": f"/var/azureml-app/azureml-models/{model_name}/1",
                "MODEL_NAME": model_name,
            },
            instance_type="Standard_DS2_v2",
            instance_count=1,
        )
        self.ml_client.begin_create_or_update(blue_deployment)

    def register_model(self, job_name=None, local_path=None, model_name="brain"):
        if job_name is not None:
            model_to_register = self._get_model_from_job_name(
                job_name=job_name, model_name=model_name)
        if local_path is not None:
            model_to_register = self._get_model_from_local(
                local_path=local_path, model_name=model_name)
        self.ml_client.models.create_or_update(model_to_register)

    def _get_model_from_local(self, local_path, model_name="brain"):
        path_to_model = os.path.join(local_path, model_name)
        run_model = Model(
            path=path_to_model, name=model_name,
            description="JAX ML Model created from run and converted to Tensorflow Saved Model.",
            type="custom_model"
        )

        return run_model

    def _get_model_from_job_name(self, job_name, model_name="brain"):

        run_model = Model(
            path=f"azureml://jobs/{job_name}/outputs/artifacts/models/{model_name}", name=model_name,
            description="JAX ML Model created from run and converted to Tensorflow Saved Model.",
            type="custom_model"
        )
        return run_model

    def submit_pipeline_job(self, pipeline_definition):
        pipeline_instance = pipeline_definition()

        pipeline_job = self.ml_client.jobs.create_or_update(
            pipeline_instance, experiment_name="pipeline_samples"
        )
