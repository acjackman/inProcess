# import the really small API
# Configuration options found at https://github.com/jeffh/sniffer/
from sniffer.api import *
from subprocess import call
import os
import termstyle
# you can customize the pass/fail colors like this
pass_fg_color = termstyle.green
pass_bg_color = termstyle.bg_default
fail_fg_color = termstyle.red
fail_bg_color = termstyle.bg_default

# All lists in this variable will be under surveillance for changes.
# watch_paths = ['.', 'tests/']


@file_validator
def py_files(filename):
    """
    this gets invoked on every file that gets changed in the directory. Return
    True to invoke any runnable functions, False otherwise.

    This fires runnables only if files ending with .py extension and not prefixed
    with a period.
    """
    return filename.endswith('.py') and not os.path.basename(filename).startswith('.')


@runnable
def execute_tests(*args):
    """
    This gets invoked for verification. This is ideal for running tests of some sort.
    For anything you want to get constantly reloaded, do an import in the function.

    sys.argv[0] and any arguments passed via -x prefix will be sent to this function as
    it's arguments. The function should return logically True if the validation passed
    and logicially False if it fails.

    This example simply runs nose.
    """

    fn = ['py.test', '--cov', 'inprocess']

    args = set(args[1:])

    fn += list(args)
    return call(fn) == 0
