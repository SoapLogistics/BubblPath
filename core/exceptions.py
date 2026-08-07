class SolomonError(Exception):
    """Base exception for all Solomon errors."""
    pass

class ConfigurationError(SolomonError):
    """Raised when configuration is missing or invalid."""
    pass
