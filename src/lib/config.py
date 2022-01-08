#####################
# Dennis MUD        #
# config.py         #
# Copyright 2020    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

# This code adapted from Driftwood 2D Game Dev. Suite,
# Copyright 2014-2017 Michael D. Reiley and Paul Merrill.
# https://github.com/Driftwood2D/Driftwood

import json
import os
import sys

from lib.contrib_micropython_lib import traceback

from lib.logger import timestamp

VERSION = "Dennis MUD v0.0.3-Alpha"
COPYRIGHT = "Copyright 2018-2020 Michael D. Reiley"


class ConfigManager:
    """The Config Manager

    This class reads command line input and a configuration file and presents the resulting configuration for easy
    access. Command line options always supersede their configuration file equivalents.
    
    :ivar config: The internal dictionary of all config values. Base keys are "defaults", "server", and "singleuser".
    :ivar defaults: A convenience class instance providing protected access to just the defaults config values.
    :ivar vars: A convenience class instance providing protected access to special command-line-only variables.
    """

    def __init__(self, single):
        """ConfigManager class initializer.

        :param single: Whether or not to run in single user mode.
        """
        # This is a ConfigBaseKey pseudo-dictionary of server or singleuser config values.
        self.config = ConfigBaseKey()

        # This is a ConfigBaseKey pseudo-dictionary of defaults config values.
        self.defaults = None

        # Here we allow special command-line-only config variables.
        # They are passed on the command line in Quake style: +varname=value
        self.vars = ConfigBaseKey()

        # This is empty at the start when the Logger hasn't been initialized yet.
        self._log = None

        # Run initialization steps. It's ok to do an unclean sys.exit() during these because
        # we are just starting up the engine.
        self._single = single
        self._prepare_config()

    def __contains__(self, item):
        if item in self.config:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.config[item]
        else:
            # Config variables should never be null, so this works as an unambiguous error code.
            return None

    def __setitem__(self, key, value):
        self.config[key] = value

    def __iter__(self):
        return iter(self.config.__iter__())

    def _prepare_config(self):
        """Prepare the configuration for use.
        """
        # Load the defaults configuration file, otherwise fail.
        try:
            with open("defaults.config.json") as defaultsfile:
                self.defaults = ConfigBaseKey(json.load(defaultsfile))
                self.config["defaults"] = self.defaults
        except (OSError, IOError):
            print("{0} [config#critical] Could not open defaults config file: {1}".format(
                timestamp(), self._cmdline_args.defaultsfile[0]))
            print(traceback.format_exc(1))
            sys.exit(2)
        except json.JSONDecodeError:
            print("{0} [config#critical] JSON error from defaults config file: {1}".format(
                timestamp(), self._cmdline_args.defaultsfile[0]))
            print(traceback.format_exc(1))
            sys.exit(2)

        # If single user mode, load the singleuser configuration file, otherwise fail.
        if self._single:
            try:
                with open("singleuser.config.json", 'r') as singleuserfile:
                    self.config = ConfigBaseKey(json.load(singleuserfile))
            except (OSError, IOError):
                print("{0} [config#critical] Could not open singleuser config file: {1}".format(
                    timestamp(), self._cmdline_args.singleuserfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)
            except json.JSONDecodeError:
                print("{0} [config#critical] JSON error from singleuser config file: {1}".format(
                    timestamp(), self._cmdline_args.singleuserfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)

        # If server mode, load the server configuration file, otherwise fail.
        else:
            try:
                with open("server.config.json", 'r') as serverfile:
                    self.config = ConfigBaseKey(json.load(serverfile))
            except (OSError, IOError):
                print("{0} [config#critical] Could not open server config file: {1}".format(
                    timestamp(), self._cmdline_args.serverfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)
            except json.JSONDecodeError:
                print("{0} [config#critical] JSON error from server config file: {1}".format(
                    timestamp(), self._cmdline_args.serverfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)


class ConfigBaseKey:
    """This is a convenience class for providing protected access to just a section of the config.

    It behaves almost exactly like a dictionary, so you can basically treat it like one.
    The major difference is that it won't crash if you try to pull a nonexistent key.
    """
    def __init__(self, document=None):
        if document is None:
            self.config = {}
        else:
            self.config = document

    def __contains__(self, item):
        if item in self.config:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.config[item]
        else:
            return None

    def __setitem__(self, key, value):
        self.config[key] = value

    def __iter__(self):
        return iter(self.config.keys())

