from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint for the AI Auditing Service."""
    return {"message": "AI Auditing Service is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint for the AI Auditing Service."""
    return {"status": "healthy"}
