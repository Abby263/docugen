"""Langfuse Monitoring - API Integration"""

import os
import json
import time
import uuid
from typing import Dict, Any, Optional, List
from functools import wraps
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
    logger.info("Langfuse library successfully imported")
except ImportError as e:
    LANGFUSE_AVAILABLE = False
    logger.warning(f"Langfuse library import failed: {e}")
    Langfuse = None


class LangfuseMonitor:
    """Langfuse Monitor - API Integration for LLM tracking"""
    
    def __init__(self):
        self.enabled = False
        self.langfuse = None
        self.active_traces = {}  # Active traces
        self.active_generations = {}  # Active generations
        self.active_spans = {}  # Active spans
        self._initialize()
    
    def _initialize(self):
        """Initialize Langfuse monitoring"""
        if not LANGFUSE_AVAILABLE:
            logger.warning("Langfuse library not available")
            return
        
        # Get API keys from environment
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        # Support both LANGFUSE_HOST and LANGFUSE_BASE_URL for compatibility
        host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
        
        if not secret_key or not public_key:
            logger.warning("Langfuse API keys not configured")
            logger.info(f"Configuration status: LANGFUSE_SECRET_KEY={'configured' if secret_key else 'missing'}, LANGFUSE_PUBLIC_KEY={'configured' if public_key else 'missing'}")
            return
        
        try:
            self.langfuse = Langfuse(
                secret_key=secret_key,
                public_key=public_key,
                host=host,
                debug=False
            )
            
            # Verify authentication
            self.langfuse.auth_check()
            self.enabled = True
            logger.info(f"Langfuse successfully initialized: {host}")
            
        except Exception as e:
            logger.error(f"Langfuse initialization failed: {e}")
            logger.info("Please check your API keys")
    
    def start_trace(self, name: str, input_data: Dict = None, metadata: Dict = None) -> Optional[str]:
        """Start a new trace"""
        if not self.langfuse:
            return None
        
        try:
            # Use start_observation to create a trace
            trace = self.langfuse.start_observation(
                name=name,
                as_type="span",
                input=input_data or {},
                metadata=metadata or {}
            )
            
            trace_id = trace.trace_id
            self.active_traces[trace_id] = trace
            
            logger.info(f"Started trace: {name}, ID: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"Failed to start trace: {e}")
            return None
    
    def end_trace(self, trace_id: str, output_data: Dict = None, metadata: Dict = None):
        """End a trace"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            # Update trace with output and metadata
            if output_data or metadata:
                trace.update(
                    output=output_data,
                    metadata=metadata or {}
                )
            
            # End the trace
            trace.end()
            del self.active_traces[trace_id]
            
            logger.info(f"Ended trace: {trace_id}")
            
        except Exception as e:
            logger.error(f"Failed to end trace: {e}")
    
    def log_llm_call(self, trace_id: str, model: str, input_messages: List, 
                     output: str, usage: Dict = None, metadata: Dict = None) -> Optional[str]:
        """Log an LLM call"""
        if not self.langfuse or trace_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[trace_id]
            
            # Use trace's start_observation to create a generation
            generation = trace.start_observation(
                name=f"LLM-{model}",
                as_type="generation",
                model=model,
                input=input_messages,
                output=output,
                usage_details=usage or {},
                metadata=metadata or {}
            )
            
            generation_id = generation.id
            self.active_generations[generation_id] = generation
            
            logger.info(f"Logged LLM call: {model}, generation_id: {generation_id}")
            return generation_id
            
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")
            return None
    
    def end_llm_call(self, generation_id: str, output: str = None, usage: Dict = None):
        """End an LLM call"""
        if not self.langfuse or generation_id not in self.active_generations:
            return
        
        try:
            generation = self.active_generations[generation_id]
            
            # Update generation with output and usage
            if output or usage:
                generation.update(
                    output=output,
                    usage_details=usage or {}
                )
            
            generation.end()
            del self.active_generations[generation_id]
            
            logger.info(f"Ended LLM call: {generation_id}")
            
        except Exception as e:
            logger.error(f"Failed to end LLM call: {e}")
    
    def log_agent_action(self, trace_id: str, agent_name: str, action: str, 
                        input_data: Any = None, output_data: Any = None,
                        metadata: Dict = None) -> Optional[str]:
        """Log an agent action"""
        if not self.langfuse or trace_id not in self.active_traces:
            return None
        
        try:
            trace = self.active_traces[trace_id]
            
            # Use trace's start_span to create an agent span
            span = trace.start_span(
                name=f"Agent-{agent_name}-{action}",
                input=input_data,
                output=output_data,
                metadata=metadata or {}
            )
            
            span_id = span.id
            self.active_spans[span_id] = span
            
            logger.info(f"Logged agent action: {agent_name}-{action}, span_id: {span_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"Failed to log agent action: {e}")
            return None
    
    def end_agent_action(self, span_id: str, output_data: Any = None, metadata: Dict = None):
        """End an agent action"""
        if not self.langfuse or span_id not in self.active_spans:
            return
        
        try:
            span = self.active_spans[span_id]
            
            # Update span with output and metadata
            if output_data or metadata:
                span.update(
                    output=output_data,
                    metadata=metadata or {}
                )
            
            span.end()
            del self.active_spans[span_id]
            
            logger.info(f"Ended agent action: {span_id}")
            
        except Exception as e:
            logger.error(f"Failed to end agent action: {e}")
    
    def log_search_action(self, trace_id: str, query: str, results_count: int,
                         search_time: float, metadata: Dict = None):
        """Log a search action"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Web-Search",
                input={"query": query},
                output={"results_count": results_count, "search_time": search_time},
                metadata=metadata or {}
            )
            
            # End span immediately
            span.end()
            
            logger.info(f"Logged search: {query} -> {results_count} results")
            
        except Exception as e:
            logger.error(f"Failed to log search action: {e}")
    
    def log_content_extraction(self, trace_id: str, url: str, content_length: int,
                              extraction_time: float, success: bool,
                              metadata: Dict = None):
        """Log content extraction"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Content-Extraction",
                input={"url": url},
                output={
                    "content_length": content_length,
                    "extraction_time": extraction_time,
                    "success": success
                },
                metadata=metadata or {}
            )
            
            # End span immediately
            span.end()
            
            logger.info(f"Logged extraction: {url} -> {content_length} chars")
            
        except Exception as e:
            logger.error(f"Failed to log content extraction: {e}")
    
    def log_evaluation(self, trace_id: str, content_items: int, 
                      relevant_items: int, evaluation_time: float,
                      metadata: Dict = None):
        """Log content evaluation"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Content-Evaluation",
                input={"content_items": content_items},
                output={
                    "relevant_items": relevant_items,
                    "relevance_rate": relevant_items / content_items if content_items > 0 else 0,
                    "evaluation_time": evaluation_time
                },
                metadata=metadata or {}
            )
            
            # End span immediately
            span.end()
            
            logger.info(f"Logged evaluation: {relevant_items}/{content_items} items")
            
        except Exception as e:
            logger.error(f"Failed to log evaluation: {e}")
    
    def log_report_generation(self, trace_id: str, report_type: str, 
                             word_count: int, generation_time: float,
                             metadata: Dict = None):
        """Log report generation"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            span = trace.start_span(
                name="Report-Generation",
                input={"report_type": report_type},
                output={
                    "word_count": word_count,
                    "generation_time": generation_time
                },
                metadata=metadata or {}
            )
            
            # End span immediately
            span.end()
            
            logger.info(f"Logged report generation: {report_type} -> {word_count} words")
            
        except Exception as e:
            logger.error(f"Failed to log report generation: {e}")
    
    def log_event(self, trace_id: str, name: str, input_data: Any = None, 
                  metadata: Dict = None):
        """Log an event"""
        if not self.langfuse or trace_id not in self.active_traces:
            return
        
        try:
            trace = self.active_traces[trace_id]
            
            event = trace.create_event(
                name=name,
                input=input_data,
                metadata=metadata or {}
            )
            
            logger.info(f"Logged event: {name}")
            return event.id
            
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
            return None
    
    def flush(self):
        """Flush all pending data to Langfuse"""
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
                logger.info("Langfuse data flushed successfully")
            except Exception as e:
                logger.error(f"Failed to flush Langfuse data: {e}")


# Global monitor instance
monitor = LangfuseMonitor()


def trace_agent_method(agent_name: str, action: str):
    """Decorator to trace agent methods"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not monitor.enabled:
                return await func(*args, **kwargs)
            
            trace_id = getattr(args[0], '_trace_id', None)
            if not trace_id:
                return await func(*args, **kwargs)
            
            start_time = time.time()
            span_id = None
            
            try:
                # Log agent action start
                span_id = monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:])[:500], "kwargs": str(kwargs)[:500]},
                    metadata={"start_time": start_time}
                )
                
                result = await func(*args, **kwargs)
                
                # Log agent action completion
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=str(result)[:1000] if result else None,
                        metadata={"execution_time": time.time() - start_time, "success": True}
                    )
                
                return result
                
            except Exception as e:
                # Log agent action failure
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=None,
                        metadata={
                            "execution_time": time.time() - start_time,
                            "success": False,
                            "error": str(e)
                        }
                    )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not monitor.enabled:
                return func(*args, **kwargs)
            
            trace_id = getattr(args[0], '_trace_id', None)
            if not trace_id:
                return func(*args, **kwargs)
            
            start_time = time.time()
            span_id = None
            
            try:
                # Log agent action start
                span_id = monitor.log_agent_action(
                    trace_id=trace_id,
                    agent_name=agent_name,
                    action=action,
                    input_data={"args": str(args[1:])[:500], "kwargs": str(kwargs)[:500]},
                    metadata={"start_time": start_time}
                )
                
                result = func(*args, **kwargs)
                
                # Log agent action completion
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=str(result)[:1000] if result else None,
                        metadata={"execution_time": time.time() - start_time, "success": True}
                    )
                
                return result
                
            except Exception as e:
                # Log agent action failure
                if span_id:
                    monitor.end_agent_action(
                        span_id=span_id,
                        output_data=None,
                        metadata={
                            "execution_time": time.time() - start_time,
                            "success": False,
                            "error": str(e)
                        }
                    )
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator