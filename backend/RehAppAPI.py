import pandas as pd
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from prediction.reh_app import reh_app, plot_data
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
import contextlib
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import json
from sqlalchemy.orm import Session
from fastapi import Depends
from pandas import DataFrame
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
import os
import tempfile
import matplotlib.pyplot as plt
import numpy as np

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# Database Setup

DATABASE_URL = "sqlite:///trainings.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Template Setup
templates = Jinja2Templates(directory="templates")

from fastapi import Depends

# Define a dependency function to manage the database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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

# @app.get("/{template}", response_class=HTMLResponse)
# async def read_template(template: str):
#     if template in ["analyze", "exercises", "contact"]:
#         with open(f"templates/{template}.html", "r") as f:
#             content = f.read()
#         return content
#     else:
#         return "Template not found"

@app.get("/analyze", response_class=HTMLResponse)
async def show_analyze():
    with open(f"templates/analyze.html", "r") as f:
        content = f.read()
    return content

@app.get("/exercises", response_class=HTMLResponse)
async def show_analyze():
    with open(f"templates/exercises.html", "r") as f:
        content = f.read()
    return content

@app.get("/contact", response_class=HTMLResponse)
async def show_analyze():
    with open(f"templates/contact.html", "r") as f:
        content = f.read()
    return content

# @app.post("/analyzes/")
# async def analyze(file: UploadFile = File(...)):
#     df, summary_count, duration = reh_app(file.file)
#     encoded_content = json.dumps(df, cls=CustomJSONEncoder)
#     f = pd.read_excel(file.file)
#
#     # Example of how to insert records into the database
#     new_record = TrainingRecord(
#         bend=summary_count.get('BEND', 0),
#         circular_raise=summary_count.get('CIRCULAR_RAISE', 0),
#         abduction=summary_count.get('ABDUCTION', 0),
#         rear_touch=summary_count.get('REAR_TOUCH', 0),
#         side_bend=summary_count.get('SIDE_BEND', 0),
#         duration=duration
#     )
#
#     db = SessionLocal()
#     db.add(new_record)
#     db.commit()
#     db.close()
#
#     return JSONResponse(content=encoded_content)

@app.get("/trainings", response_class=HTMLResponse)
async def trainings(request: Request):
    try:
        db = SessionLocal()
        records = db.query(TrainingRecord).all()
        print("Records", records)
        return templates.TemplateResponse(
            request,
            "trainings.html",
            {"records": records},
        )
    except Exception as e:
        print("Error:", e)
        raise
    finally:
        db.close()

#
#
#
# @app.post("/analyzes/", response_class=HTMLResponse)
# async def analyze(request: Request, file: UploadFile = File(...)):
#     try:
#         db = SessionLocal()
#         df, summary_count, duration = reh_app(file.file)
#         encoded_content = json.dumps(summary_count, cls=CustomJSONEncoder)
#
#         new_record = TrainingRecord(
#             bend=summary_count.get('BEND', 0),
#             circular_raise=summary_count.get('CIRCULAR_RAISE', 0),
#             abduction=summary_count.get('ABDUCTION', 0),
#             rear_touch=summary_count.get('REAR_TOUCH', 0),
#             side_bend=summary_count.get('SIDE_BEND', 0),
#             duration=duration
#         )
#
#         db.add(new_record)
#         db.commit()
#
#         return templates.TemplateResponse(
#             "analyze.html",
#             {"request": request, "encoded_content": encoded_content},
#         )
#     except Exception as e:
#         print("Error:", e)
#         raise
#     finally:
#         db.close()

# ... (your existing imports) ...

@app.post("/analyzes/", response_class=JSONResponse)
async def analyze(file: UploadFile = File(...)):
    temp_path = None
    db = None
    try:
        suffix = os.path.splitext(file.filename or "")[1] or ".xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            tmp.write(await file.read())

        db = SessionLocal()
        _, summary_count, duration = reh_app(temp_path)
        encoded_content = jsonable_encoder(summary_count)

        new_record = TrainingRecord(
            bend=summary_count.get('BEND', 0),
            circular_raise=summary_count.get('CIRCULAR_RAISE', 0),
            abduction=summary_count.get('ABDUCTION', 0),
            rear_touch=summary_count.get('REAR_TOUCH', 0),
            side_bend=summary_count.get('SIDE_BEND', 0),
            duration=duration
        )

        db.add(new_record)
        db.commit()
        df = pd.read_excel(temp_path)
        plot_data = {
            "seconds_elapsed": df['seconds_elapsed'].tolist(),
            "acc_x": df["acc_x"].tolist(),
            "acc_y": df["acc_y"].tolist(),
            "acc_z": df["acc_z"].tolist(),
            "gra_x": df["gra_x"].tolist(),
            "gra_y": df["gra_y"].tolist(),
            "gra_z": df["gra_z"].tolist(),
            "gyr_x": df["gyr_x"].tolist(),
            "gyr_y": df["gyr_y"].tolist(),
            "gyr_z": df["gyr_z"].tolist(),
            "ori_x": df["ori_x"].tolist(),
            "ori_y": df["ori_y"].tolist(),
            "ori_z": df["ori_z"].tolist(),
        }

        return {"summary_count": encoded_content, "plot_data": plot_data}
    except Exception as e:
        print("Error:", e)
        raise
    finally:
        if db is not None:
            db.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)