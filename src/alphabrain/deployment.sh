az ml online-endpoint create --name mlpatterns-endpoint -f serving-endpoint.yaml -g csu-nl-intelligence -w mlpatterns
az ml online-deployment create --name tfwithjax --endpoint mlpatterns-endpoint -f serving-deployment.yaml --all-traffic -g csu-nl-intelligence -w mlpatterns


az acr login --name alphabraincrauofwmqbg5jr2 
docker build -t jaxserving .
docker tag jaxserving alphabraincrauofwmqbg5jr2.azurecr.io/jaxserving
docker push alphabraincrauofwmqbg5jr2.azurecr.io/jaxserving

az deployment group create --resource-group csu-nl-innovative-ml-apps --template-file=iac/ml_platform.bicep
az deployment group create --resource-group csu-nl-innovative-ml-apps --template-file=iac/mlops.bicep --parameters image_uri=csu-nl-innovative-ml-apps --parameters ml_workspace_name=alphabrain-platform-auofwmqbg5jr2