"""
Base Agent class that all agents inherit from.
Provides common logging, state management, and event tracking.
"""

import logging
import time
from datetime import datetime


class AgentEvent:
    """Represents an event logged by an agent."""

    def __init__(self, agent_name, event_type, message, data=None):
        self.timestamp = datetime.now().isoformat()
        self.agent_name = agent_name
        self.event_type = event_type
        self.message = message
        self.data = data or {}

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "agent": self.agent_name,
            "type": self.event_type,
            "message": self.message,
            "data": self.data,
        }


class BaseAgent:
    """
    Base class for all agents in the system.
    Provides logging, event tracking, and state management.
    """

    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.events = []
        self._start_time = None

    def log_event(self, event_type, message, data=None):
        """Record an event and log it."""
        event = AgentEvent(self.name, event_type, message, data)
        self.events.append(event)
        self.logger.info("[%s] %s: %s", event_type.upper(), self.name, message)
        return event

    def start_timer(self):
        self._start_time = time.time()

    def elapsed_seconds(self):
        if self._start_time is None:
            return 0
        return round(time.time() - self._start_time, 2)

    def get_events(self):
        return [e.to_dict() for e in self.events]

    def clear_events(self):
        self.events.clear()
