from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from fastapi.responses import HTMLResponse

from fastapi import Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
import os
import pandas as pd
from typing import List

app = FastAPI()


# Create an SQLite database connection
conn = sqlite3.connect("mydatabase2.db")
cursor = conn.cursor()

# Define a table to store file data
cursor.execute('''CREATE TABLE IF NOT EXISTS files
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                content BLOB NOT NULL)''')
conn.commit()


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    if file.filename.endswith(".xlsx"):
        content = await file.read()
        cursor.execute("INSERT INTO files (filename, content) VALUES (?, ?)", (file.filename, content))
        conn.commit()
        return {"filename": file.filename, "message": "File uploaded successfully"}
    else:
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx) are allowed")


@app.get("/files/")
async def list_files():
    cursor.execute("SELECT id, filename FROM files")
    files = cursor.fetchall()
    return files


@app.get("/files/{file_id}/")
async def show_file(file_id: int):
    cursor.execute("SELECT filename, content FROM files WHERE id=?", (file_id,))
    file_data = cursor.fetchone()
    if not file_data:
        raise HTTPException(status_code=404, detail="File not found")

    df = pd.read_excel(file_data[1])
    return df.to_dict()


@app.get("/upload/{file_id}/")
async def delete_file(file_id: int):
    try:
        cursor.execute("SELECT filename FROM files WHERE id=?", (file_id,))
        filename = cursor.fetchone()
        if not filename:
            raise HTTPException(status_code=404, detail="File not found")

        cursor.execute("DELETE FROM files WHERE id=?", (file_id,))
        conn.commit()
        return {"message": f"File {filename[0]} deleted successfully"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the File Upload App"}



import sqlite3

def get_all_files():
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename FROM files")
    files = cursor.fetchall()
    conn.close()
    return files

@app.get("/upload/")
async def upload_page(request: Request):
    files = get_all_files()  # Implement your function to fetch all files from the database
    return templates.TemplateResponse("upload2.html", {"request": request, "files": files})





# Add more routes as needed

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
