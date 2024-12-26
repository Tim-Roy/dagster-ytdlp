from __future__ import annotations

from os import environ

from .exceptions import EnvVarMissingError


def get_env_var(env_var: str, assigned_var: str):
    """Load env variable, return error if not present."""
    var = environ.get(env_var, None)
    if var is None:
        raise EnvVarMissingError(
            f"If '{assigned_var}' is left as None, the environment variable '{env_var}' must exist"
        )
    return var
