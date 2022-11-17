param ml_workspace_name string
param image_uri string

param environment_version string = '1'
param ml_model_name string = 'brain'
param location string = resourceGroup().location
var uuid = uniqueString(resourceGroup().id)
var unique_endpoint_name = 'moe${uuid}'

resource serving_image 'Microsoft.MachineLearningServices/workspaces/environments/versions@2022-06-01-preview' = {
  name: '${ml_workspace_name}/jaxserving/${environment_version}'
  properties: {
    image: image_uri
    inferenceConfig: {
      livenessRoute: {
        path: '/v1/models/${ml_model_name}'
        port: 8501
      }
      readinessRoute: {
        path: '/v1/models/${ml_model_name}'
        port: 8501
      }
      scoringRoute: {
        path: '/v1/models/${ml_model_name}:predict'
        port: 8501
      }
    }
    osType: 'Linux'
  }
}

resource jax_online_endpoint 'Microsoft.MachineLearningServices/workspaces/onlineEndpoints@2022-06-01-preview' = {
  name: '${ml_workspace_name}/${unique_endpoint_name}'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    // authMode: 'AMLToken'
    authMode: 'Key'
    traffic: {}
  }
}
