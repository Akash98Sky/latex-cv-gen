from fastapi import FastAPI

from routers import all_routes
from services.db import prisma


app = FastAPI(
    title="LaTeX-CV-Gen",
    routes=all_routes
)

async def startup():
    await prisma.connect()

async def shutdown():
    await prisma.disconnect()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

@app.get("/")
async def root():
    return {"message": "Hello! Welcome to the LaTeX-CV-Gen API..."}

