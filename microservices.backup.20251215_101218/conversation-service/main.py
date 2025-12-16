from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api.endpoints import interview

app = FastAPI(
    title="TalentAI - Conversation Service",
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
    openapi_url="/openapi.json"
)

@app.get("/")
async def root():
    """Root endpoint for the Conversation Service."""
    return {
        "message": "Conversation Service is running!",
        "service": "TalentAI Conversation Service",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "alternative": "/doc",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
            "api_summary": "/api-docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for the Conversation Service."""
    return {"status": "healthy"}

@app.get("/doc", include_in_schema=False)
async def doc_redirect():
    """Alternative redirect to API documentation."""
    return RedirectResponse(url="/docs")

@app.get("/api-docs", include_in_schema=False)
async def api_docs_info():
    """Get API documentation information and available endpoints."""
    routes_info = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            route_info = {
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown'),
                "summary": getattr(route, 'summary', None) or getattr(route, 'description', None)
            }
            routes_info.append(route_info)
    
    return {
        "service": "TalentAI Conversation Service API",
        "version": "1.0.0",
        "total_endpoints": len(routes_info),
        "documentation_urls": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "routes": routes_info
    }

# Include the router from the interview endpoints
app.include_router(interview.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
