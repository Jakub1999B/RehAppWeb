import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from prediction.reh_app import reh_app, plot_data
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# Database Setup

DATABASE_URL = "sqlite:///trainings.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

import json
import numpy as np
from pandas import DataFrame
from fastapi.encoders import jsonable_encoder


class TrainingRecord(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, default=datetime.utcnow)
    bend = Column(Integer)
    circular_raise = Column(Integer)
    abduction = Column(Integer)
    rear_touch = Column(Integer)
    side_bend = Column(Integer)
    duration = Column(Integer)

Base.metadata.create_all(bind=engine)

# Template Setup
templates = Jinja2Templates(directory="templates")

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, DataFrame):
            return obj.to_dict()
        return super().default(obj)



@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/home.html", "r") as f:
        content = f.read()
    return content

@app.get("/{template}", response_class=HTMLResponse)
async def read_template(template: str):
    if template in ["trainings", "analyze", "exercises", "contact"]:
        with open(f"templates/{template}.html", "r") as f:
            content = f.read()
        return content
    else:
        return "Template not found"

@app.post("/analyzes/")
async def analyze(file: UploadFile = File(...)):
    df, summary_count, duration = reh_app(file.file)
    encoded_content = json.dumps(df, cls=CustomJSONEncoder)
    f = pd.read_excel(file.file)

    # Example of how to insert records into the database
    new_record = TrainingRecord(
        bend=summary_count.get('BEND', 0),
        circular_raise=summary_count.get('CIRCULAR_RAISE', 0),
        abduction=summary_count.get('ABDUCTION', 0),
        rear_touch=summary_count.get('REAR_TOUCH', 0),
        side_bend=summary_count.get('SIDE_BEND', 0),
        duration=duration
    )

    db = SessionLocal()
    db.add(new_record)
    db.commit()
    db.close()

    return JSONResponse(content=encoded_content)


from fastapi.responses import HTMLResponse
from fastapi.requests import Request

@app.get("/analyze/", response_class=HTMLResponse)
async def show_analyze_page(request: Request):
    return templates.TemplateResponse("analyze.html", {"request": request})


@app.get("/trainings/", response_class=HTMLResponse)
async def show_trainings(request: Request):
    db = SessionLocal()
    records = db.query(TrainingRecord).all()
    db.close()
    return templates.TemplateResponse("trainings.html", {"request": request, "records": records})



from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import matplotlib.pyplot as plt
import numpy as np


# @app.get("/styles.css")
# async def get_styles():
#     return FileResponse("static/styles.css")
#
# @app.get("/static/logo.png")
# async def get_styles():
#     return FileResponse("static/logo.png")



# @app.get("/load-template/{template_name}", response_class=HTMLResponse)
# async def load_template(template_name: str, request: Request):
#     templates_old = Jinja2Templates(directory="templates_old")
#     print(templates_old)
#     print(template_name)
#     print(templates_old.TemplateResponse(f"{template_name}.html", {"request": request}))
#     return templates_old.TemplateResponse(f"{template_name}.html", {"request": request})



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)