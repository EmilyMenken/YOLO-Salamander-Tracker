import os, shutil, uuid
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
    "status": "idle",
    "progress": 0,
    "job_id": None,
    "metrics": None
}

@app.get("/progress")
def get_progress():
    return JSONResponse(job)


def run_track_job(input_path, output_path, job_id):
    global job

    try:
        job["status"] = "processing"
        job["progress"] = 0
        job["job_id"] = job_id
        job["metrics"] = None

        # pass the shared job dict directly
        metrics = process_video(input_path, output_path, job)

        job["progress"] = 100
        job["status"] = "done"
        job["metrics"] = metrics

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    global job

    job_id = str(uuid.uuid4())

    input_path = f"{UPLOAD_DIR}/{job_id}_input.mp4"
    output_path = f"{OUTPUT_DIR}/{job_id}_output.mp4"

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    job = {
        "status": "starting",
        "progress": 0,
        "job_id": job_id,
        "metrics": None
    }

    thread = Thread(
        target=run_track_job,
        args=(input_path, output_path, job_id)
    )

    thread.start()

    return JSONResponse({
        "status": "started",
        "job_id": job_id
    })


@app.get("/video/{job_id}")
def get_video(job_id: str):
    path = f"{OUTPUT_DIR}/{job_id}_output_web.mp4"
    return FileResponse(path, media_type="video/mp4")