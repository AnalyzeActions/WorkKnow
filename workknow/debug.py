"""Manage debugging levels."""

from enum import Enum

from workknow import constants


class DebugLevel(str, Enum):
    """The predefined levels for debugging."""

    DEBUG = constants.logging.Debug
    INFO = constants.logging.Info
    WARNING = constants.logging.Warning
    ERROR = constants.logging.Error
    CRITICAL = constants.logging.Critical
