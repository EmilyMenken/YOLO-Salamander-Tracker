import os
import shutil
import uuid
import time

from threading import Thread

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from tracker import process_video

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

job = {
    "status": "idle"
}


@app.get("/track")
def get_track():
    return JSONResponse(job)


def run_track_job(input_path, output_path, job_id):
    global job

    try:
        metrics = process_video(
            input_path,
            output_path,
            job
        )

        job.clear()

        job["status"] = "done"
        job["percent"] = 100

        job["result"] = {
            "video_url": f"http://localhost:8000/video/{job_id}?t={int(time.time())}",
            "metrics": metrics
        }

    except Exception as e:
        print(f"error: {e}", flush=True)

        job.clear()

        job["status"] = "error"
        job["message"] = str(e)


@app.post("/track")
async def start_track(video: UploadFile = File(...)):
    global job

    job_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{job_id}_input.mp4"
    output_path = f"{OUTPUT_DIR}/{job_id}_output.mp4"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    job.clear()

    job["status"] = "processing"
    job["percent"] = 0
    job["job_id"] = job_id

    Thread(
        target=run_track_job,
        args=(input_path, output_path, job_id),
        daemon=True
    ).start()

    return JSONResponse({
        "status": "processing"
    })


@app.get("/video/{job_id}")
def get_video(job_id: str):
    path = f"{OUTPUT_DIR}/{job_id}_output_web.mp4"

    return FileResponse(
        path,
        media_type="video/mp4"
    )