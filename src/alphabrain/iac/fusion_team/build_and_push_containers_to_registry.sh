#!/bin/bash

CONTAINER_NAME=$1
RESOURCE_GROUP=$2

az acr login --name $CONTAINER_NAME


SUBSCRIPTION_ID=${az account show --query id}
RESOURCE_GROUP=$RESOURCE_GROUP
AZUREML_WORKSPACE_NAME=${az ml workspace list --resource-group=$RESOURCE_GROUP --query "[].{name: name}" --output tsv}
TRAIN_ENV=jax_training
COMPUTE_CLUSTER='cpu-cluster'
AZUREML_ONLINE_ENDPOINT=${az ml online-endpoint list --resource-group=csu-nl-fresh-deployment --workspace-name=mb-pf-fpnllumqpjqe2 --query '[].name' --output tsv}


docker build -t microbrain \
    --build-arg SUBSCRIPTION_ID=$SUBSCRIPTION_ID \
    --build-arg RESOURCE_GROUP=$RESOURCE_GROUP \
    --build-arg AZUREML_WORKSPACE_NAME=$AZUREML_WORKSPACE_NAME \
    --build-arg TRAIN_ENV=$TRAIN_ENV \
    --build-arg COMPUTE_CLUSTER=$COMPUTE_CLUSTER \
    --build-arg AZUREML_ONLINE_ENDPOINT=$AZUREML_ONLINE_ENDPOINT \
    .

docker tag microbrain $CONTAINER_NAME.azurecr.io/microbrain:latest
docker push $CONTAINER_NAME.azurecr.io/microbrain:latest

docker build -t gateway ./gateway
docker tag gateway $CONTAINER_NAME.azurecr.io/gateway:latest
docker push $CONTAINER_NAME.azurecr.io/gateway:latest