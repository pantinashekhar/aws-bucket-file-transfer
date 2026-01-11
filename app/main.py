from fastapi import FastAPI
from api.routes.transfers import router as transfers_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from db.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from api.routes.transfers import router as transfers_router
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from db.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession



app = FastAPI(title="S3 Transfer Service")


# Add after app = FastAPI(...)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



# Add after app = FastAPI(...)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


app.include_router(transfers_router, prefix="/api")

# Add after app.include_router(...)
app.dependency_overrides[get_session] = get_session  # Enable session DI


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})