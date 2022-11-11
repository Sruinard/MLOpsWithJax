#!/bin/bash

CONTAINER_NAME=$1

az acr login --name $CONTAINER_NAME

docker build -t microbrain .
docker tag microbrain $CONTAINER_NAME.azurecr.io/microbrain:latest
docker push $CONTAINER_NAME.azurecr.io/microbrain:latest