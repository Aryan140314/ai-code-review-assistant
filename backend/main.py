from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.analyze import router
from database.db import engine, Base

# Create the database tables if they do not exist.
# SQLite will create the local file automatically.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Code Review Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"status": "AI Code Review API is running"}