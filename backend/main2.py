from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import databases
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.orm import sessionmaker
from databases import Database
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./tes.db"

database = Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

files = sqlalchemy.Table(
    "files",
    metadata,
    Column("id", Integer, Sequence("file_id_seq"), primary_key=True),
    Column("filename", String(255)),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class FileUpload(BaseModel):
    file: UploadFile


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    query = files.select()
    result = await database.fetch_all(query)
    return templates.TemplateResponse(
        "index.html", {"request": request, "files": result}
    )


# @app.post("/uploadfile/")
# async def upload_file(file: UploadFile = File(...)):
#     async with database.transaction():
#         query = files.insert().values(filename=file.filename)
#         last_record_id = await database.execute(query)
#
#         file_path = f"static/{last_record_id}_{file.filename}"
#         with open(file_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)
#
#     return {"filename": file.filename}

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    async with database.transaction():
        query = files.insert().values(filename=file.filename)
        last_record_id = await database.execute(query)

        file_path = f"static/{last_record_id}_{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    return JSONResponse(content={"id": last_record_id, "filename": file.filename})



@app.get("/files/{file_id}/")
async def read_file(file_id: int):
    query = files.select().where(files.c.id == file_id)
    result = await database.fetch_one(query)

    if result:
        file_path = f"static/{result['id']}_{result['filename']}"
        return FileResponse(file_path, media_type="application/octet-stream")

    return {"error": "File not found"}

from fastapi.responses import HTMLResponse

@app.get("/files/{file_id}/content", response_class=HTMLResponse)
async def read_file_content(file_id: int):
    query = files.select().where(files.c.id == file_id)
    result = await database.fetch_one(query)

    if result:
        file_path = f"static/{result['id']}_{result['filename']}"
        try:
            with open(file_path, "r") as f:
                file_content = f.read()
            return templates.TemplateResponse(
                "file_table_content.html", {"request": None, "file_content": file_content}
            )
        except FileNotFoundError:
            return templates.TemplateResponse(
                "file_table_content.html", {"request": None, "file_content": "File not found"}
            )

    return templates.TemplateResponse(
        "file_table_content.html", {"request": None, "file_content": "File not found"}
    )




from fastapi.responses import JSONResponse


@app.delete("/files/{file_id}/")
async def delete_file(file_id: int):
    query = files.select().where(files.c.id == file_id)
    result = await database.fetch_one(query)

    if result:
        file_path = f"static/{result['id']}_{result['filename']}"
        try:
            os.remove(file_path)
        except OSError as e:
            return JSONResponse(content={"error": f"Error deleting file: {e}"}, status_code=500)

        async with database.transaction():
            query = files.delete().where(files.c.id == file_id)
            await database.execute(query)

        return JSONResponse(content={"message": "File deleted successfully"})

    return JSONResponse(content={"error": "File not found"}, status_code=404)


from fastapi.responses import HTMLResponse

from fastapi import Depends


from fastapi.responses import JSONResponse

# ... (other imports and code)

@app.get("/files/{file_id}/table-content", response_class=HTMLResponse)
async def read_file_table_content(file_id: int, request: Request):
    query = files.select().where(files.c.id == file_id)
    result = await database.fetch_one(query)

    if result:
        file_path = f"static/{result['id']}_{result['filename']}"
        try:
            with open(file_path, "r") as f:
                file_content = f.readlines()
            file_content_lines = [(line_number + 1, line.strip()) for line_number, line in enumerate(file_content)]
            return templates.TemplateResponse(
                "file_table_content.html", {"request": request, "file_content_lines": file_content_lines}
            )
        except FileNotFoundError:
            return templates.TemplateResponse(
                "file_table_content.html", {"request": request, "file_content_lines": [(1, "File not found")]}
            )
        except Exception as e:
            return templates.TemplateResponse(
                "file_table_content.html", {"request": request, "file_content_lines": [(1, f"Error: {e}")]}
            )

    return templates.TemplateResponse(
        "file_table_content.html", {"request": request, "file_content_lines": [(1, "File not found")]}
    )





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
