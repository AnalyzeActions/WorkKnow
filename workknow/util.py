"""Utility functions for WorkKnow."""


def human_readable_boolean(answer: bool) -> str:
    """Produce a human-readable Yes or No for a boolean value of True or False."""
    if answer:
        return "Yes"
    return "No"
