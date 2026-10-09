from routes.routes import route
from fastapi import FastAPI
import uvicorn
from database.db import engine, Base
import database.models 


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Certificate Generator"
)

app.include_router(route)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
