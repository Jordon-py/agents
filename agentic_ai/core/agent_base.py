from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import asyncio
from loguru import logger


class AgentBase(ABC):
    """
    Abstract base class for all agents in the agentic system.
    
    🧠 DESIGN PRINCIPLES:
    - Implements core agentic patterns: perception, decision, action, messaging
    - Async-ready for concurrent agent execution and multi-agent orchestration
    - Built-in observability with structured logging
    - Extensible state management and inter-agent communication
    
    🎯 USAGE PATTERNS:
    - Single Agent: await agent.run(observation)
    - Multi-Agent: Use message() for agent-to-agent communication
    - Custom Workflows: Override run() for specialized agentic loops
    """

    def __init__(
        self,
        name: str,
        state: Optional[Dict[str, Any]] = None,
        log_level: str = "INFO",
    ):
        """
        Initialize the agent with identity, state, and observability.
        
        Args:
            name: Unique agent identifier for logging and messaging
            state: Optional initial state (avoid mutable defaults)
            log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
        """
        self.name = name
        self.state = state or {}  # Fresh dict per instance - critical for multi-agent
        self.logger = logger.bind(agent=self.name)  # Structured logging context
        
        # Configure per-agent logging
        logger.remove()  # Remove default handler
        logger.add(
            lambda msg: print(msg),  # Simple console output for now
            format="<green>{time}</green> | <level>{level: <8}</level> | <cyan>[{extra[agent]}]</cyan> | {message}",
            level=log_level,
        )

    @abstractmethod
    async def perceive(self, observation: Any) -> None:
        """
        🔍 PERCEPTION PHASE: Receive and process inputs from environment/agents.
        
        Should update internal state, memory, or world model.
        This is where agents build situational awareness.
        
        Design Notes:
        - Keep perception logic simple and focused
        - Use state dict for short-term memory
        - Consider external storage for large memories (vector DBs, files)
        """
        pass

    @abstractmethod
    async def decide(self) -> Any:
        """
        🤔 DECISION PHASE: Generate actions based on current state and goals.
        
        Returns an action, command, or message to be executed.
        This is the "intelligence" of the agent.
        
        Design Notes:
        - Stateless decision functions are easier to test and debug
        - Consider using strategy patterns for complex decision logic
        - Return structured data (dicts, Pydantic models) for complex actions
        """
        pass

    @abstractmethod
    async def act(self, action: Any) -> None:
        """
        🎯 ACTION PHASE: Execute decisions in the environment or communicate.
        
        Should produce side effects: file I/O, API calls, agent messages, etc.
        
        Design Notes:
        - Separate action execution from decision logic
        - Use try/catch for robust error handling
        - Log all actions for observability and debugging
        """
        pass

    async def message(self, recipient: 'AgentBase', content: Any) -> None:
        """
        📨 INTER-AGENT COMMUNICATION: Send structured messages between agents.
        
        Enables multi-agent coordination, task delegation, and information sharing.
        By default, routes messages to recipient's perceive() method.
        
        Args:
            recipient: Target agent instance
            content: Message payload (any structured data)
        """
        self.logger.info(f"Sending message to {recipient.name}: {content}")
        await recipient.perceive(content)

    async def run(self, observation: Any) -> Any:
        """
        🔄 STANDARD AGENTIC LOOP: perceive → decide → act
        
        Can be overridden for custom workflows or specialized agent behaviors.
        Returns the action for potential chaining or logging.
        
        Usage:
            result = await agent.run("Hello, agent!")
        """
        self.logger.debug(f"Starting agent loop with observation: {observation}")
        
        await self.perceive(observation)
        action = await self.decide()
        await self.act(action)
        
        self.logger.debug(f"Agent loop completed with action: {action}")
        return action

    def log(self, message: str, level: str = "INFO") -> None:
        """
        📝 STRUCTURED LOGGING: Agent-specific logging with context.
        
        Args:
            message: Log message
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        getattr(self.logger, level.lower())(message)


# --- 🎓 TEACHING NOTES ---
# 
# 🏗️ ARCHITECTURAL DECISIONS:
# - Async methods enable concurrent agent execution (essential for multi-agent systems)
# - State management via dict (simple) vs Pydantic models (type-safe, serializable)
# - Loguru provides structured logging with agent context (better than print())
# - message() method enables agent-to-agent communication patterns
#
# ⚠️ PRODUCTION CONSIDERATIONS:
# - Add input validation (Pydantic) for robust state management
# - Use external message buses (Redis, Kafka) for distributed agents
# - Implement agent lifecycle management (start, stop, health checks)
# - Add metrics collection for observability (Prometheus, DataDog)
#
# 🧪 EXTENSIBILITY PATTERNS:
# - Behavior Trees: Override run() for complex decision sequences
# - State Machines: Use state dict with formal state transitions
# - Plugin Architecture: Abstract capabilities into mixins or protocols
# - Event-Driven: React to events instead of polling with run()
#
# 🔄 NEXT STEPS:
# 1. Implement a concrete agent (TaskAgent, ChatAgent, FileAgent)
# 2. Add agent orchestration layer (AgentManager, Environment)
# 3. Build monitoring and debugging tools
# 4. Scale to distributed multi-agent systems