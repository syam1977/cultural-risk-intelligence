"""FastAPI アプリケーションのエントリーポイント."""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from google import genai
from google.genai.types import HttpOptions

from app.live_session import router as live_router, init_clients

app = FastAPI(title="Cultural Risk Intelligence")

app.include_router(live_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup():
    project = os.environ["GOOGLE_CLOUD_PROJECT"]

    live_client = genai.Client(
        vertexai=True,
        project=project,
        location=os.environ.get("GOOGLE_CLOUD_LIVE_LOCATION", "us-central1"),
        http_options=HttpOptions(api_version="v1beta1"),
    )
    analysis_client = genai.Client(
        vertexai=True,
        project=project,
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    )
    init_clients(live_client, analysis_client)


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=True)
