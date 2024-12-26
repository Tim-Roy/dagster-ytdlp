"""Custom exceptions to provide more granular verbosity."""


class EnvVarMissingError(KeyError):
    """Raise when a specific subset of values in context of app is wrong."""

    def __init__(self, message):
        super().__init__(message)
