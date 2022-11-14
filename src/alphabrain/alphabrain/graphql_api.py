
import json
import os
import random
from dataclasses import dataclass

import requests
import strawberry
import uvicorn
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from strawberry.asgi import GraphQL

from alphabrain.config import GraphAPIConfig


@strawberry.type
class AdditionProblem:
    digit_1: int
    digit_2: int


@strawberry.type
class InferredSolution:
    inputs: str
    outputs: str
    combined: str


@strawberry.type
class Query:
    # required by Apollo Server
    _service: Optional[str]

    @strawberry.field
    def get_addition_problem_to_solve(self) -> AdditionProblem:
        digit_1, digit_2 = sorted((
            random.randint(0, 99), random.randint(0, 999)))
        return AdditionProblem(digit_1=digit_1, digit_2=digit_2)

    @ strawberry.field
    def hello(self) -> str:
        return "Hello World"


@ strawberry.type
class Mutation:
    @ strawberry.field
    def compute(self, digit_1: int, digit_2: int) -> InferredSolution:
        url = f"{GraphAPIConfig.microbrain_endpoint}/models/brain/predict"
        data = {"body": f"{digit_1}+{digit_2}"}
        predictions = requests.post(url=url, data=json.dumps(data), headers={
                                    'Content-Type': "application/json"}).json()

        return InferredSolution(**predictions)


schema = strawberry.federation.Schema(
    query=Query, mutation=Mutation, types=[AdditionProblem])


graphql_app = GraphQL(schema)

app = FastAPI()

origins = [
    "*",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8081",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

if __name__ == "__main__":
    # run uvicorn on port environment variable PORT or 8000
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8181)))
