from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.analytics import router as analyse_router
from app.routers.export import router as export_router
from app.routers.ai import router as ai_router
from app.core.config import settings


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse_router)
app.include_router(export_router)
app.include_router(ai_router)
