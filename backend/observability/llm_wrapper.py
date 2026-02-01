"""
Wrapper for LLM calls to automatically track AI metrics.
Use this instead of direct ChatOpenAI calls to get observability.
"""
import time
from typing import Any, Optional, Dict
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from backend.observability.ai_metrics import ai_metrics

class ObservableChatOpenAI(ChatOpenAI):
    """ChatOpenAI wrapper that automatically tracks AI metrics."""
    
    def __init__(self, agent_name: str = "Unknown", operation: str = "llm_call", task_id: Optional[str] = None, **kwargs):
        """
        Initialize with observability tracking.
        
        Args:
            agent_name: Name of the agent making the call
            operation: Type of operation (e.g., "response_generation", "intent_classification")
            task_id: Optional task ID for correlation
            **kwargs: All ChatOpenAI parameters
        """
        super().__init__(**kwargs)
        self._agent_name = agent_name
        self._operation = operation
        self._task_id = task_id
    
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Override to track metrics."""
        start_time = time.time()
        prompt_text = self._extract_prompt_text(messages)
        
        try:
            # Make the actual LLM call
            result = super()._generate(messages, stop, run_manager, **kwargs)
            
            # Extract token usage from response
            prompt_tokens = 0
            completion_tokens = 0
            
            # Try to get token usage from result
            if hasattr(result, 'llm_output') and result.llm_output:
                token_usage = result.llm_output.get('token_usage', {})
                prompt_tokens = token_usage.get('prompt_tokens', 0)
                completion_tokens = token_usage.get('completion_tokens', 0)
            
            # If not available, estimate (rough approximation: ~4 chars per token)
            if prompt_tokens == 0:
                prompt_tokens = len(prompt_text) // 4
            
            if completion_tokens == 0 and result.generations:
                # Handle different structures: result.generations can be list of lists or list of ChatGeneration
                try:
                    if result.generations[0] and isinstance(result.generations[0], list):
                        response_text = result.generations[0][0].text if result.generations[0] else ""
                    elif result.generations[0] and hasattr(result.generations[0], 'text'):
                        response_text = result.generations[0].text
                    else:
                        response_text = str(result.generations[0]) if result.generations[0] else ""
                    completion_tokens = len(response_text) // 4
                except (IndexError, AttributeError, TypeError):
                    completion_tokens = 0
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Track the call
            response_preview = None
            if result.generations:
                try:
                    # Handle different structures
                    if result.generations[0] and isinstance(result.generations[0], list):
                        if result.generations[0][0]:
                            gen = result.generations[0][0]
                            response_preview = gen.text if hasattr(gen, 'text') else str(gen)
                    elif result.generations[0] and hasattr(result.generations[0], 'text'):
                        response_preview = result.generations[0].text
                    elif result.generations[0]:
                        response_preview = str(result.generations[0])
                except (IndexError, AttributeError, TypeError):
                    response_preview = None
            
            ai_metrics.track_llm_call(
                model=self.model_name,
                agent_name=self._agent_name,
                operation=self._operation,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency_ms,
                task_id=self._task_id,
                success=True,
                prompt_preview=prompt_text[:500],
                response_preview=response_preview[:500] if response_preview else None
            )
            
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            # Track failed call
            ai_metrics.track_llm_call(
                model=self.model_name,
                agent_name=self._agent_name,
                operation=self._operation,
                prompt_tokens=len(prompt_text) // 4,  # Estimate
                completion_tokens=0,
                latency_ms=latency_ms,
                task_id=self._task_id,
                success=False,
                error=error_msg,
                prompt_preview=prompt_text[:500]
            )
            
            raise
    
    def _extract_prompt_text(self, messages: list[BaseMessage]) -> str:
        """Extract text from messages for preview."""
        text_parts = []
        for msg in messages:
            if hasattr(msg, 'content'):
                text_parts.append(str(msg.content))
            else:
                text_parts.append(str(msg))
        return " ".join(text_parts)

def create_observable_llm(
    agent_name: str,
    operation: str,
    task_id: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    temperature: float = 0.7,
    **kwargs
) -> ObservableChatOpenAI:
    """
    Create an observable LLM instance.
    
    Usage:
        llm = create_observable_llm(
            agent_name="ResponseAgent",
            operation="response_generation",
            task_id=state.get("task_id"),
            model="gpt-3.5-turbo",
            temperature=0.7
        )
    """
    return ObservableChatOpenAI(
        agent_name=agent_name,
        operation=operation,
        task_id=task_id,
        model=model,
        temperature=temperature,
        **kwargs
    )

