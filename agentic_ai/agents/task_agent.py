"""
🤖 TaskAgent: A concrete implementation of AgentBase for task processing.

This agent demonstrates the core agentic patterns:
- Receives tasks via perception
- Makes decisions about task priority and execution
- Logs and executes tasks as actions

Perfect for learning agent development and testing agentic workflows.
"""

import asyncio
from typing import Any, Dict, List
from ..core.agent_base import AgentBase


class TaskAgent(AgentBase):
    """
    A simple task-processing agent that demonstrates core agentic patterns.
    
    🎯 CAPABILITIES:
    - Receives and queues tasks
    - Prioritizes tasks by type or urgency  
    - Executes tasks and logs results
    - Maintains task history and performance metrics
    
    🧠 STATE MANAGEMENT:
    - task_queue: List of pending tasks
    - completed_tasks: History of finished tasks
    - performance_metrics: Task execution statistics
    """
    
    def __init__(self, name: str, max_queue_size: int = 10):
        """
        Initialize TaskAgent with task management capabilities.
        
        Args:
            name: Agent identifier
            max_queue_size: Maximum number of queued tasks
        """
        super().__init__(name)
        
        # Initialize agent state with task management structures
        self.state.update({
            "task_queue": [],
            "completed_tasks": [],
            "performance_metrics": {
                "tasks_completed": 0,
                "tasks_failed": 0,
                "average_execution_time": 0.0,
            },
            "max_queue_size": max_queue_size,
        })
        
        self.logger.info(f"TaskAgent {name} initialized with max queue size: {max_queue_size}")

    async def perceive(self, observation: Any) -> None:
        """
        🔍 PERCEPTION: Receive and process task requests.
        
        Handles different input types:
        - String: Simple task description
        - Dict: Structured task with metadata
        - List: Multiple tasks to queue
        """
        self.logger.debug(f"Perceiving observation: {observation}")
        
        # Handle different observation types
        if isinstance(observation, str):
            # Simple string task
            task = {
                "id": len(self.state["task_queue"]) + len(self.state["completed_tasks"]) + 1,
                "description": observation,
                "priority": "normal",
                "created_at": asyncio.get_event_loop().time(),
            }
            await self._add_task(task)
            
        elif isinstance(observation, dict):
            # Structured task with metadata
            task = {
                "id": observation.get("id", len(self.state["task_queue"]) + len(self.state["completed_tasks"]) + 1),
                "description": observation.get("description", "Unknown task"),
                "priority": observation.get("priority", "normal"),
                "created_at": asyncio.get_event_loop().time(),
                **observation  # Include any additional metadata
            }
            await self._add_task(task)
            
        elif isinstance(observation, list):
            # Multiple tasks
            for item in observation:
                await self.perceive(item)  # Recursively process each task
                
        else:
            self.logger.warning(f"Unknown observation type: {type(observation)}")

    async def decide(self) -> Any:
        """
        🤔 DECISION: Select the next task to execute based on priority and queue status.
        
        Decision Logic:
        1. Check if queue is empty
        2. Prioritize tasks (high > normal > low)
        3. Return the selected task for execution
        """
        if not self.state["task_queue"]:
            self.logger.debug("No tasks in queue - deciding to wait")
            return {"action": "wait", "reason": "queue_empty"}
        
        # Simple priority-based selection
        # In production, consider more sophisticated algorithms (FIFO, deadline-based, etc.)
        high_priority_tasks = [t for t in self.state["task_queue"] if t.get("priority") == "high"]
        normal_priority_tasks = [t for t in self.state["task_queue"] if t.get("priority") == "normal"]
        low_priority_tasks = [t for t in self.state["task_queue"] if t.get("priority") == "low"]
        
        if high_priority_tasks:
            selected_task = high_priority_tasks[0]
        elif normal_priority_tasks:
            selected_task = normal_priority_tasks[0]
        elif low_priority_tasks:
            selected_task = low_priority_tasks[0]
        else:
            selected_task = self.state["task_queue"][0]  # Fallback to FIFO
        
        self.logger.info(f"Selected task for execution: {selected_task['id']} - {selected_task['description']}")
        
        return {
            "action": "execute_task",
            "task": selected_task,
            "reason": f"priority_{selected_task.get('priority', 'normal')}"
        }

    async def act(self, action: Any) -> None:
        """
        🎯 ACTION: Execute the decided action (task execution or waiting).
        
        Handles different action types:
        - execute_task: Process and complete a task
        - wait: Idle state when no tasks available
        """
        if not isinstance(action, dict):
            self.logger.error(f"Invalid action format: {action}")
            return
        
        action_type = action.get("action")
        
        if action_type == "execute_task":
            await self._execute_task(action["task"])
        elif action_type == "wait":
            self.logger.debug("Agent waiting - no tasks to process")
            await asyncio.sleep(0.1)  # Brief pause to prevent busy waiting
        else:
            self.logger.warning(f"Unknown action type: {action_type}")

    async def _add_task(self, task: Dict[str, Any]) -> None:
        """
        Internal method to add tasks to the queue with overflow protection.
        """
        if len(self.state["task_queue"]) >= self.state["max_queue_size"]:
            self.logger.warning(f"Task queue full ({self.state['max_queue_size']}), dropping task: {task['id']}")
            return
        
        self.state["task_queue"].append(task)
        self.logger.info(f"Task added to queue: {task['id']} - {task['description']}")

    async def _execute_task(self, task: Dict[str, Any]) -> None:
        """
        Internal method to execute a task and update performance metrics.
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Remove task from queue
            if task in self.state["task_queue"]:
                self.state["task_queue"].remove(task)
            
            self.logger.info(f"Executing task {task['id']}: {task['description']}")
            
            # Simulate task execution (replace with real logic)
            execution_time = task.get("execution_time", 1.0)  # Default 1 second
            await asyncio.sleep(execution_time)
            
            # Mark task as completed
            task["completed_at"] = asyncio.get_event_loop().time()
            task["execution_duration"] = task["completed_at"] - start_time
            task["status"] = "completed"
            
            self.state["completed_tasks"].append(task)
            
            # Update performance metrics
            self._update_performance_metrics(task, success=True)
            
            self.logger.info(f"Task {task['id']} completed successfully in {task['execution_duration']:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Task {task['id']} failed: {str(e)}")
            task["status"] = "failed"
            task["error"] = str(e)
            self.state["completed_tasks"].append(task)
            self._update_performance_metrics(task, success=False)

    def _update_performance_metrics(self, task: Dict[str, Any], success: bool) -> None:
        """
        Update agent performance statistics.
        """
        metrics = self.state["performance_metrics"]
        
        if success:
            metrics["tasks_completed"] += 1
        else:
            metrics["tasks_failed"] += 1
        
        # Update average execution time (moving average)
        if "execution_duration" in task:
            total_tasks = metrics["tasks_completed"] + metrics["tasks_failed"]
            current_avg = metrics["average_execution_time"]
            new_duration = task["execution_duration"]
            
            # Simple moving average calculation
            metrics["average_execution_time"] = (
                (current_avg * (total_tasks - 1) + new_duration) / total_tasks
            )

    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and performance summary.
        Useful for monitoring and debugging.
        """
        return {
            "agent_name": self.name,
            "queue_length": len(self.state["task_queue"]),
            "completed_tasks": len(self.state["completed_tasks"]),
            "performance_metrics": self.state["performance_metrics"],
            "queue_capacity": f"{len(self.state['task_queue'])}/{self.state['max_queue_size']}",
        }


# --- 🎓 TEACHING NOTES ---
#
# 🏗️ DESIGN PATTERNS DEMONSTRATED:
# - State Management: Using agent.state dict for task queues and metrics
# - Priority Queuing: Simple priority-based task selection
# - Error Handling: Try/catch with graceful failure logging
# - Performance Monitoring: Basic metrics collection and moving averages
# - Async Operations: Non-blocking task execution with asyncio.sleep()
#
# 🔄 AGENTIC LOOP BREAKDOWN:
# 1. PERCEIVE: Receive task (string, dict, or list)
# 2. DECIDE: Select highest priority task from queue
# 3. ACT: Execute task and update performance metrics
#
# 🚀 PRODUCTION ENHANCEMENTS:
# - Add task persistence (database, files)
# - Implement sophisticated priority algorithms
# - Add task dependencies and workflows
# - Integrate with external task queues (Celery, RQ)
# - Add resource limits and rate limiting
# - Implement task retry mechanisms
#
# 🧪 TESTING SCENARIOS:
# - Single task: await agent.run("Process this task")
# - Priority tasks: await agent.run({"description": "Urgent!", "priority": "high"})
# - Multiple tasks: await agent.run(["task1", "task2", "task3"])
# - Queue overflow: Add more tasks than max_queue_size
