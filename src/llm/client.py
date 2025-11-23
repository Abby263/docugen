"""LLM Client Module"""

import asyncio
import time
from typing import List, Dict, Any, Optional, AsyncGenerator, Union
from loguru import logger
import json

# Import monitoring if available
try:
    from ..monitoring.langfuse_monitor import monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("Monitoring module not available")

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available, please install: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available, please install: pip install anthropic for Claude support")

from .config import LLMConfig, LLMProvider


class LLMClient:
    """LLM Client for interacting with various LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """TODO: Add docstring."""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                self._initialize_openai()
            elif self.config.provider == LLMProvider.AZURE_OPENAI:
                self._initialize_azure_openai()
            elif self.config.provider == LLMProvider.ANTHROPIC:
                self._initialize_anthropic()
            elif self.config.provider in [
                LLMProvider.ZHIPU, 
                LLMProvider.QWEN, 
                LLMProvider.DEEPSEEK,
                LLMProvider.OLLAMA
            ]:
                self._initialize_openai_compatible()
            else:
                raise ValueError(f"Unsupported LLM provider: {self.config.provider}")
                
            logger.info(f"LLM client initialized: {self.config.provider} - {self.config.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed: pip install openai")
        
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
        
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_azure_openai(self):
        """Initialize Azure OpenAI client"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed: pip install openai")
        
        if not self.config.api_key:
            raise ValueError("Azure OpenAI API key is required")
        
        if not self.config.azure_deployment:
            raise ValueError("Azure deployment name is required")
        
        # Construct Azure OpenAI URL
        azure_base_url = self.config.base_url
        if not azure_base_url.endswith('/'):
            azure_base_url += '/'
        
        self._client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=f"{azure_base_url}openai/deployments/{self.config.azure_deployment}",
            api_version=self.config.azure_api_version,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_anthropic(self):
        """Initialize Anthropic client"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed: pip install anthropic")
        
        if not self.config.api_key:
            raise ValueError("Anthropic API key is required")
        
        self._client = anthropic.AsyncAnthropic(
            api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def _initialize_openai_compatible(self):
        """Initialize OpenAI-compatible clients (Qwen, DeepSeek, Zhipu, Ollama, etc.)"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed: pip install openai")
        
        # Ollama doesn't require an API key
        if self.config.provider == LLMProvider.OLLAMA:
            api_key = "ollama"  # Dummy key for Ollama
        else:
            if not self.config.api_key:
                raise ValueError(f"{self.config.provider} API key is required")
            api_key = self.config.api_key
        
        # Get base_url
        base_url = self.config.base_url
        if not base_url:
            # Use default URL for each provider
            if self.config.provider == LLMProvider.ZHIPU:
                base_url = "https://open.bigmodel.cn/api/paas/v4"
            elif self.config.provider == LLMProvider.QWEN:
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            elif self.config.provider == LLMProvider.DEEPSEEK:
                base_url = "https://api.deepseek.com/v1"
            elif self.config.provider == LLMProvider.OLLAMA:
                base_url = "http://localhost:11434/v1"
            else:
                raise ValueError(f"No default base_url for provider: {self.config.provider}")
        
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
        
        logger.info(f"Initialized OpenAI-compatible client: {self.config.provider} @ {base_url}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        trace_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        start_time = time.time()
        
        try:
            # 
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "stream": self.config.stream,
                **kwargs
            }
            
            if self.config.provider == LLMProvider.ANTHROPIC:
                result = await self._anthropic_chat_completion(messages, **kwargs)
            else:
                result = await self._openai_chat_completion(params)
            
            # Log LLM call to Langfuse if monitoring is enabled
            if MONITORING_AVAILABLE and trace_id:
                execution_time = time.time() - start_time
                monitor.log_llm_call(
                    trace_id=trace_id,
                    model=self.config.model_name,
                    input_messages=messages,
                    output=result.get("content", ""),
                    usage=result.get("usage"),
                    metadata={
                        "provider": self.config.provider.value,
                        "execution_time": execution_time,
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens
                    }
                )
            
            return result
                
        except Exception as e:
            # Log error to Langfuse
            if MONITORING_AVAILABLE and trace_id:
                execution_time = time.time() - start_time
                monitor.log_llm_call(
                    trace_id=trace_id,
                    model=self.config.model_name,
                    input_messages=messages,
                    output="",
                    usage=None,
                    metadata={
                        "provider": self.config.provider.value,
                        "execution_time": execution_time,
                        "error": str(e),
                        "temperature": self.config.temperature,
                        "max_tokens": self.config.max_tokens
                    }
                )
            
            logger.error(f"LLM call failed ({self.config.provider}): {e}")
            # Provide more specific error messages
            if "api_key" in str(e).lower():
                raise ValueError(f"API key error ({self.config.provider}): Please check your API key")
            elif "model" in str(e).lower():
                raise ValueError(f"Model error ({self.config.provider}): Model {self.config.model_name} may not be available")
            elif "base_url" in str(e).lower() or "connection" in str(e).lower():
                raise ValueError(f"Connection error ({self.config.provider}): Please check base_url: {self.config.base_url}")
            else:
                raise

    async def get_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_model: Any = None,
        trace_id: Optional[str] = None,
        **kwargs
    ):
        """
        Get structured response from LLM using Pydantic model

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            response_model: Pydantic model for response structure
            trace_id: Optional trace ID for monitoring
            **kwargs: Additional parameters

        Returns:
            Pydantic model instance with structured response
        """
        try:
            # instructor
            import instructor
            from pydantic import BaseModel

            # Note: Only OpenAI-compatible providers support instructor
            openai_compatible_providers = [
                LLMProvider.OPENAI,
                LLMProvider.AZURE_OPENAI,
                LLMProvider.DEEPSEEK,
                LLMProvider.ZHIPU,
                LLMProvider.QWEN
            ]

            if self.config.provider in openai_compatible_providers:
                client = instructor.from_openai(self._client)
            else:
                # Fall back to JSON mode for other providers
                logger.warning(f"{self.config.provider} doesn't support instructor, falling back to JSON mode")
                return await self._fallback_structured_response(prompt, system_prompt, response_model)

            # Construct messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Get structured response
            response = await client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                response_model=response_model,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
            )

            logger.info(f"Got structured response: {response_model.__name__}")
            return response

        except ImportError:
            logger.warning("instructor library not installed, falling back to JSON mode")
            return await self._fallback_structured_response(prompt, system_prompt, response_model)
        except Exception as e:
            logger.error(f"Structured response failed: {e}")
            # Fall back to JSON mode
            return await self._fallback_structured_response(prompt, system_prompt, response_model)

    async def _fallback_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_model: Any = None
    ):
        """Fallback method for structured response using JSON mode + manual parsing"""
        import json
        from pydantic import BaseModel

        # Add JSON schema to prompt if available
        if response_model and hasattr(response_model, 'model_json_schema'):
            schema = response_model.model_json_schema()
            enhanced_prompt = f"""{prompt}

Please respond with a JSON object matching this schema:
```json
{json.dumps(schema, indent=2, ensure_ascii=False)}
```

Respond ONLY with valid JSON."""
        else:
            enhanced_prompt = prompt

        # Construct messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": enhanced_prompt})

        # Call chat_completion with JSON mode
        result = await self.chat_completion(
            messages=messages,
            response_format={"type": "json_object"}
        )

        # Extract JSON from response
        content = result.get("content", "")

        # Remove markdown code block markers if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        data = json.loads(content)

        # Convert to Pydantic model if provided
        if response_model:
            return response_model(**data)
        return data

    async def _openai_chat_completion(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI-style chat completion"""
        try:
            response = await self._client.chat.completions.create(**params)
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "finish_reason": response.choices[0].finish_reason
            }
        except Exception as e:
            # Provide provider-specific error messages
            if self.config.provider == LLMProvider.QWEN:
                if "InvalidApiKey" in str(e):
                    raise ValueError("Invalid Qwen API key. Please set DASHSCOPE_API_KEY")
                elif "ModelNotFound" in str(e):
                    raise ValueError(f"Model {self.config.model_name} not found for Qwen")
            elif self.config.provider == LLMProvider.ZHIPU:
                if "invalid_api_key" in str(e):
                    raise ValueError("Invalid Zhipu AI API key. Please check your API key")
            elif self.config.provider == LLMProvider.DEEPSEEK:
                if "invalid_api_key" in str(e):
                    raise ValueError("Invalid DeepSeek API key. Please check your API key")
            elif self.config.provider == LLMProvider.OLLAMA:
                if "Connection" in str(e):
                    raise ValueError("Failed to connect to Ollama. Please make sure Ollama is running (ollama serve)")
            
            raise
    
    async def _anthropic_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> Dict[str, Any]:
        """Anthropic-style chat completion"""
        # Extract system message (Anthropic handles it separately)
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append(msg)
        
        params = {
            "model": self.config.model_name,
            "messages": converted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            **kwargs
        }
        
        if system_message:
            params["system"] = system_message
        
        response = await self._client.messages.create(**params)
        
        return {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            "finish_reason": response.stop_reason
        }
    
    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """TODO: Add docstring."""
        try:
            params = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "top_p": self.config.top_p,
                "stream": True,
                **kwargs
            }
            
            if self.config.provider == LLMProvider.ANTHROPIC:
                async for chunk in self._anthropic_stream_chat(messages, **kwargs):
                    yield chunk
            else:
                async for chunk in self._openai_stream_chat(params):
                    yield chunk
                    
        except Exception as e:
            logger.error(f": {e}")
            raise
    
    async def _openai_stream_chat(self, params: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """OpenAI"""
        stream = await self._client.chat.completions.create(**params)
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def _anthropic_stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Anthropic-style streaming chat completion"""
        # Extract system message (Anthropic handles it separately)
        system_message = None
        converted_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                converted_messages.append(msg)
        
        params = {
            "model": self.config.model_name,
            "messages": converted_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": True,
            **kwargs
        }
        
        if system_message:
            params["system"] = system_message
        
        stream = await self._client.messages.create(**params)
        
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text
    
    async def simple_chat(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """TODO: Add docstring."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(messages)
        return response["content"]
    
    def get_model_info(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "provider": self.config.provider,
            "model_name": self.config.model_name,
            "base_url": self.config.base_url,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
    
    async def test_connection(self) -> bool:
        """Test the LLM connection"""
        try:
            response = await self.simple_chat(
                "Hello", 
                "You are a helpful assistant. Please respond with 'OK' only."
            )
            return len(response.strip()) > 0
        except Exception as e:
            logger.error(f"Connection test failed ({self.config.provider}): {e}")
            return False