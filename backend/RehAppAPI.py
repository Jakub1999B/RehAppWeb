from fastapi import FastAPI, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from prediction.reh_app import reh_app
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
    df = reh_app(file.file)
    encoded_content = json.dumps(df, cls=CustomJSONEncoder)
    return JSONResponse(content=encoded_content)

    return df


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)