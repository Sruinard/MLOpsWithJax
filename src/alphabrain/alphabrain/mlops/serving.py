
import jax.numpy as jnp
from alphabrain.mlops.trainer import transform
from alphabrain.config import PipelineConfig
from typing import Tuple, Any, Dict
import requests
import json
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

from alphabrain.config import AzureMLConfig

Array = Any


class IInferencePipeline:
    def __init__(self, azure_ml_config: AzureMLConfig = AzureMLConfig()):
        self.ml_client = MLClient(DefaultAzureCredential(), azure_ml_config.subscription_id,
                                  azure_ml_config.resource_group_name, azure_ml_config.workspace_name)

    def _preprocessing(self, *kwargs):
        raise NotImplementedError()

    def _inference(self, *kwargs):
        raise NotImplementedError()

    def _postprocessing(self, *kwargs):
        raise NotImplementedError()

    def predict(self, inputs: Any):
        features = self._preprocessing(inputs)
        predictions = self._inference(features)
        outputs = self._postprocessing(predictions)
        return outputs


class MicroBrainInferencePipeline(IInferencePipeline):
    def __init__(self, ctable=transform.CharacterTable('0123456789+= ', PipelineConfig.train_config.max_len_query_digit)):
        super().__init__()
        self.ctable = ctable

    def _preprocessing(self, input_query: str):
        inputs_encoder = self.ctable.encode_one_hot([input_query])
        init_decoder_input = self.ctable.one_hot(self.ctable.encode('=')[0:1])
        inputs_decoder = jnp.tile(init_decoder_input,
                                  (inputs_encoder.shape[0], self.ctable.max_output_len, 1))
        return (inputs_encoder, inputs_decoder)

    def _inference(self, inputs: Tuple[Array, Array]):
        encoder_inputs, decoder_inputs = inputs
        url = f'https://{PipelineConfig.deployment_config.online_endpoint_name}.westeurope.inference.ml.azure.com/v1/models/brain:predict'

        # The azureml-model-deployment header will force the request to go to a specific deployment.
        # Remove this header to have the request observe the endpoint traffic rules
        # , 'azureml-model-deployment': 'brain-deployment-20221104160432' }
        access_token = self.ml_client.online_endpoints.get_keys(
            name=PipelineConfig.deployment_config.online_endpoint_name).access_token
        headers = {'Content-Type': 'application/json',
                   'Authorization': ('Bearer ' + access_token)}
        data = {
            "signature_name": "serving_default",
            "instances": [{
                "inputs": encoder_inputs[0].tolist(),
                "decoder_inputs": decoder_inputs[0].tolist()
            }]
        }
        outputs = requests.post(
            url=url, data=json.dumps(data), headers=headers).json()['predictions'][0]
        return outputs

    def _postprocessing(self, outputs: Dict[str, Array]):
        return self.ctable.decode_onehot(jnp.array(outputs['output_1'])[jnp.newaxis, :])[0]


class InferencePipelineFactory:
    def get_inference_pipeline(self, model_name):
        if model_name == "brain":
            return MicroBrainInferencePipeline()
