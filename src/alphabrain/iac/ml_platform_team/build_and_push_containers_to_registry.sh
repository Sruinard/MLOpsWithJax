#!/bin/bash

CONTAINER_MLOPS_NAME=$1

az acr login --name $CONTAINER_MLOPS_NAME

docker build -t jaxserving ./iac/ml_platform_team/
docker tag jaxserving $CONTAINER_MLOPS_NAME.azurecr.io/jaxserving:latest
docker push $CONTAINER_MLOPS_NAME.azurecr.io/jaxserving:latest