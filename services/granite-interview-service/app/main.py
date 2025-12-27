"""
OpenTalent Granite Interview Service - Main Application

Modular AI service supporting multiple model architectures for interview intelligence.
Supports Granite, Llama, Mistral, and other models with fine-tuning capabilities.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import uvicorn
from app.config.settings import Settings
from app.services.inference_engine import InferenceEngine
from app.services.model_loader import ModelLoader
from app.services.model_registry import ModelRegistry
from app.services.training_service import TrainingService
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global service instances
model_registry = None
model_loader = None
inference_engine = None
training_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global model_registry, model_loader, inference_engine, training_service

    logger.info("Starting Granite Interview Service...")

    # Initialize services
    settings = Settings()
    model_registry = ModelRegistry(settings)
    model_loader = ModelLoader(settings, model_registry)
    inference_engine = InferenceEngine(settings, model_loader)
    training_service = TrainingService(settings, model_registry)

    # Load default model if specified
    if settings.default_model:
        try:
            await model_loader.load_model(settings.default_model)
            logger.info(f"Loaded default model: {settings.default_model}")
        except Exception as e:
            logger.warning(f"Failed to load default model {settings.default_model}: {e}")

    logger.info("Granite Interview Service started successfully")

    yield

    # Shutdown cleanup
    logger.info("Shutting down Granite Interview Service...")
    await model_loader.unload_all_models()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="OpenTalent Granite Interview Service",
    description="Modular AI service supporting multiple model architectures for interview intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---


class ModelInfo(BaseModel):
    """Model information response."""

    name: str
    architecture: str
    size: str
    quantization: str
    status: str
    loaded_at: datetime | None = None
    memory_usage: str | None = None


class LoadModelRequest(BaseModel):
    """Request to load a model."""

    model_name: str = Field(..., description="Name of the model to load")
    quantization: str = Field("4bit", description="Quantization level (4bit, 8bit, 16bit)")
    device: str = Field("auto", description="Device to load on (auto, cpu, cuda)")


class InterviewContext(BaseModel):
    """Interview context for question generation."""

    job_title: str
    skills: list[str]
    difficulty: str = "intermediate"
    previous_questions: list[str] = Field(default_factory=list)
    company_culture: list[str] = Field(default_factory=list)
    interview_phase: str = "general"


class CandidateProfile(BaseModel):
    """Candidate profile information."""

    experience_years: int
    current_role: str
    skills: list[str] = Field(default_factory=list)
    education_level: str = "bachelors"


class GenerateQuestionRequest(BaseModel):
    """Request to generate an interview question."""

    model_name: str
    context: InterviewContext
    candidate_profile: CandidateProfile
    temperature: float = Field(0.7, description="Sampling temperature")
    max_tokens: int = Field(256, description="Maximum tokens to generate")


class AnalyzeResponseRequest(BaseModel):
    """Request to analyze a candidate response."""

    model_name: str
    question: str
    response: str
    context: dict[str, Any] = Field(default_factory=dict)


class FineTuneRequest(BaseModel):
    """Request to fine-tune a model."""

    base_model: str
    training_data: str
    config: dict[str, Any] = Field(default_factory=dict)


class TrainingStatus(BaseModel):
    """Training status response."""

    job_id: str
    status: str
    progress: float
    eta: str | None = None
    current_epoch: int = 0
    total_epochs: int = 0


# --- API Endpoints ---


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "OpenTalent Granite Interview Service",
        "version": "1.0.0",
        "description": "Modular AI service for interview intelligence",
        "models_loaded": len(model_loader.loaded_models) if model_loader else 0,
        "supported_architectures": ["granite", "llama", "mistral"],
        "endpoints": {
            "models": "/api/v1/models",
            "interview": "/api/v1/interview",
            "training": "/api/v1/training",
        },
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        # Check model registry
        models_status = "healthy" if model_registry else "unhealthy"

        # Check loaded models
        loaded_count = len(model_loader.loaded_models) if model_loader else 0

        # GPU status (if available)
        gpu_info = {}
        try:
            import torch

            if torch.cuda.is_available():
                gpu_info = {
                    "cuda_available": True,
                    "device_count": torch.cuda.device_count(),
                    "current_device": torch.cuda.current_device(),
                    "device_name": torch.cuda.get_device_name(),
                }
            else:
                gpu_info = {"cuda_available": False}
        except ImportError:
            gpu_info = {"cuda_available": False, "error": "torch not available"}

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "model_registry": models_status,
                "model_loader": "healthy" if model_loader else "unhealthy",
                "inference_engine": "healthy" if inference_engine else "unhealthy",
                "training_service": "healthy" if training_service else "unhealthy",
            },
            "models": {
                "loaded_count": loaded_count,
                "available_count": len(model_registry.models) if model_registry else 0,
            },
            "hardware": gpu_info,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# --- Model Management Endpoints ---


@app.get("/api/v1/models", response_model=list[ModelInfo])
async def list_models():
    """List all available models and their status."""
    if not model_registry:
        raise HTTPException(status_code=503, detail="Model registry not available")

    models = []
    for name, config in model_registry.models.items():
        status = "loaded" if name in model_loader.loaded_models else "available"
        loaded_at = None
        memory_usage = None

        if status == "loaded":
            model_instance = model_loader.loaded_models.get(name)
            if model_instance:
                loaded_at = getattr(model_instance, "loaded_at", None)
                memory_usage = getattr(model_instance, "memory_usage", None)

        models.append(
            ModelInfo(
                name=name,
                architecture=config.get("architecture", "unknown"),
                size=config.get("size", "unknown"),
                quantization=config.get("quantization", "unknown"),
                status=status,
                loaded_at=loaded_at,
                memory_usage=memory_usage,
            )
        )

    return models


@app.post("/api/v1/models/load")
async def load_model(request: LoadModelRequest):
    """Load a model into memory."""
    try:
        await model_loader.load_model(
            request.model_name, quantization=request.quantization, device=request.device
        )
        return {"message": f"Model {request.model_name} loaded successfully"}
    except Exception as e:
        logger.error(f"Failed to load model {request.model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")


@app.delete("/api/v1/models/{model_name}")
async def unload_model(model_name: str):
    """Unload a model from memory."""
    try:
        await model_loader.unload_model(model_name)
        return {"message": f"Model {model_name} unloaded successfully"}
    except Exception as e:
        logger.error(f"Failed to unload model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")


@app.get("/api/v1/models/{model_name}/status")
async def get_model_status(model_name: str):
    """Get detailed status of a specific model."""
    if model_name not in model_loader.loaded_models:
        return {"status": "not_loaded"}

    model_instance = model_loader.loaded_models[model_name]
    return {
        "status": "loaded",
        "loaded_at": getattr(model_instance, "loaded_at", None),
        "memory_usage": getattr(model_instance, "memory_usage", None),
        "device": getattr(model_instance, "device", None),
        "quantization": getattr(model_instance, "quantization", None),
    }


# --- Interview Intelligence Endpoints ---


@app.post("/api/v1/interview/generate-question")
async def generate_interview_question(request: GenerateQuestionRequest):
    """Generate an interview question using the specified model."""
    try:
        # Check if model is loaded
        if request.model_name not in model_loader.loaded_models:
            raise HTTPException(status_code=400, detail=f"Model {request.model_name} not loaded")

        # Generate question
        result = await inference_engine.generate_question(
            model_name=request.model_name,
            context=request.context,
            candidate_profile=request.candidate_profile,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return result

    except Exception as e:
        logger.error(f"Failed to generate question: {e}")
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")


@app.post("/api/v1/interview/analyze-response")
async def analyze_candidate_response(request: AnalyzeResponseRequest):
    """Analyze a candidate's response to an interview question."""
    try:
        # Check if model is loaded
        if request.model_name not in model_loader.loaded_models:
            raise HTTPException(status_code=400, detail=f"Model {request.model_name} not loaded")

        # Analyze response
        result = await inference_engine.analyze_response(
            model_name=request.model_name,
            question=request.question,
            response=request.response,
            context=request.context,
        )

        return result

    except Exception as e:
        logger.error(f"Failed to analyze response: {e}")
        raise HTTPException(status_code=500, detail=f"Response analysis failed: {str(e)}")


# --- Training Endpoints ---


@app.post("/api/v1/training/fine-tune")
async def start_fine_tuning(request: FineTuneRequest, background_tasks: BackgroundTasks):
    """Start fine-tuning a model."""
    try:
        job_id = await training_service.start_fine_tuning(
            base_model=request.base_model,
            training_data=request.training_data,
            config=request.config,
        )

        # Add to background tasks if async training
        # background_tasks.add_task(training_service.monitor_training, job_id)

        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Fine-tuning started for {request.base_model}",
        }

    except Exception as e:
        logger.error(f"Failed to start fine-tuning: {e}")
        raise HTTPException(status_code=500, detail=f"Fine-tuning failed: {str(e)}")


@app.get("/api/v1/training/jobs/{job_id}", response_model=TrainingStatus)
async def get_training_status(job_id: str):
    """Get the status of a training job."""
    try:
        status = await training_service.get_training_status(job_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get training status for {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get training status: {str(e)}")


@app.delete("/api/v1/training/jobs/{job_id}")
async def cancel_training(job_id: str):
    """Cancel a training job."""
    try:
        await training_service.cancel_training(job_id)
        return {"message": f"Training job {job_id} cancelled"}
    except Exception as e:
        logger.error(f"Failed to cancel training {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel training: {str(e)}")


# --- System Endpoints ---


@app.get("/api/v1/system/gpu")
async def get_gpu_status():
    """Get GPU usage information."""
    try:
        import torch

        if not torch.cuda.is_available():
            return {"cuda_available": False}

        devices = []
        for i in range(torch.cuda.device_count()):
            devices.append(
                {
                    "device_id": i,
                    "name": torch.cuda.get_device_name(i),
                    "memory_allocated": f"{torch.cuda.memory_allocated(i) / 1024**3:.2f}GB",
                    "memory_reserved": f"{torch.cuda.memory_reserved(i) / 1024**3:.2f}GB",
                    "memory_total": f"{torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f}GB",
                }
            )

        return {
            "cuda_available": True,
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device(),
            "devices": devices,
        }

    except ImportError:
        return {"cuda_available": False, "error": "PyTorch not available"}
    except Exception as e:
        logger.error(f"Failed to get GPU status: {e}")
        raise HTTPException(status_code=500, detail=f"GPU status check failed: {str(e)}")


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("GRANITE_INTERVIEW_PORT", 8005))
    uvicorn.run(app, host=host, port=port)
