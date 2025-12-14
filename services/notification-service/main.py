from fastapi import FastAPI, Depends, Body
from fastapi.responses import JSONResponse
from .providers import get_provider

app = FastAPI(title="Notification Service", version="1.0.0")

def provider_dep():
    return get_provider()

@app.get("/")
async def root():
    return {"service": "notification", "status": "ok"}

@app.get("/health")
async def health(p=Depends(provider_dep)):
    status = await p.health()
    return {"service": "notification", "provider": status}

@app.get("/api/v1/provider")
async def provider_info(p=Depends(provider_dep)):
    status = await p.health()
    return status

@app.post("/api/v1/notify/email")
async def notify_email(payload: dict = Body(...), p=Depends(provider_dep)):
    to = payload.get("to")
    subject = payload.get("subject")
    html = payload.get("html", "")
    text = payload.get("text")
    if not to or not subject:
        return JSONResponse(status_code=400, content={"error": "Missing 'to' or 'subject'"})
    return await p.send_email(to, subject, html, text)

@app.post("/api/v1/notify/sms")
async def notify_sms(payload: dict = Body(...), p=Depends(provider_dep)):
    to = payload.get("to")
    text = payload.get("text")
    if not to or not text:
        return JSONResponse(status_code=400, content={"error": "Missing 'to' or 'text'"})
    return await p.send_sms(to, text)

@app.post("/api/v1/notify/push")
async def notify_push(payload: dict = Body(...), p=Depends(provider_dep)):
    to = payload.get("to")
    title = payload.get("title")
    body = payload.get("body")
    data = payload.get("data")
    if not to or not title or not body:
        return JSONResponse(status_code=400, content={"error": "Missing 'to', 'title' or 'body'"})
    return await p.send_push(to, title, body, data)

@app.get("/api/v1/notify/templates")
async def list_templates(p=Depends(provider_dep)):
    return {"data": await p.get_templates()}
