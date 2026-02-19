"""
Custom exception classes for AITeam application.

This module defines a hierarchy of custom exceptions that provide:
- Clear error categorization
- User-friendly error messages
- Structured error responses for API clients
"""


class AITeamException(Exception):
    """Base exception class for all AITeam errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API response."""
        result = {
            "error": self.code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


# ============================================================================
# Resource Not Found Errors
# ============================================================================

class ResourceNotFoundError(AITeamException):
    """Base class for resource not found errors."""

    def __init__(self, resource_type: str, resource_id: str, details: dict = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} with id '{resource_id}' not found"
        super().__init__(
            message=message,
            code=f"{resource_type.upper().replace(' ', '_')}_NOT_FOUND",
            details=details
        )


class PlanNotFoundError(ResourceNotFoundError):
    """Raised when a plan is not found."""

    def __init__(self, plan_id: str, details: dict = None):
        super().__init__("Plan", plan_id, details)


class TaskNotFoundError(ResourceNotFoundError):
    """Raised when a task is not found."""

    def __init__(self, task_id: str, details: dict = None):
        super().__init__("Task", task_id, details)


class AgentNotFoundError(ResourceNotFoundError):
    """Raised when an agent is not found."""

    def __init__(self, agent_id: str, details: dict = None):
        super().__init__("Agent", agent_id, details)


class ProjectNotFoundError(ResourceNotFoundError):
    """Raised when a project is not found."""

    def __init__(self, project_id: str, details: dict = None):
        super().__init__("Project", project_id, details)


# ============================================================================
# Validation Errors
# ============================================================================

class ValidationError(AITeamException):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None, details: dict = None):
        self.field = field
        code = "VALIDATION_ERROR"
        if field:
            code = f"INVALID_{field.upper().replace(' ', '_')}"
            details = details or {}
            details["field"] = field
        super().__init__(message=message, code=code, details=details)


class InvalidStatusTransitionError(ValidationError):
    """Raised when an invalid status transition is attempted."""

    def __init__(self, current_status: str, target_status: str, resource_type: str = "Resource"):
        message = f"Cannot transition {resource_type} from '{current_status}' to '{target_status}'"
        super().__init__(
            message=message,
            field="status",
            details={
                "current_status": current_status,
                "target_status": target_status,
                "resource_type": resource_type,
            }
        )


class MissingRequiredFieldError(ValidationError):
    """Raised when a required field is missing."""

    def __init__(self, field_name: str, context: str = None):
        message = f"Required field '{field_name}' is missing"
        if context:
            message = f"{message} in {context}"
        super().__init__(message=message, field=field_name)


# ============================================================================
# Execution Errors
# ============================================================================

class ExecutionError(AITeamException):
    """Raised when task/plan execution fails."""

    def __init__(self, message: str, task_id: str = None, agent_id: str = None, details: dict = None):
        self.task_id = task_id
        self.agent_id = agent_id
        details = details or {}
        if task_id:
            details["task_id"] = task_id
        if agent_id:
            details["agent_id"] = agent_id
        super().__init__(message=message, code="EXECUTION_ERROR", details=details)


class TaskTimeoutError(ExecutionError):
    """Raised when a task execution times out."""

    def __init__(self, task_id: str, timeout_seconds: int, agent_id: str = None):
        message = f"Task '{task_id}' timed out after {timeout_seconds} seconds"
        super().__init__(
            message=message,
            task_id=task_id,
            agent_id=agent_id,
            details={"timeout_seconds": timeout_seconds}
        )
        self.code = "TASK_TIMEOUT"


class TaskRetryExhaustedError(ExecutionError):
    """Raised when all retry attempts for a task have been exhausted."""

    def __init__(self, task_id: str, retry_count: int, last_error: str = None):
        message = f"Task '{task_id}' failed after {retry_count} retry attempts"
        details = {"retry_count": retry_count}
        if last_error:
            details["last_error"] = last_error
        super().__init__(message=message, task_id=task_id, details=details)
        self.code = "TASK_RETRY_EXHAUSTED"


class PipelineError(ExecutionError):
    """Raised when the pipeline execution fails."""

    def __init__(self, message: str, plan_id: str = None, phase: str = None, details: dict = None):
        details = details or {}
        if plan_id:
            details["plan_id"] = plan_id
        if phase:
            details["phase"] = phase
        super().__init__(message=message, details=details)
        self.code = "PIPELINE_ERROR"
        self.plan_id = plan_id
        self.phase = phase


# ============================================================================
# LLM Errors
# ============================================================================

class LLMError(AITeamException):
    """Raised when LLM operations fail."""

    def __init__(self, message: str, provider: str = None, model: str = None, details: dict = None):
        self.provider = provider
        self.model = model
        details = details or {}
        if provider:
            details["provider"] = provider
        if model:
            details["model"] = model
        super().__init__(message=message, code="LLM_ERROR", details=details)


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limit is exceeded."""

    def __init__(self, provider: str = None, retry_after: int = None):
        message = "LLM rate limit exceeded"
        if retry_after:
            message = f"{message}, please retry after {retry_after} seconds"
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
        super().__init__(message=message, provider=provider, details=details)
        self.code = "LLM_RATE_LIMIT"


class LLMResponseError(LLMError):
    """Raised when LLM response is invalid or cannot be parsed."""

    def __init__(self, message: str, raw_response: str = None, provider: str = None):
        details = {}
        if raw_response:
            # Truncate raw response for logging
            details["raw_response_preview"] = raw_response[:500] if len(raw_response) > 500 else raw_response
        super().__init__(message=message, provider=provider, details=details)
        self.code = "LLM_RESPONSE_ERROR"


# ============================================================================
# Configuration Errors
# ============================================================================

class ConfigurationError(AITeamException):
    """Raised when there is a configuration error."""

    def __init__(self, message: str, config_key: str = None, details: dict = None):
        self.config_key = config_key
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message=message, code="CONFIGURATION_ERROR", details=details)


class MissingConfigurationError(ConfigurationError):
    """Raised when a required configuration is missing."""

    def __init__(self, config_key: str, environment_variable: str = None):
        message = f"Required configuration '{config_key}' is missing"
        if environment_variable:
            message = f"{message}. Please set the environment variable '{environment_variable}'"
        super().__init__(message=message, config_key=config_key)


# ============================================================================
# Storage Errors
# ============================================================================

class StorageError(AITeamException):
    """Raised when storage operations fail."""

    def __init__(self, message: str, operation: str = None, path: str = None, details: dict = None):
        details = details or {}
        if operation:
            details["operation"] = operation
        if path:
            details["path"] = path
        super().__init__(message=message, code="STORAGE_ERROR", details=details)


class FileSaveError(StorageError):
    """Raised when file save operation fails."""

    def __init__(self, path: str, reason: str = None):
        message = f"Failed to save file to '{path}'"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message=message, operation="save", path=path)


class FileReadError(StorageError):
    """Raised when file read operation fails."""

    def __init__(self, path: str, reason: str = None):
        message = f"Failed to read file from '{path}'"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message=message, operation="read", path=path)


# ============================================================================
# WebSocket Errors
# ============================================================================

class WebSocketError(AITeamException):
    """Raised when WebSocket operations fail."""

    def __init__(self, message: str, client_id: str = None, details: dict = None):
        details = details or {}
        if client_id:
            details["client_id"] = client_id
        super().__init__(message=message, code="WEBSOCKET_ERROR", details=details)


class ConnectionError(WebSocketError):
    """Raised when WebSocket connection fails."""

    def __init__(self, reason: str = None, client_id: str = None):
        message = "WebSocket connection failed"
        if reason:
            message = f"{message}: {reason}"
        super().__init__(message=message, client_id=client_id)
        self.code = "WEBSOCKET_CONNECTION_ERROR"


class BroadcastError(WebSocketError):
    """Raised when WebSocket broadcast fails."""

    def __init__(self, message_type: str = None, reason: str = None):
        message = "Failed to broadcast message"
        if message_type:
            message = f"{message} of type '{message_type}'"
        if reason:
            message = f"{message}: {reason}"
        details = {}
        if message_type:
            details["message_type"] = message_type
        super().__init__(message=message, details=details)
        self.code = "WEBSOCKET_BROADCAST_ERROR"
