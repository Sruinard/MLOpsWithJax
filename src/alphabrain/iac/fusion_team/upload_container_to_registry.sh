#!/bin/bash

CONTAINER_NAME=$1
az acr login --name $CONTAINER_NAME

docker build -t microbrain ./src/alphabrain/
docker tag microbrain $CONTAINER_NAME.azurecr.io/microbrain:latest
docker push $CONTAINER_NAME.azurecr.io/microbrain:latest


docker build -t jaxserving ./src/alphabrain/alphabrain/mlops/
docker tag jaxserving $CONTAINER_NAME.azurecr.io/jaxserving:latest
docker push $CONTAINER_NAME.azurecr.io/jaxserving:latest