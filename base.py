import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run(app, port="5000")