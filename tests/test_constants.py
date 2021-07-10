"""Tests for the constants module."""

import pytest

from workknow import constants

CANNOT_SET_CONSTANT_VARIABLE = "cannot_set_constant_variable"


def test_logging_constant_defined():
    """Check correctness for the variables in the logging constant."""
    assert constants.logging.Debug == "DEBUG"
    assert constants.logging.Info == "INFO"
    assert constants.logging.Warning == "WARNING"
    assert constants.logging.Error == "ERROR"
    assert constants.logging.Critical == "CRITICAL"
    assert constants.logging.Default_Logging_Level == "ERROR"
    assert constants.logging.Format == "%(message)s"
    assert constants.logging.Rich == "Rich"


def test_logging_constant_cannot_redefine():
    """Check cannot redefine the variables in the logging constant."""
    with pytest.raises(AttributeError):
        constants.logging.Debug = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Info = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Warning = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Error = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Critical = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Critical = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Default_Logging_Level = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Format = CANNOT_SET_CONSTANT_VARIABLE
    with pytest.raises(AttributeError):
        constants.logging.Rich = CANNOT_SET_CONSTANT_VARIABLE
