from fastapi import FastAPI
from api.routes import files

app = FastAPI(title="S3 Transfer Service")

app.include_router(files.router, prefix="/api")
