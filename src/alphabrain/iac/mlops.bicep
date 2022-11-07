param ml_workspace_name string
param image_uri string

param environment_version string = '2'
param ml_model_name string = 'brain'
param location string = resourceGroup().location

// resource serving_base_environment 'Microsoft.MachineLearningServices/workspaces/environments@2022-06-01-preview' = {
//   name: '${ml_workspace_name}/jaxserving-environment'
//   properties: {
//     description: 'base environment'
//     isArchived: false
//     tags: {}
//     properties: {}
//   }
// }

resource serving_image 'Microsoft.MachineLearningServices/workspaces/environments/versions@2022-06-01-preview' = {
  name: '${ml_workspace_name}/jaxserving/${environment_version}'
  // parent: serving_base_environment
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
  name: '${ml_workspace_name}/alphabrain-online-endpoint'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    authMode: 'AMLToken'
    traffic: {}
  }
}
