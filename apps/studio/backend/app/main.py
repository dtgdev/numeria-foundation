from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import router as graph_router
from app.routers.creator import router as creator_router
from app.routers.world_creator import router as world_creator_router


app = FastAPI(
    title="Numeria Studio API",
    version="0.3.0",
    description=(
        "Graph-native Creator and World services "
        "for Numeria Studio."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graph_router)
app.include_router(creator_router)
app.include_router(world_creator_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "numeria-studio-api",
        "version": "0.3.0",
    }
