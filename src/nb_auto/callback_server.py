from __future__ import annotations

from fastapi import FastAPI, Request

from .config import load_settings
from .kie_client import KieClient
from .storage import download_urls, upsert_task

app = FastAPI(title="Nano Banana Pro Callback Receiver")


@app.post("/api/callback")
async def kie_callback(request: Request):
    payload = await request.json()
    settings = load_settings()
    client = KieClient(api_key=settings.api_key, base_url=settings.base_url)

    data = payload.get("data", payload)
    task_id = data.get("taskId") or data.get("task_id") or "unknown-task"
    state = data.get("state", "callback")

    upsert_task(settings.db_path, task_id, state=state, response=payload)

    urls = client.extract_result_urls(payload)
    downloaded = []
    if urls:
        downloaded = [str(p) for p in download_urls(urls, settings.output_dir, prefix=task_id)]

    return {"ok": True, "taskId": task_id, "downloaded": downloaded}
