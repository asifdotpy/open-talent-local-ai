from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint for the Notification Service."""
    return {"message": "Notification Service is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint for the Notification Service."""
    return {"status": "healthy"}