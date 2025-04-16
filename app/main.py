from fastapi import FastAPI
from webhook import router as webhook_router
from db import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

app.include_router(webhook_router, prefix="/webhook")
