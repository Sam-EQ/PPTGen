from fastapi import FastAPI, UploadFile, File
import uuid
import shutil
from pathlib import Path
from config import TEMP_DIR
from core.pipeline import _PIPELINE

app = FastAPI()

@app.post("/extract")
async def extract_markdown(file: UploadFile = File(...)):
    req_id = uuid.uuid4().hex
    pdf_path = TEMP_DIR / f"{req_id}_{file.filename}"
    
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    try:
        markdown = await _PIPELINE.process_pdf(pdf_path)
        return {"markdown": markdown}
    finally:
        if pdf_path.exists():
            pdf_path.unlink()