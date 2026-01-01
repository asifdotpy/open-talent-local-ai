from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.endpoints import interview

app = FastAPI(
    title="OpenTalent - Conversation Service",
    description="""
    AI-powered conversation management for interview automation.

    **Capabilities:**
    - Interview conversation orchestration
    - Natural language processing
    - Context-aware responses
    - Multi-turn dialogue management

    **API Documentation:**
    - Interactive Swagger UI: `/docs`
    - Alternative docs URL: `/doc`
    - ReDoc documentation: `/redoc`
    - OpenAPI schema: `/openapi.json`
    - API endpoints summary: `/api-docs`
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/")
async def root():
    """Service identification endpoint for the Conversation Service.

    Returns:
        A dictionary confirming the service name, version, and documentation links.
    """
    return {
        "message": "Conversation Service is running!",
        "service": "OpenTalent Conversation Service",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "alternative": "/doc",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "api_summary": "/api-docs",
        },
    }


@app.get("/health")
async def health_check():
    """Standard health check endpoint for system monitoring and orchestration.

    Returns:
        A dictionary confirming the service health status.
    """
    return {"status": "healthy"}


@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Redirect alternative documentation path to the standard Swagger UI.

    Returns:
        A RedirectResponse to the /docs endpoint.
    """
    return RedirectResponse(url="/docs")


@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints."""
    routes_info = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, "name", "unknown"),
                "summary": getattr(route, "summary", None) or getattr(route, "description", None),
            }
            routes_info.append(route_info)

    return {
        "service": "OpenTalent Conversation Service API",
        "version": "1.0.0",
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "routes": routes_info,
    }


# Include the router from the interview endpoints
app.include_router(interview.router)

if __name__ == "__main__":
    import os

    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=8002)
