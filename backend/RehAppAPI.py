import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from prediction.reh_app import reh_app, plot_data


import json
import numpy as np
from pandas import DataFrame
from fastapi.encoders import jsonable_encoder

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        if isinstance(obj, DataFrame):
            return obj.to_dict()
        return super().default(obj)


templates = Jinja2Templates(directory="templates")


app = FastAPI()

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    df, summary_count, duration = reh_app(file.file)
    encoded_content = json.dumps(df, cls=CustomJSONEncoder)
    f = pd.read_excel(file.file)
    # await plot_data(f)
    # print(encoded_content[0])
    return JSONResponse(content=encoded_content)


    # return df

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import matplotlib.pyplot as plt
import numpy as np

# Calculate data for plot
@app.post("/calculate/")
async def calculate_data(start: float, end: float, num_points: int):
    if num_points <= 0:
        raise HTTPException(status_code=400, detail="Number of points must be greater than 0")

    x = np.linspace(start, end, num_points)
    y = np.sin(x)

    data = {"x": x.tolist(), "y": y.tolist()}
    return data


# Plot data
@app.post("/plot/")
async def plot_data(data: dict):
    x = data.get("x")
    y = data.get("y")

    if x is None or y is None:
        raise HTTPException(status_code=400, detail="Invalid data format")

    plt.figure()
    plt.plot(x, y)
    plt.title("Plot from Calculated Data")
    plot_filename = "plot.png"
    plt.savefig(plot_filename)
    plt.close()

    return FileResponse(plot_filename)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)