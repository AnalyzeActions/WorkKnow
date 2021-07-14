"""Display messages in the terminal window."""

from workknow import configure
from workknow import constants
from workknow import debug


def display_tool_details(
    debug_level: debug.DebugLevel = debug.DebugLevel.ERROR,
):
    """Display the details about the tool."""
    # setup the console and the logger and then create a blank line for space
    console, _ = configure.setup(debug_level)
    # display the messages about the tool
    console.print()
    # --> display the tagline for the tool
    console.print(
        constants.workknow.Emoji + constants.markers.Space + constants.workknow.Tagline
    )
    # --> display the web site for the tool
    console.print(constants.workknow.Website)
    console.print()
