from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger
from datetime import datetime
import uuid


class BaseAgent(ABC):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logger
        self.execution_history = []

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def log_execution(self, input_data: Dict[str, Any], output_data: Dict[str, Any], status: str = "success", error: Optional[str] = None):
        execution_record = {
            "execution_id": str(uuid.uuid4()),
            "agent_name": self.agent_name,
            "input_data": input_data,
            "output_data": output_data,
            "status": status,
            "error_message": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.execution_history.append(execution_record)
        self.logger.info(f"Agent {self.agent_name} execution logged: {execution_record['execution_id']}")
        return execution_record

    def validate_input(self, input_data: Dict[str, Any], required_keys: list) -> bool:
        for key in required_keys:
            if key not in input_data:
                self.logger.error(f"Missing required key: {key}")
                return False
        return True
