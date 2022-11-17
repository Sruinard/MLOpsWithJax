#!/bin/bash

CONTAINER_NAME=$1
RESOURCE_GROUP=$2
CONTAINER_MLOPS_NAME=$3

az acr login --name $CONTAINER_NAME


SUBSCRIPTION_ID=$(az account show --query id --output tsv)
RESOURCE_GROUP=$RESOURCE_GROUP
AZUREML_WORKSPACE_NAME=$(az ml workspace list --resource-group=$RESOURCE_GROUP --query "[].{name: name}" --output tsv)
TRAIN_ENV='jaxtraining'
COMPUTE_CLUSTER='cpu-cluster'
AZUREML_ONLINE_ENDPOINT=$(az ml online-endpoint list --resource-group=$RESOURCE_GROUP --workspace-name=$AZUREML_WORKSPACE_NAME --query '[].name' --output tsv)


echo $SUBSCRIPTION_ID
echo $AZUREML_WORKSPACE_NAME
echo $AZUREML_ONLINE_ENDPOINT

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



az acr login --name $CONTAINER_MLOPS_NAME
docker tag microbrain $CONTAINER_MLOPS_NAME.azurecr.io/jaxtraining:latest
docker push $CONTAINER_MLOPS_NAME.azurecr.io/jaxtraining:latest