from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.cities import router as cities_router

app = FastAPI(title="Weather Enrichment Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cities_router)
