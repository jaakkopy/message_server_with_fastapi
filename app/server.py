from fastapi import FastAPI
from app.routers import auth, messages

app = FastAPI()
app.include_router(auth.router)
app.include_router(messages.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
