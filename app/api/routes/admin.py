import os
import boto3
from fastapi import APIRouter, Form, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def check_admin(username: str, password: str):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

# Very naive auth: form → cookie "is_admin"
def get_admin(request: Request):
    if request.cookies.get("is_admin") == "1":
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not check_admin(username, password):
        return templates.TemplateResponse(
            "admin_login.html",
            {"request": request, "error": "Invalid credentials"},
            status_code=400,
        )
    resp = RedirectResponse(url="/admin/panel", status_code=302)
    resp.set_cookie("is_admin", "1", httponly=True)
    return resp

@router.get("/panel")
async def panel(request: Request, _: bool = Depends(get_admin)):
    backend = os.getenv("STORAGE_BACKEND", "local")
    aws_region = os.getenv("AWS_REGION")
    default_bucket = os.getenv("AWS_S3_DEFAULT_BUCKET")

    buckets = []
    if backend == "s3":
        s3 = boto3.client("s3")
        res = s3.list_buckets()  # simple sanity check [web:117]
        buckets = [b["Name"] for b in res.get("Buckets", [])]

    return templates.TemplateResponse(
        "admin_panel.html",
        {
            "request": request,
            "backend": backend,
            "aws_region": aws_region,
            "default_bucket": default_bucket,
            "buckets": buckets,
        },
    )
