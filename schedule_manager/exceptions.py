"""
Custom exceptions for the schedule manager
"""


class ScheduleManagerError(Exception):
    """Base exception for schedule manager errors"""
    pass


class AgentError(ScheduleManagerError):
    """Base exception for agent-related errors"""
    pass


class AgentUnavailableError(AgentError):
    """Raised when the AI agent is not responding or unavailable"""
    pass


class AgentStartupError(AgentError):
    """Raised when the AI agent fails to start"""
    pass


class AgentShutdownError(AgentError):
    """Raised when the AI agent fails to shutdown cleanly"""
    pass


class AgentCommunicationError(AgentError):
    """Raised when communication with the AI agent fails"""
    pass
