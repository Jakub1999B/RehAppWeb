from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import pandas as pd
import numpy as np

app = FastAPI()

app.mount("/static3", StaticFiles(directory="static3"), name="static3")

templates = Jinja2Templates(directory="templates3")

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_contents = await file.read()
    filename = file.filename
    return {"filename": filename, "file_contents": file_contents}

@app.get("/", response_class=HTMLResponse)
async def read_item():
    return templates.TemplateResponse("index.html", {"request": "empty"})

@app.get("/calculateplot/")
async def calculate_and_plot():
    # Simulated data for demonstration purposes
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    data = {"x": x.tolist(), "y": y.tolist()}
    return JSONResponse(content=data)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
