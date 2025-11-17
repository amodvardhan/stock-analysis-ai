"""
=============================================================================
AI Hub - Base Agent Class
=============================================================================
Abstract base class for all AI agents in the system.
=============================================================================
"""

from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
import structlog

from core.config import settings

logger = structlog.get_logger()


class BaseAgent:
    """
    Base class for all AI agents.
    
    Provides common functionality:
    - LLM initialization
    - Prompt management
    - Logging
    - Error handling
    
    All specific agents (Technical, Fundamental, etc.) inherit from this.
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (e.g., "TechnicalAnalyst")
            system_prompt: System instructions for the agent
            model: OpenAI model to use
            temperature: Model temperature (0.0 = deterministic, 1.0 = creative)
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model_name = model
        self.temperature = temperature
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # Create chain
        self.chain = self.prompt | self.llm
        
        logger.info(
            "agent_initialized",
            agent_name=name,
            model=model
        )
    
    async def invoke(
        self,
        input_text: str,
        config: Optional[RunnableConfig] = None
    ) -> str:
        """
        Invoke the agent with input text.
        
        Args:
            input_text: Input to the agent
            config: Optional LangChain config
        
        Returns:
            Agent's response as string
        """
        try:
            response = await self.chain.ainvoke(
                {"input": input_text},
                config=config
            )
            return response.content
            
        except Exception as e:
            logger.error("agent_invocation_failed", agent=self.name, error=str(e))
            raise
    
    async def analyze(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Abstract method for analysis.
        
        Each agent subclass must implement this method.
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement analyze() method")
