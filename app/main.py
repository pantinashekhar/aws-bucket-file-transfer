from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from db.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.routes.transfers import router as transfers_router
from api.routes.files import router as files_router
from db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="S3 Transfer Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transfers_router, prefix="/api", tags=["transfers"])
app.include_router(files_router, prefix="/api", tags=["files"])

# Add after app = FastAPI(...)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



# Add after app.include_router(...)
app.dependency_overrides[get_session] = get_session  # Enable session DI


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    return {"status": "ok"}

   