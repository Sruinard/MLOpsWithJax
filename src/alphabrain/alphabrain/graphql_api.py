
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import uvicorn
import pathlib
import os
import strawberry
from strawberry.fastapi import GraphQLRouter


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"


@strawberry.type
class Mutation:
    @strawberry.field
    def compute(self, digit_1: str, digit_2: str) -> str:
        return f"{digit_1}+{digit_2}={int(digit_1) + int(digit_2)}"

    def find_similarity(self, query: str) -> [str]:
        print(query)
        return ["doc_id_1", "doc_id_2"]


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_app = GraphQLRouter(schema)

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
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    # run uvicorn on port environment variable PORT or 8000
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
