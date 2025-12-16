"""
Modular LLM Service for TalentAI Platform

This service provides a unified interface for different LLM providers:
- Ollama (local models like granite4:350m-h)
- OpenAI API (GPT models)
- Future: Anthropic Claude, Google Gemini, etc.

The service uses a strategy pattern to allow easy switching between providers
based on configuration, with fallback mechanisms for reliability.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import httpx
from datetime import datetime, timedelta

# Configure logging early (before any usage)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add PEFT and transformers imports
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    from peft import PeftModel, PeftConfig
    import torch
    PEFT_AVAILABLE = True
except ImportError:
    PEFT_AVAILABLE = False
    logger.warning("PEFT/transformers not available. PEFT provider will not be functional.")

class LLMProvider(Enum):
    """Available LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    PEFT = "peft"  # PEFT/LoRA models
    VLLM = "vllm"  # vLLM server
    MOCK = "mock"  # For testing/development

@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 300
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    fallback_provider: Optional[LLMProvider] = None
    lora_adapter: Optional[str] = None  # For vLLM LoRA adapters

class LLMResponse:
    """Standardized response from LLM providers."""
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.provider_used = None
        self.tokens_used = None
        self.processing_time = None

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using the LLM provider."""
        pass

    @abstractmethod
    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate structured JSON output."""
        pass

    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation for real-time responses."""
        pass

    async def health_check(self) -> bool:
        """Check if the provider is healthy and available."""
        try:
            # Simple health check - try a minimal prompt
            response = await self.generate("Hello", max_tokens=10)
            return len(response.content.strip()) > 0
        except Exception as e:
            logger.warning(f"Health check failed for {self.__class__.__name__}: {e}")
            return False

class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLM models."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=config.base_url or "http://localhost:11434",
            timeout=httpx.Timeout(config.timeout)
        )
        self.current_model = config.model  # Allow dynamic model switching

    def switch_persona(self, persona_model: str):
        """Switch to a different persona model (must share same base model)."""
        self.current_model = persona_model
        logger.info(f"Switched to persona model: {persona_model}")

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using Ollama."""
        start_time = datetime.now()

        try:
            payload = {
                "model": self.current_model,  # Use current persona model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.temperature),
                    "num_predict": kwargs.get('max_tokens', self.config.max_tokens or 2048)
                }
            }

            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()

            result = response.json()
            content = result.get("response", "")

            processing_time = (datetime.now() - start_time).total_seconds()

            llm_response = LLMResponse(content)
            llm_response.provider_used = LLMProvider.OLLAMA
            llm_response.processing_time = processing_time
            llm_response.metadata = {
                "model": result.get("model"),
                "done": result.get("done"),
                "context_length": len(result.get("context", []))
            }

            return llm_response

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate JSON using Ollama with format instruction."""
        system_prompt = """
        You are an AI assistant that responds only with valid JSON. Do not include any explanatory text, markdown formatting, or additional content. Your response must be parseable JSON.
        """

        if schema:
            system_prompt += f"\n\nExpected JSON schema: {json.dumps(schema, indent=2)}"

        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        response = await self.generate(full_prompt, **kwargs)

        try:
            return json.loads(response.content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Ollama response: {response.content}")
            raise ValueError(f"Invalid JSON response from Ollama: {e}")

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation from Ollama."""
        try:
            payload = {
                "model": self.current_model,  # Use current persona model
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": kwargs.get('temperature', self.config.temperature),
                    "num_predict": kwargs.get('max_tokens', self.config.max_tokens or 2048)
                }
            }

            async with self.client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data.get("response"):
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider for GPT models."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = httpx.AsyncClient(
            base_url="https://api.openai.com/v1",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=httpx.Timeout(config.timeout)
        )

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using OpenAI."""
        start_time = datetime.now()

        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens or 2048),
                "stream": False
            }

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            result = response.json()
            choice = result["choices"][0]
            content = choice["message"]["content"]

            processing_time = (datetime.now() - start_time).total_seconds()

            llm_response = LLMResponse(content)
            llm_response.provider_used = LLMProvider.OPENAI
            llm_response.processing_time = processing_time
            llm_response.tokens_used = result.get("usage", {}).get("total_tokens")
            llm_response.metadata = {
                "model": result.get("model"),
                "finish_reason": choice.get("finish_reason"),
                "usage": result.get("usage", {})
            }

            return llm_response

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate JSON using OpenAI with structured output."""
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens or 2048),
                "response_format": {"type": "json_object"} if schema else None
            }

            if schema:
                # Add schema information to the prompt
                schema_instruction = f"\n\nRespond with valid JSON matching this schema: {json.dumps(schema, indent=2)}"
                payload["messages"][0]["content"] += schema_instruction

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                return json.loads(content.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from OpenAI response: {content}")
                raise ValueError(f"Invalid JSON response from OpenAI: {e}")

        except Exception as e:
            logger.error(f"OpenAI JSON generation failed: {e}")
            raise

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation from OpenAI."""
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens or 2048),
                "stream": True
            }

            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip() and line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            if data.get("choices"):
                                delta = data["choices"][0].get("delta", {})
                                if delta.get("content"):
                                    yield delta["content"]
                            if data.get("choices", [{}])[0].get("finish_reason"):
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise

class MockProvider(BaseLLMProvider):
    """Mock provider for testing and development."""

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate mock response."""
        import time
        await asyncio.sleep(0.1)  # Simulate processing time

        content = f"Mock response for prompt: {prompt[:50]}..."
        llm_response = LLMResponse(content)
        llm_response.provider_used = LLMProvider.MOCK
        llm_response.processing_time = 0.1
        return llm_response

    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate mock JSON response."""
        return {"mock": True, "prompt": prompt[:50], "response": "Mock JSON response"}

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream mock response."""
        words = f"Mock streaming response for: {prompt[:30]}...".split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.05)

class PEFTProvider(BaseLLMProvider):
    """PEFT/LoRA provider for fine-tuned models."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        if not PEFT_AVAILABLE:
            raise ImportError("PEFT and transformers are required for PEFT provider")

        self.model = None
        self.tokenizer = None
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        """Load the PEFT model and tokenizer."""
        try:
            logger.info(f"Loading PEFT model: {self.config.model}")

            # For packaged models, load directly (already merged)
            # For LoRA models, load base + adapters
            if "packaged" in self.config.model.lower():
                # Load packaged model directly
                logger.info("Loading packaged model (already merged)...")
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.config.model,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )
                self.tokenizer = AutoTokenizer.from_pretrained(self.config.model)
            else:
                # Load base model and LoRA adapters
                logger.info("Loading base model + LoRA adapters...")
                base_model_name = "ibm-granite/granite-3.0-2b-instruct"
                self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)

                # Load base model
                base_model = AutoModelForCausalLM.from_pretrained(
                    base_model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True
                )

                # Load PEFT model (LoRA adapters)
                self.model = PeftModel.from_pretrained(base_model, self.config.model)

            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.float16,
                device_map="auto",
                max_new_tokens=self.config.max_tokens or 2048,
                temperature=self.config.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )

            logger.info("✅ PEFT model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load PEFT model {self.config.model}: {e}")
            raise

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using PEFT model."""
        start_time = datetime.now()

        try:
            # Use asyncio.to_thread for CPU-bound operations
            temperature = kwargs.get('temperature', self.config.temperature)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens or 2048)

            # Update pipeline parameters
            self.pipeline.model.config.temperature = temperature
            self.pipeline.max_new_tokens = max_tokens

            # Generate response
            outputs = await asyncio.to_thread(
                self.pipeline,
                prompt,
                return_full_text=False,
                num_return_sequences=1
            )

            content = outputs[0]['generated_text']
            processing_time = (datetime.now() - start_time).total_seconds()

            llm_response = LLMResponse(content)
            llm_response.provider_used = LLMProvider.PEFT
            llm_response.processing_time = processing_time
            llm_response.metadata = {
                "model": self.config.model,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            return llm_response

        except Exception as e:
            logger.error(f"PEFT generation failed: {e}")
            raise

    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate JSON using PEFT model with format instruction."""
        system_prompt = """
        You are an AI assistant that responds only with valid JSON. Do not include any explanatory text, markdown formatting, or additional content. Your response must be parseable JSON.
        """

        if schema:
            system_prompt += f"\n\nExpected JSON schema: {json.dumps(schema, indent=2)}"

        full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"

        response = await self.generate(full_prompt, **kwargs)

        try:
            return json.loads(response.content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from PEFT response: {response.content}")
            raise ValueError(f"Invalid JSON response from PEFT: {e}")

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation from PEFT model."""
        try:
            temperature = kwargs.get('temperature', self.config.temperature)
            max_tokens = kwargs.get('max_tokens', self.config.max_tokens or 2048)

            # Update pipeline parameters
            self.pipeline.model.config.temperature = temperature
            self.pipeline.max_new_tokens = max_tokens

            # For streaming, we'll generate in chunks
            # This is a simplified implementation - in production you'd want proper streaming
            outputs = await asyncio.to_thread(
                self.pipeline,
                prompt,
                return_full_text=False,
                num_return_sequences=1
            )

            content = outputs[0]['generated_text']
            words = content.split()

            for word in words:
                yield word + " "
                await asyncio.sleep(0.01)  # Small delay to simulate streaming

        except Exception as e:
            logger.error(f"PEFT streaming failed: {e}")
            raise

class VLLMProvider(BaseLLMProvider):
    """vLLM provider for high-performance LLM serving."""

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = httpx.AsyncClient(
            base_url=config.base_url or "http://localhost:8000/v1",
            timeout=httpx.Timeout(config.timeout)
        )
        self.lora_adapter = getattr(config, 'lora_adapter', None)

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using vLLM server."""
        start_time = datetime.now()

        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens or 2048),
                "stream": False
            }

            # Add LoRA adapter if specified
            if self.lora_adapter:
                payload["extra_body"] = {"lora_name": self.lora_adapter}

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            result = response.json()
            choice = result["choices"][0]
            content = choice["message"]["content"]

            processing_time = (datetime.now() - start_time).total_seconds()

            llm_response = LLMResponse(content)
            llm_response.provider_used = LLMProvider.VLLM
            llm_response.processing_time = processing_time
            llm_response.tokens_used = result.get("usage", {}).get("total_tokens")
            llm_response.metadata = {
                "model": result.get("model"),
                "finish_reason": choice.get("finish_reason"),
                "usage": result.get("usage", {}),
                "lora_adapter": self.lora_adapter
            }

            return llm_response

        except Exception as e:
            logger.error(f"vLLM generation failed: {e}")
            raise

    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate JSON using vLLM with structured output."""
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens or 2048),
                "response_format": {"type": "json_object"} if schema else None
            }

            # Add LoRA adapter if specified
            if self.lora_adapter:
                payload["extra_body"] = {"lora_name": self.lora_adapter}

            if schema:
                # Add schema information to the prompt
                schema_instruction = f"\n\nRespond with valid JSON matching this schema: {json.dumps(schema, indent=2)}"
                payload["messages"][0]["content"] += schema_instruction

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            try:
                return json.loads(content.strip())
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from vLLM response: {content}")
                raise ValueError(f"Invalid JSON response from vLLM: {e}")

        except Exception as e:
            logger.error(f"vLLM JSON generation failed: {e}")
            raise

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation from vLLM."""
        try:
            payload = {
                "model": self.config.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get('temperature', self.config.temperature),
                "max_tokens": kwargs.get('max_tokens', self.config.max_tokens or 2048),
                "stream": True
            }

            # Add LoRA adapter if specified
            if self.lora_adapter:
                payload["extra_body"] = {"lora_name": self.lora_adapter}

            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip() and line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])  # Remove "data: " prefix
                            if data.get("choices"):
                                delta = data["choices"][0].get("delta", {})
                                if delta.get("content"):
                                    yield delta["content"]
                            if data.get("choices", [{}])[0].get("finish_reason"):
                                break
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"vLLM streaming failed: {e}")
            raise
    """Main service that manages multiple LLM providers with fallback support."""

    def __init__(self):
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self.primary_provider: Optional[LLMProvider] = None
        self.fallback_provider: Optional[LLMProvider] = None

    def configure_provider(self, config: LLMConfig):
        """Configure a specific LLM provider."""
        if config.provider == LLMProvider.OLLAMA:
            provider = OllamaProvider(config)
        elif config.provider == LLMProvider.OPENAI:
            provider = OpenAIProvider(config)
        elif config.provider == LLMProvider.PEFT:
            provider = PEFTProvider(config)
        elif config.provider == LLMProvider.VLLM:
            provider = VLLMProvider(config)
        elif config.provider == LLMProvider.MOCK:
            provider = MockProvider(config)
        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

        self.providers[config.provider] = provider

        # Set primary provider if not set
        if not self.primary_provider:
            self.primary_provider = config.provider

        # Set fallback if specified
        if config.fallback_provider:
            self.fallback_provider = config.fallback_provider

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate text using primary provider with fallback."""
        return await self._execute_with_fallback("generate", prompt, **kwargs)

    async def generate_json(self, prompt: str, schema: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Generate JSON using primary provider with fallback."""
        return await self._execute_with_fallback("generate_json", prompt, schema=schema, **kwargs)

    async def stream_generate(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream text generation using primary provider with fallback."""
        async for chunk in self._execute_stream_with_fallback("stream_generate", prompt, **kwargs):
            yield chunk

    async def _execute_with_fallback(self, method_name: str, *args, **kwargs):
        """Execute method with fallback to secondary provider."""
        primary = self.providers.get(self.primary_provider)
        if not primary:
            raise ValueError(f"Primary provider {self.primary_provider} not configured")

        try:
            method = getattr(primary, method_name)
            result = await method(*args, **kwargs)
            logger.info(f"Successfully used {self.primary_provider.value} for {method_name}")
            return result
        except Exception as e:
            logger.warning(f"Primary provider {self.primary_provider.value} failed: {e}")

            # Try fallback provider
            if self.fallback_provider and self.fallback_provider in self.providers:
                try:
                    fallback = self.providers[self.fallback_provider]
                    method = getattr(fallback, method_name)
                    result = await method(*args, **kwargs)
                    logger.info(f"Successfully used fallback {self.fallback_provider.value} for {method_name}")
                    return result
                except Exception as fallback_e:
                    logger.error(f"Fallback provider {self.fallback_provider.value} also failed: {fallback_e}")

            raise e

    async def _execute_stream_with_fallback(self, method_name: str, *args, **kwargs):
        """Execute streaming method with fallback."""
        primary = self.providers.get(self.primary_provider)
        if not primary:
            raise ValueError(f"Primary provider {self.primary_provider} not configured")

        try:
            method = getattr(primary, method_name)
            async for chunk in method(*args, **kwargs):
                yield chunk
            logger.info(f"Successfully used {self.primary_provider.value} for streaming {method_name}")
        except Exception as e:
            logger.warning(f"Primary provider {self.primary_provider.value} failed: {e}")

            # Try fallback provider
            if self.fallback_provider and self.fallback_provider in self.providers:
                try:
                    fallback = self.providers[self.fallback_provider]
                    method = getattr(fallback, method_name)
                    async for chunk in method(*args, **kwargs):
                        yield chunk
                    logger.info(f"Successfully used fallback {self.fallback_provider.value} for streaming {method_name}")
                except Exception as fallback_e:
                    logger.error(f"Fallback provider {self.fallback_provider.value} also failed: {fallback_e}")
                    raise fallback_e
            else:
                raise e

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all configured providers."""
        results = {}
        for provider_type, provider in self.providers.items():
            results[provider_type.value] = await provider.health_check()
        return results

    def switch_persona(self, persona_model: str):
        """Switch to a different interviewer persona (Ollama only).

        This switches the model name for the Ollama provider, allowing
        instant persona switching without reloading the base model.
        All personas must share the same base model (granite3.0:2b).

        Args:
            persona_model: Name of the persona model (e.g., 'technical-interviewer')
        """
        ollama_provider = self.providers.get(LLMProvider.OLLAMA)
        if not ollama_provider:
            raise ValueError("Persona switching only available with Ollama provider")

        if not isinstance(ollama_provider, OllamaProvider):
            raise ValueError("Persona switching requires OllamaProvider instance")

        ollama_provider.switch_persona(persona_model)
        logger.info(f"Switched to interviewer persona: {persona_model}")

    def get_current_persona(self) -> str:
        """Get the currently active persona model name."""
        ollama_provider = self.providers.get(LLMProvider.OLLAMA)
        if ollama_provider and isinstance(ollama_provider, OllamaProvider):
            return ollama_provider.current_model
        return "unknown"

# ---------------------------------------------------------------------------
# Minimal service orchestrator
# ---------------------------------------------------------------------------

class ModularLLMService:
    """Lightweight orchestrator for LLM providers.

    The full implementation was missing; this minimal version supports the
    current API surface used by the endpoints (persona switching + basic
    provider registration) without blocking import-time errors.
    """

    def __init__(self):
        self.providers: dict[LLMProvider, BaseLLMProvider] = {}
        self.primary_provider: LLMProvider | None = None
        self.fallback_provider: LLMProvider | None = None
        self._current_persona: str = os.getenv("LLM_MODEL", "granite4:350m-h")

    def configure_provider(self, config: LLMConfig):
        """Register a provider. Only Ollama is actively constructed to avoid
        optional dependency explosions during import."""
        try:
            if config.provider == LLMProvider.OLLAMA:
                self.providers[LLMProvider.OLLAMA] = OllamaProvider(config)
                self.primary_provider = self.primary_provider or LLMProvider.OLLAMA
                self._current_persona = config.model
            elif config.provider == LLMProvider.MOCK:
                self.providers[LLMProvider.MOCK] = MockProvider(config)
                self.primary_provider = self.primary_provider or LLMProvider.MOCK
            else:
                # Register placeholder for other providers without instantiation
                self.providers[config.provider] = None  # type: ignore[assignment]
                if not self.primary_provider:
                    self.primary_provider = config.provider
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to configure provider {config.provider}: {exc}")

    def switch_persona(self, persona_model: str):
        ollama_provider = self.providers.get(LLMProvider.OLLAMA)
        if isinstance(ollama_provider, OllamaProvider):
            ollama_provider.switch_persona(persona_model)
        self._current_persona = persona_model

    def get_current_persona(self) -> str:
        return self._current_persona

    async def health_check(self) -> dict[str, bool]:
        results: dict[str, bool] = {}
        for provider_type, provider in self.providers.items():
            if provider is None:
                results[provider_type.value] = False
            else:
                results[provider_type.value] = await provider.health_check()
        return results


# Global instance
modular_llm_service = ModularLLMService()

def configure_llm_service():
    """Configure the LLM service based on environment variables."""
    # Primary provider configuration
    primary_provider_str = os.getenv("LLM_PROVIDER", "ollama").lower()
    primary_model = os.getenv("LLM_MODEL", "granite4:350m-h")
    primary_api_key = os.getenv("LLM_API_KEY")
    primary_base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")

    # Fallback provider configuration
    fallback_provider_str = os.getenv("LLM_FALLBACK_PROVIDER")
    fallback_model = os.getenv("LLM_FALLBACK_MODEL")
    fallback_api_key = os.getenv("LLM_FALLBACK_API_KEY")
    fallback_base_url = os.getenv("LLM_FALLBACK_BASE_URL")

    # Map string to enum
    try:
        primary_provider = LLMProvider(primary_provider_str)
    except ValueError:
        logger.warning(f"Invalid LLM_PROVIDER '{primary_provider_str}', using 'ollama'")
        primary_provider = LLMProvider.OLLAMA

    # Configure primary provider
    primary_config = LLMConfig(
        provider=primary_provider,
        model=primary_model,
        api_key=primary_api_key,
        base_url=primary_base_url,
        timeout=int(os.getenv("LLM_TIMEOUT", "300")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")) if os.getenv("LLM_MAX_TOKENS") else None,
        lora_adapter=os.getenv("LLM_LORA_ADAPTER")  # LoRA adapter for vLLM
    )

    modular_llm_service.configure_provider(primary_config)

    # Configure fallback provider if specified
    if fallback_provider_str:
        try:
            fallback_provider = LLMProvider(fallback_provider_str.lower())
        except ValueError:
            logger.warning(f"Invalid LLM_FALLBACK_PROVIDER '{fallback_provider_str}', using 'mock'")
            fallback_provider = LLMProvider.MOCK

        fallback_config = LLMConfig(
            provider=fallback_provider,
            model=fallback_model or primary_model,
            api_key=fallback_api_key or primary_api_key,
            base_url=fallback_base_url or primary_base_url,
            timeout=int(os.getenv("LLM_FALLBACK_TIMEOUT", "300")),
            temperature=float(os.getenv("LLM_FALLBACK_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_FALLBACK_MAX_TOKENS", "2048")) if os.getenv("LLM_FALLBACK_MAX_TOKENS") else None,
            fallback_provider=None  # No fallback for fallback provider
        )

        modular_llm_service.configure_provider(fallback_config)
        primary_config.fallback_provider = fallback_provider

    logger.info(f"Configured LLM service with primary: {primary_provider.value}, fallback: {fallback_provider_str or 'none'}")

# Initialize on import
configure_llm_service()