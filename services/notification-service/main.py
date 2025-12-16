from fastapi import FastAPI, Depends, Body
from fastapi.responses import JSONResponse
import os
import sys as _sys

# Ensure local imports work in various loaders
_this_dir = os.path.dirname(__file__)
if _this_dir not in _sys.path:
    _sys.path.append(_this_dir)

# Import from local modules (handles both package and spec loading)
try:
    from .providers import get_provider
except ImportError:
    from providers import get_provider

from schemas import (
    EmailNotificationRequest,
    SMSNotificationRequest,
    PushNotificationRequest,
)

app = FastAPI(title="Notification Service", version="1.0.0")

def provider_dep():
    return get_provider()

@app.get("/")
async def root():
    return {"service": "notification", "status": "ok"}

@app.get("/health")
async def health(p=Depends(provider_dep)):
    status = await p.health()
    top_ok = None
    try:
        top_ok = bool(status.get("ok"))
    except Exception:
        top_ok = None
    return {"service": "notification", "provider": status, "ok": top_ok}

@app.get("/api/v1/provider")
async def provider_info(p=Depends(provider_dep)):
    status = await p.health()
    return status

@app.post("/api/v1/notify/email")
async def notify_email(payload: EmailNotificationRequest = Body(...), p=Depends(provider_dep)):
    # FastAPI will emit 422 for missing/invalid fields; keep behavior-compatible
    if not payload.to or not payload.subject:
        return JSONResponse(status_code=400, content={"error": "Missing 'to' or 'subject'"})
    result = await p.send_email(str(payload.to), payload.subject, payload.html or "", payload.text)
    if isinstance(result, dict):
        result.setdefault("status", "sent")
    return result

@app.post("/api/v1/notify/sms")
async def notify_sms(payload: SMSNotificationRequest = Body(...), p=Depends(provider_dep)):
    if not payload.to or not payload.text:
        return JSONResponse(status_code=400, content={"error": "Missing 'to' or 'text'"})
    result = await p.send_sms(payload.to, payload.text)
    if isinstance(result, dict):
        result.setdefault("status", "sent")
    return result

@app.post("/api/v1/notify/push")
async def notify_push(payload: PushNotificationRequest = Body(...), p=Depends(provider_dep)):
    if not payload.to or not payload.title or not payload.body:
        return JSONResponse(status_code=400, content={"error": "Missing 'to', 'title' or 'body'"})
    result = await p.send_push(payload.to, payload.title, payload.body, payload.data)
    if isinstance(result, dict):
        result.setdefault("status", "sent")
    return result

@app.get("/api/v1/notify/templates")
async def list_templates(p=Depends(provider_dep)):
    return {"data": await p.get_templates()}
