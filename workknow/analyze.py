"""Analyze a data frame to answer research questions and return a data frame."""

from pathlib import Path

import pluginbase  # type: ignore
from pluginbase import PluginBase

from workknow import constants
from workknow import files

PLUGIN_SOURCE = None

DEFAULT_FUNCTIONS = [
    constants.plugins.Function_Analyze,
]


def get_source(plugin_path: Path) -> pluginbase.PluginSource:
    """Load all of the plugins using pluginbase."""
    # define the "package" in which the plugins reside
    # the term "package" corresponds to "module.sub-module"
    plugin_base = PluginBase(package=constants.plugins.Plugins)
    # remove any directories from the path listings that are Nothing (i.e., "")
    # this case occurs when the optional --plugindir is not provided on command-line
    # Create the directory where the internal plugins live inside of GatorGrader.
    # Note that this directory includes the home for GatorGrader, which can be set
    # by an environment variable and otherwise defaults to the directory from which
    # GatorGrader was run and then the directory where internal plugins are stored.
    internal_plugin_path = files.create_path(
        constants.plugins.Internal_Plugins_Dir, home=constants.plugins.Home
    )
    # create the listing of the paths that could contain plugins, including
    # all of the provided paths for external plugins and the directory that
    # contains all of the internal plugins provided by GatorGrader
    if files.confirm_valid_directory(plugin_path):
        all_plugin_paths = [str(plugin_path), str(internal_plugin_path)]
    else:
        all_plugin_paths = [str(internal_plugin_path)]
    # Create and return a source of plugins using PluginBase.
    # The documentation for this function advices that you
    # give an identifier to the source for the plugins
    # because this will support saving and transfer, if needed.
    # Only perform this operation if the plugin source is None,
    # meaning that it has not already been initialized.
    # pylint: disable=global-statement
    global PLUGIN_SOURCE
    if PLUGIN_SOURCE is None:
        PLUGIN_SOURCE = plugin_base.make_plugin_source(
            identifier=constants.plugins.Plugin_Base_Identifier,
            searchpath=all_plugin_paths,
        )
    return PLUGIN_SOURCE


def transform_plugin_name(plugin_name: str) -> str:
    """Transform the chosen plugin from the provided command-line arguments."""
    # add "plugin" to the name of the plugin so that it looks like, for instance,
    # "plugin_" when "CountCommits" is chosen on command-line
    transformed_plugin = constants.plugins.Plugin_Prefix + plugin_name
    return transformed_plugin


def verify_plugin_existence(
    plugin: str, plugin_source: pluginbase.PluginSource
) -> bool:
    """Verify that the requested plugin is available from the source(s)."""
    plugin_exists = False
    # list each of the plugins by name as they are available in the
    # --> internal source that comes with GatorGrader
    # --> the external source specified by user on the command-line
    plugin_list = plugin_source.list_plugins()
    # if the name of the plugin is in the list of plugins
    # then we can confirm its existence, signalling its use is acceptable
    if plugin in plugin_list:
        plugin_exists = True
    return plugin_exists


def verify_plugin_function(plugin, function):
    """Verify that the requested plugin has a function."""
    # the specified plugin, a module loaded by pluginbase, has the specified function
    if hasattr(plugin, function):
        return True
    # the specified plugin does not have the function, so do not verify it
    return False


def verify_plugin_functions(plugin, functions=DEFAULT_FUNCTIONS):
    """Verify that the requested plugin has the required function(s)."""
    # perform verification on the specified plugin, a module loaded by pluginbase,
    # for all of the provided functions, which are, DEFAULT_FUNCTIONS by default
    verify_status_results = [
        verify_plugin_function(plugin, function) for function in functions
    ]
    # verify the status of the plugin as long as all values in verify_status_results are True
    return all(verify_status_results)
