from fastapi import FastAPI
from app.routers.analytics import router as analyse_router
from app.routers.export import router as export_router


app = FastAPI()

app.include_router(analyse_router)
app.include_router(export_router)
