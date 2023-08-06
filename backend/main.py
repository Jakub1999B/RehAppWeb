from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, Response  # Add this import
from fastapi.staticfiles import StaticFiles
import sqlite3
from fastapi.templating import Jinja2Templates
import openpyxl
import tempfile
from starlette.requests import Request
from starlette.responses import FileResponse
import os

app = FastAPI()

# Configure static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize the database table
def initialize_database():
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, content BLOB)"
    )
    conn.commit()
    conn.close()

initialize_database()



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith(".xlsx"):
        content = await file.read()
        conn = sqlite3.connect("mydatabase.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (filename, content) VALUES (?, ?)", (file.filename, content))
        conn.commit()
        conn.close()

        return {"filename": file.filename, "message": "File uploaded successfully"}
    else:
        return {"error": "Only Excel files (.xlsx) are allowed"}


@app.get("/file/{file_id}/")
async def display_file(file_id: int, request: Request):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT filename, content FROM files WHERE id = ?", (file_id,))
    filename, content = cursor.fetchone()
    conn.close()

    if filename.endswith(".xlsx"):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        temp_file.write(content)
        temp_file.close()

        wb = openpyxl.load_workbook(filename=temp_file.name, data_only=True)
        ws = wb.active
        rows = ws.iter_rows(values_only=True)
        header, *data = rows

        return templates.TemplateResponse(
            "excel_table.html",
            {"request": request, "filename": filename, "header": header, "data": data,
             "list_files_url": app.url_path_for("list_files")}
        )
    else:
        return Response(
            content, media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )


@app.delete("/file/{file_id}/")
async def delete_file(file_id: int):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()

    # Get the filename associated with the file_id
    cursor.execute("SELECT filename FROM files WHERE id = ?", (file_id,))
    filename = cursor.fetchone()[0]

    # Delete the file from the database
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    conn.commit()
    conn.close()

    # Delete the file from the filesystem (assuming it's stored in the 'static' directory)
    file_path = f"static/{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": f"File with file_id {file_id} deleted successfully"}


@app.get("/list_files/", response_class=HTMLResponse)
async def list_files(request: Request):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename FROM files")
    files = [{"id": file_id, "filename": filename} for file_id, filename in cursor.fetchall()]
    conn.close()

    return templates.TemplateResponse("list_files.html", {"request": request, "files": files})



