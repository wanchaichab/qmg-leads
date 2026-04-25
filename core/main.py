from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from api.admin import router as admin_router  # adjust path if needed
from fastapi.responses import FileResponse


app = FastAPI()
app.include_router(admin_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")