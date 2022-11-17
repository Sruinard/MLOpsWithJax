FROM python:3.8.14-bullseye

ARG SUBSCRIPTION_ID
ARG RESOURCE_GROUP
ARG AZUREML_WORKSPACE_NAME

ARG TRAIN_ENV
ARG COMPUTE_CLUSTER 
ARG AZUREML_ONLINE_ENDPOINT


ENV SUBSCRIPTION_ID=${SUBSCRIPTION_ID}
ENV RESOURCE_GROUP=${RESOURCE_GROUP}
ENV AZUREML_WORKSPACE_NAME=${AZUREML_WORKSPACE_NAME}
ENV TRAIN_ENV=${TRAIN_ENV}
ENV COMPUTE_CLUSTER=${COMPUTE_CLUSTER}
ENV AZUREML_ONLINE_ENDPOINT=${AZUREML_ONLINE_ENDPOINT}



WORKDIR /alphabrain
ENV POETRY_HOME=/etc/poetry


RUN apt-get update && apt-get install curl -y
RUN pip install -U pip \
    && curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python3 -

ENV PATH="${POETRY_HOME}/bin:${PATH}"
COPY pyproject.toml poetry.lock ./

# First we install keyrings and authenicate AFTER it. Which is required to access private repositories.
# I believe setting virtualenvs.create to false enables the right python interpreter installs the packages
# (i.e. the one that the dataflow runner will use for its workers).
RUN poetry config virtualenvs.create false \
    && poetry export --without-hashes -f requirements.txt --with dev --output requirements_from_export.txt \
    && poetry run pip install -r requirements_from_export.txt 


COPY alphabrain alphabrain
RUN poetry install --no-interaction

# CMD ["python3", "alphabrain/app.py"]