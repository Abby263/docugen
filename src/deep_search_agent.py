"""DeepSearch Agent - Main entry point for deep search operations"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from .llm import LLMManager, PromptManager
from .agents.coordinator import DeepSearchCoordinator, DeepSearchConfig

# Import Langfuse monitoring
try:
    from .monitoring.langfuse_monitor import monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    logger.warning("Langfuse monitoring not available")


class DeepSearchAgent:
    """DeepSearch - """
    
    def __init__(
        self,
        config: Optional[DeepSearchConfig] = None,
        llm_manager: Optional[LLMManager] = None,
        prompt_manager: Optional[PromptManager] = None
    ):
        """DeepSearch"""
        self.config = config or DeepSearchConfig()
        self.llm_manager = llm_manager or LLMManager()
        self.prompt_manager = prompt_manager or PromptManager()
        
        # 
        self.coordinator = DeepSearchCoordinator(
            config=self.config,
            llm_manager=self.llm_manager,
            prompt_manager=self.prompt_manager
        )
        
        logger.info("DeepSearch")
    
    async def search(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute deep search for the given query
        
        Args:
            query: Search query
            context: Optional context information
            
        Returns:
            Search results dictionary
        """
        logger.info(f"Starting deep search: {query}")
        
        # Start Langfuse trace
        trace_id = None
        if MONITORING_AVAILABLE:
            trace_id = monitor.start_trace(
                name="DeepSearch",
                input_data={"query": query, "context": context},
                metadata={"timestamp": datetime.now().isoformat()}
            )
            # Store trace_id in coordinator for propagation
            if trace_id:
                self.coordinator._trace_id = trace_id
        
        try:
            # Execute search via coordinator
            result = await self.coordinator.process_query(query, context)
            
            logger.info(f"Search complete: {result.get('status')}")
            
            # End Langfuse trace
            if MONITORING_AVAILABLE and trace_id:
                monitor.end_trace(
                    trace_id=trace_id,
                    output_data={"status": result.get('status')},
                    metadata={"timestamp": datetime.now().isoformat()}
                )
                # Flush to ensure data is sent
                monitor.flush()
            
            return result
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            
            # End trace with error
            if MONITORING_AVAILABLE and trace_id:
                monitor.end_trace(
                    trace_id=trace_id,
                    output_data={"status": "error", "error": str(e)},
                    metadata={"error": True, "timestamp": datetime.now().isoformat()}
                )
                monitor.flush()
            
            return {
                "status": "error",
                "error": str(e),
                "query": query,
                "result": {}
            }
    
    async def quick_answer(self, query: str) -> str:
        """TODO: Add docstring."""
        return await self.coordinator.quick_answer(query)
    
    def get_status(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        return {
            "system": "DeepSearch",
            "version": "2.0",
            "status": "active",
            "coordinator": self.coordinator.get_agent_status(),
            "llm_manager": {
                "available_configs": len(self.llm_manager.configs),
                "available_providers": self.llm_manager.get_available_providers()
            },
            "prompt_manager": {
                "loaded_prompts": len(self.prompt_manager.prompts_cache) if self.prompt_manager else 0
            }
        }
    
    async def analyze_query_complexity(self, query: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            # 
            task_decomposer = self.coordinator.agents["task_decomposer"]
            result = await task_decomposer.process({
                "query": query,
                "context": {}
            })
            
            if result.get("status") == "success":
                analysis = result.get("result", {}).get("query_analysis", {})
                return {
                    "status": "success",
                    "complexity": analysis.get("complexity", "unknown"),
                    "intent": analysis.get("intent", "unknown"),
                    "time_sensitive": analysis.get("time_sensitive", False),
                    "domain": analysis.get("domain", "unknown"),
                    "expected_output": analysis.get("expected_output", "unknown")
                }
            else:
                return {
                    "status": "error",
                    "error": ""
                }
                
        except Exception as e:
            logger.error(f": {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def generate_report_only(
        self, 
        query: str, 
        search_results: list, 
        report_type: str = "general"
    ) -> Dict[str, Any]:
        """TODO: Add docstring."""
        try:
            report_generator = self.coordinator.agents["report_generator"]
            
            report_input = {
                "query": query,
                "task_analysis": {"query_analysis": {"expected_output": report_type}},
                "search_results": search_results,
                "analysis_results": {},
                "synthesis_results": {}
            }
            
            result = await report_generator.process(report_input)
            
            return result
            
        except Exception as e:
            logger.error(f": {e}")
            return {
                "status": "error",
                "error": str(e)
            }