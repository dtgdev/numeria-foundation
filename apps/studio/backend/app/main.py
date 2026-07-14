from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import router as graph_router


app = FastAPI(
    title="Numeria Studio API",
    version="0.1.0",
    description="Graph-native API for the Numeria educational universe.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "numeria-studio-api",
        "version": "0.1.0",
    }
