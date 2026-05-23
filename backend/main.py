import os, shutil, uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tracker import process_video

import asyncio
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

current_progress = {"progress": 0}

@app.get("/progress")
def get_progress():
    return JSONResponse(current_progress)

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    global current_progress
    current_progress = {"progress": 0}

    job_id = str(uuid.uuid4())
    input_path = f"{UPLOAD_DIR}/{job_id}_input.mp4"
    output_path = f"{OUTPUT_DIR}/{job_id}_output.mp4"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    metrics = await run_in_threadpool(process_video, input_path, output_path, current_progress)
    return JSONResponse({"job_id": job_id, "metrics": metrics})

@app.get("/video/{job_id}")
def get_video(job_id: str):
    path = f"outputs/{job_id}_output_web.mp4"
    return FileResponse(path, media_type="video/mp4")