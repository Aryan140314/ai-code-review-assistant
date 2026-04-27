from fastapi import FastAPI
from routes.analyze import router

app = FastAPI(title="AI Code Review Assistant")

app.include_router(router)