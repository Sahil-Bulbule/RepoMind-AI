import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .models.database import init_db
from .api import routes_github, routes_chat, routes_search, routes_health


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ask_my_github")

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Initializing Ask My GitHub Database...")
    init_db()
    logger.info("Ask My GitHub Backend is ready.")
    yield

    logger.info("Shutting down Ask My GitHub Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Turn any public GitHub profile into a conversational AI knowledge base with RAG.",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled server error on %s (%s)",
        request.url.path,
        type(exc).__name__,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again or check server logs."
        }
    )


app.include_router(routes_health.router)
app.include_router(routes_github.router)
app.include_router(routes_chat.router)
app.include_router(routes_search.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
