from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from api.admin import router as admin_router  # adjust path if needed
from fastapi.responses import FileResponse
from api.endpoints.webhooks import router as webhook_router
from core.messaging import sendSlackNotification 


app = FastAPI()
app.include_router(admin_router)
app.include_router(webhook_router)  # include other routers as needed

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")