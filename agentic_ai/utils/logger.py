"""
🛠️ Utility module for agentic system logging and helpers.

This module provides production-ready utilities for agent observability,
debugging, and system monitoring.
"""

from loguru import logger
from rich.console import Console
from rich.table import Table
from typing import Dict, Any, List
import json
import asyncio


def setup_agent_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configure structured logging for the agentic system.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log persistence
    """
    logger.remove()  # Clear default handlers
    
    # Console logging with rich formatting
    logger.add(
        lambda msg: print(msg),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[agent] if 'agent' in extra else 'SYSTEM'}</cyan> | {message}",
        level=log_level,
        colorize=True,
    )
    
    # File logging (if specified)
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {extra[agent] if 'agent' in extra else 'SYSTEM'} | {message}",
            level=log_level,
            rotation="10 MB",  # Rotate when file gets large
        )


def display_agent_state(agent_name: str, state: Dict[str, Any]) -> None:
    """
    Display agent state in a formatted table using Rich.
    Useful for debugging and monitoring agent internals.
    """
    console = Console()
    
    table = Table(title=f"Agent State: {agent_name}")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_column("Type", style="green")
    
    for key, value in state.items():
        # Handle complex objects by converting to JSON
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        
        table.add_row(key, value_str, type(value).__name__)
    
    console.print(table)


async def monitor_agent_performance(agents: List[Any], interval: int = 5) -> None:
    """
    Monitor multiple agents and log their states periodically.
    Useful for debugging multi-agent interactions.
    
    Args:
        agents: List of agent instances to monitor
        interval: Monitoring interval in seconds
    """
    while True:
        logger.info("=== AGENT MONITORING CYCLE ===")
        
        for agent in agents:
            logger.info(f"Agent {agent.name} state: {agent.state}")
        
        await asyncio.sleep(interval)


# --- 🎓 TEACHING NOTES ---
#
# 🔍 OBSERVABILITY PATTERNS:
# - Structured logging with agent context (essential for multi-agent debugging)
# - Rich formatting for better developer experience
# - State visualization for understanding agent internals
# - Performance monitoring for production systems
#
# 🚀 PRODUCTION UPGRADES:
# - Add metrics collection (Prometheus, StatsD)
# - Integrate with APM tools (DataDog, New Relic)
# - Add distributed tracing for multi-agent workflows
# - Implement health checks and alerting
