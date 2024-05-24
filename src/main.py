import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.worker import session
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# @app.post("/upload")
# async def upload_file(file: UploadFile):
#     content = await file.read()
#     async with aiofiles.open(f"static/{file.filename}", "wb") as f:
#         await f.write(content)

class SessionDTO(BaseModel):
    filename: str
@app.post("/session/start")
async def session_start(data: SessionDTO):
    task = session.delay(data.filename)
    return task.id

@app.get("/session/{task_id}")
async def get_session(task_id):
    task_result = session.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result

@app.delete("/session/{task_id}")
async def delete_session(task_id):
    task_result = session.AsyncResult(task_id)
    task_result.abort()
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return result

@app.delete("/file/{filename}")
async def delete_file(filename):
    os.remove(f"static/{filename}")
