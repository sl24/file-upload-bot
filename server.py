import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

UPLOAD_DIR = "uploads"

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден.")

    return FileResponse(file_path, filename=filename, media_type='application/octet-stream')
