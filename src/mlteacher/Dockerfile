FROM python:3.8.14-bullseye

WORKDIR /mlteacher
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


COPY mlteacher mlteacher
RUN poetry install --no-interaction

CMD ["python3", "mlteacher/app.py"]